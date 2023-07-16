import subprocess
import sys
from copy import deepcopy
from functools import partial
from os import environ
from pathlib import Path as LibPath

import toml
from click import Choice, argument, option, pass_context, secho
from click import command as command_
from yaspin import yaspin
from yaspin.spinners import Spinners

from .page import DownloadError, PageFinder, PageFormatter
from .parse import parse_command, parse_language, parse_platform

try:
    from importlib.metadata import version

    VERSION_CLI = version("py_tldr")
except ModuleNotFoundError:
    try:
        from pkg_resources import get_distribution

        VERSION_CLI = get_distribution("py_tldr").version
    except ModuleNotFoundError:
        VERSION_CLI = ""

VERSION_CLIENT_SPEC = "1.5"
DEFAULT_CACHE_HOURS = 24
DEFAULT_CONFIG = {
    "page_source": "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages",
    "language": "",
    "platform": "",
    "cache": {
        "enabled": True,
        "timeout": DEFAULT_CACHE_HOURS,
        "download_url": "https://tldr.sh/assets/tldr.zip",
    },
    "proxy_url": "",
}
DEFAULT_CONFIG_EDITOR = "vi"
DEFAULT_CONFIG_DIR = LibPath.home() / ".config" / "tldr"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_CACHE_DIR = LibPath.home() / ".cache" / "tldr"

DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

info = partial(secho, bold=True, fg="green")
warn = partial(secho, bold=True, fg="yellow")


def print_version(ctx, param, value):  # pylint: disable=unused-argument
    if not value or ctx.resilient_parsing:
        return
    info(f"tldr version {VERSION_CLI}")
    info(f"client specification version {VERSION_CLIENT_SPEC}")
    ctx.exit()


def edit_config(ctx, param, value):  # pylint: disable=unused-argument
    """Create config file if not existed, then open in editor."""
    if not value or ctx.resilient_parsing:
        return
    config = DEFAULT_CONFIG
    config_file = DEFAULT_CONFIG_FILE
    if not config_file.exists():
        warn("No config file found, creating...")
        with open(config_file, "w", encoding="utf8") as f:
            toml.dump(config, f)
        info(f"Default config file created: {config_file}")
    editor = environ.get("EDITOR", DEFAULT_CONFIG_EDITOR)
    subprocess.call([editor, config_file])
    ctx.exit()


def setup_config():  # pylint: disable=unused-argument
    """Build a config dict from config file on top of default settings.

    Note `toml` should used as file format.
    Raises:
      SystemExit: if merged config checking failed.
    """
    config = deepcopy(DEFAULT_CONFIG)
    config_file = DEFAULT_CONFIG_FILE
    if config_file.exists():
        warn(f"Found config file: {config_file}")
        with open(config_file, encoding="utf8") as f:
            config.update(toml.load(f))
    cache = config.get("cache")
    if not config.get("page_source") or not cache or not cache.get("download_url"):
        warn(f"Page source and cache are required in config file: {config_file}")
        sys.exit(1)
    return config


@command_(context_settings={"help_option_names": ["-h", "--help"]})
@option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    is_eager=True,
    expose_value=False,
    help="Show version info and exit.",
)
@option(
    "--edit-config",
    is_flag=True,
    callback=edit_config,
    is_eager=True,
    expose_value=False,
    help="Open config file with an editor.",
)
@option(
    "-p",
    "--platform",
    type=Choice(["android", "linux", "macos", "osx", "sunos", "windows"]),
    default="linux",
    help="Specify searching platform(macos as an alias of osx).",
)
@option(
    "-L",
    "--language",
    default="en",
    help="Specify searching language(with no fallbacks), e.g. `en`.",
)
@option("-u", "--update", is_flag=True, help="Update local cache with all pages.")
@argument("command", nargs=-1)
@pass_context
def cli(ctx, command, platform, language, update):
    """Collaborative cheatsheets for console commands.

    For subcommands such as `git commit`, just keep as it is:

        tldr git commit
    """
    config = setup_config()
    page_finder = make_page_finder(config)

    languages = parse_language(language, config)
    if update:
        with yaspin(Spinners.arc, text="Downloading pages...") as sp:
            try:
                page_finder.sync(languages[0])
            except DownloadError:
                sp.write("> Sync failed, check your network and try again.")
                sys.exit(1)
            sp.write("> Download complete.")
        info("All caches updated.")

    if not command:
        if not update:
            secho(ctx.get_help())
        return

    command = parse_command(command)
    platform = parse_platform(platform, config)
    content = None
    with yaspin(Spinners.arc, text="Searching pages...") as sp:
        try:
            content = page_finder.find(command, platform, languages=languages)
        except DownloadError:
            sp.write("> Search failed, check your network and try again.")
            sys.exit(1)
        if content:
            sp.write("> Page found.")
        else:
            sp.write("> No result.")

    if content:
        print(PageFormatter(indent_spaces=4, start_with_new_line=True).format(content))
    else:
        warn("There is no available pages right now.")
        warn("You can create an issue via https://github.com/tldr-pages/tldr/issues.")
        sys.exit(1)


def make_page_finder(config=None) -> PageFinder:
    if not config:
        config = DEFAULT_CONFIG
    source_url = config["page_source"]
    cache_config = config["cache"]
    cache_timeout = cache_config.get("timeout", DEFAULT_CACHE_HOURS)
    cache_location = DEFAULT_CACHE_DIR
    cache_download_url = cache_config["download_url"]
    cache_enabled = cache_config.get("enabled", True)
    proxy_url = config["proxy_url"]
    return PageFinder(
        source_url,
        cache_timeout,
        cache_location,
        cache_download_url,
        cache_enabled,
        proxy_url,
    )
