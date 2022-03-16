import platform as platform_
import sys
from functools import partial
from pathlib import Path as LibPath

import toml
from click import Choice, Path, argument
from click import command as command_
from click import get_app_dir, option, pass_context, secho
from yaspin import yaspin
from yaspin.spinners import Spinners

from .page import PageCache, PageFinder, PageFormatter

try:
    from importlib.metadata import version

    VERSION_CLI = version("py_tldr")
except ModuleNotFoundError:
    from pkg_resources import get_distribution

    VERSION_CLI = get_distribution("py_tldr").version

VERSION_CLIENT_SPEC = "1.5"
DEFAULT_CONFIG = {
    "page_source": "https://raw.githubusercontent.com/tldr-pages/tldr/master/pages",
    "language": "",
    "cache": {
        "enabled": True,
        "timeout": 24,
        "download_url": "https://tldr-pages.github.io/assets/tldr.zip",
    },
    "proxy_url": "",
}
DEFAULT_CONFIG_DIR = LibPath(get_app_dir("tldr"))
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_CACHE_DIR = LibPath.home() / ".cache" / "tldr"

info = partial(secho, bold=True, fg="green")
warn = partial(secho, bold=True, fg="yellow")


def print_version(ctx, param, value):  # pylint: disable=unused-argument
    if not value or ctx.resilient_parsing:
        return
    info(f"tldr version {VERSION_CLI}")
    info(f"client specification version {VERSION_CLIENT_SPEC}")
    ctx.exit()


def setup_config(ctx, param, value):  # pylint: disable=unused-argument
    """Build a config dict from either default or custom path.

    Currently custom config file is used without validation, so
    misconfiguration may cause errors. Also note `toml` should
    used as file format.
    """
    config = {}

    if not value or ctx.resilient_parsing:
        config_dir = DEFAULT_CONFIG_DIR
        config_file = DEFAULT_CONFIG_FILE

        if not config_file.exists():
            warn("No config file found, setting it up...")
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, "w", encoding="utf8") as f:
                toml.dump(DEFAULT_CONFIG, f)
            warn(f"Config file created: {config_file}")
            config = DEFAULT_CONFIG
    else:
        config_file = value
        warn(f"Using config file from {config_file}")

    if not config:
        with open(config_file, encoding="utf8") as f:
            config = toml.load(f)
    return config


def guess_os():
    system_to_platform = {
        "Linux": "linux",
        "Darwin": "osx",
        "Java": "sunos",
        "Windows": "windows",
    }
    return system_to_platform.get(platform_.system(), "linux")


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
    "--config",
    type=Path(exists=True, dir_okay=False, path_type=LibPath),
    callback=setup_config,
    help="Specify a config file to use.",
)
@option(
    "-p",
    "--platform",
    type=Choice(["android", "common", "linux", "osx", "sunos", "windows"]),
    help="Override current operating system.",
)
@option("-u", "--update", is_flag=True, help="Update local cache with all pages.")
@argument("command", nargs=-1)
@pass_context
def cli(ctx, config, command, platform, update):
    """Collaborative cheatsheets for console commands.

    For subcommands such as `git commit`, just keep as it is:

        tldr git commit
    """
    page_cache = PageCache(
        timeout=config["cache"]["timeout"],
        location_base=DEFAULT_CACHE_DIR,
        download_url=config["cache"]["download_url"],
        proxy_url=config["proxy_url"],
    )
    if update:
        with yaspin(Spinners.arc, text="Downloading pages...") as sp:
            page_cache.update()
            sp.write("> Download complete.")
        info("All caches updated.")

    if not command:
        if not update:
            secho(ctx.get_help())
        return
    else:
        command = "-".join(command)

    config["platform"] = platform or guess_os()
    page_finder = PageFinder(
        source_url=config["page_source"],
        platform=config["platform"],
        language=config["language"],
        proxy_url=config["proxy_url"],
    )
    page_content = None
    if config["cache"]["enabled"]:
        page_content = page_cache.get(command, config["platform"])
    if not page_content:
        with yaspin(Spinners.arc, text="Searching pages...") as sp:
            result = page_finder.find(command)
            if result:
                sp.write("> Page found.")
            else:
                sp.write("> No result.")
        if result:
            page_cache.set(**result)
        page_content = result.get("content")

    if page_content:
        print(
            PageFormatter(indent_spaces=4, start_with_new_line=True).format(
                page_content
            )
        )
    else:
        warn("There is no available pages right now.")
        warn("You can create an issue via https://github.com/tldr-pages/tldr/issues.")
        sys.exit(1)
