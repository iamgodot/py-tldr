import platform as platform_
import sys
from datetime import datetime
from pathlib import Path as LibPath
from zipfile import ZipFile

import requests
import toml
from click import (Choice, Path, argument, command, get_app_dir, option,
                   pass_context, secho)
from requests.exceptions import ConnectionError, HTTPError, Timeout
from rich import print as print_rich
from rich.console import Console
from rich.markdown import Markdown

from .__version__ import VERSION_CLI, VERSION_CLIENT_SPEC

DEFAULT_CONFIG = {
    'page_source':
    'https://raw.githubusercontent.com/tldr-pages/tldr/master/pages',
    'language': '',
    'cache': {
        'enabled': True,
        'timeout': 24,
        'download_url': 'https://tldr-pages.github.io/assets/tldr.zip'
    },
    'proxy_url': '',
}
DEFAULT_CONFIG_DIR = LibPath(get_app_dir('tldr'))
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / 'config.toml'
DEFAULT_CACHE_DIR = LibPath.home() / '.cache' / 'tldr'


class PageCache:
    '''PageCache intends to manage local cache data.

    It provides instant search among downloaded page files, while
    should not have direct interactions with PageFinder.

    Attributes:
        timeout: Number of hours to indicate TTL for cache data.
          Use integer for better understanding, but could be a decimal.
    '''
    def __init__(self,
                 timeout: int,
                 location_base: LibPath,
                 download_url: str,
                 proxy_url: str = None):
        self.timeout = timeout
        self.location_base = location_base
        self.location = self.location_base / 'pages'
        self.download_url = download_url
        self.proxy_url = proxy_url

    def _make_page_file(self, folder: str, name: str) -> LibPath:
        return self.location / folder / (name + '.md')

    def _validate_page_file(self, page_file: LibPath) -> bool:
        if page_file.exists():
            mtime_ts = page_file.lstat().st_mtime
            age = (datetime.now() -
                   datetime.fromtimestamp(mtime_ts)).total_seconds() / 3600
            return age <= self.timeout

        return False

    def get(self, name: str, platform: str) -> str:
        for platform in ['common', platform]:
            page_file = self._make_page_file(platform, name)
            if self._validate_page_file(page_file):
                with open(page_file) as f:
                    return f.read()

    def set(self, name: str, platform: str, content: str):
        (self.location / platform).mkdir(parents=True, exist_ok=True)
        page_file = self._make_page_file(platform, name)
        with open(page_file, 'w') as f:
            f.write(content)

    def update(self):
        '''Download all latest pages.'''
        tldr_zip = self.location_base / 'tldr.zip'
        try:
            with open(tldr_zip, 'wb') as f:
                resp = requests.get(self.download_url,
                                    proxies={'https': self.proxy_url},
                                    timeout=3)
                resp.raise_for_status()
                f.write(resp.content)
        except (ConnectionError, HTTPError, Timeout):
            # FIXME: Do something useful
            return

        with ZipFile(tldr_zip, 'r') as f:
            f.extractall(self.location_base)

        # Remove unnecessary files, like tldr.zip / index.json / LICENSE.md
        tldr_zip.unlink()
        for item in self.location_base.iterdir():
            if item.is_file():
                item.unlink()


class PageFinder:
    '''PageFinder is to locate specific entries among tldr pages.

    It tries its best to find a corresponding page answer while is
    retricted to the given language and platform. This means it will
    not change towards other scopes (except `common`) in order to
    find a match.

    Attributes:
        source_url: Indicate where tldr pages are located.
        platform: `common` will be used together with this since tldr
          merges shared entries under it.
    '''
    def __init__(self,
                 source_url: str,
                 platform: str,
                 language: str = '',
                 proxy_url: str = None):
        self.language = '' if language == 'en' else language
        self.source_url = '.'.join([source_url, self.language]).strip('.')
        self.platform = platform
        self.proxy_url = proxy_url

    def _make_page_url(self, name: str, platform: str) -> str:
        return '/'.join([self.source_url, platform, name + '.md'])

    def _query(self, url: str) -> str:
        proxies = {'https': self.proxy_url}
        result = ''
        try:
            resp = requests.get(url, proxies=proxies, timeout=3)
            resp.raise_for_status()
            result = resp.text
        except (ConnectionError, HTTPError, Timeout):
            # FIXME: Do something useful
            pass
        finally:
            return result

    def find(self, name: str) -> dict:
        result = self._query(self._make_page_url(name, 'common'))
        for platform in ['common', self.platform]:
            result = self._query(self._make_page_url(name, platform))
            if result:
                return {'name': name, 'content': result, 'platform': platform}

        return {}


class Formatter:
    '''Formatter decides how pages (or other prompts) are displayed.

    Now Formatter simply wraps `rich` utilities for markdown rendering,
    which is likely to change for better output. Also styling params
    will be exposed in the future.
    '''
    def __init__(self, content, style=None):
        self.content_orig = content
        self.content = self.content_orig.replace('{{', '').replace('}}', '')
        self.style = style

    def output_markdown(self):
        console = Console()
        # FIXME: Syntax highlighting for inline code
        md = Markdown(self.content,
                      code_theme='',
                      inline_code_lexer='console',
                      inline_code_theme='monokai')
        console.print(md, style=self.style)
        # FIXME: Find a better way for end line gap
        console.print()

    @classmethod
    def output(cls, content, category=None, style=None):
        formatter = cls(content, style=style)
        if category == 'markdown':
            formatter.output_markdown()
        else:
            print_rich(formatter.content)


def guess_os():
    system_to_platform = {
        'Linux': 'linux',
        'Darwin': 'osx',
        'Java': 'sunos',
        'Windows': 'windows'
    }
    return system_to_platform.get(platform_.system(), 'linux')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    Formatter.output(f'tldr version {VERSION_CLI}')
    Formatter.output(f'client specification version {VERSION_CLIENT_SPEC}')
    ctx.exit()


def setup_config(ctx, param, value):
    '''Build a config dict from either default or custom path.

    Currently custom config file is used without validation, so
    misconfiguration may cause errors. Also note `toml` should
    used as file format.
    '''
    config = {}

    if not value or ctx.resilient_parsing:
        config_dir = DEFAULT_CONFIG_DIR
        config_file = DEFAULT_CONFIG_FILE

        if not config_file.exists():
            secho('No config file found, setting it up...', fg='yellow')
            config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                toml.dump(DEFAULT_CONFIG, f)
            secho(f'Config file created: {config_file}', fg='yellow')
            config = DEFAULT_CONFIG
    else:
        config_file = value
        secho(f'Using config file from {config_file}', fg='yellow')

    if not config:
        with open(config_file) as f:
            config = toml.load(f)

    return config


@command(context_settings={'help_option_names': ['-h', '--help']})
@option('-v',
        '--version',
        is_flag=True,
        callback=print_version,
        is_eager=True,
        expose_value=False,
        help='Show version info and exit.')
@option('--config',
        type=Path(exists=True, dir_okay=False, path_type=LibPath),
        callback=setup_config,
        help='Specify a config file to use.')
@option('-p',
        '--platform',
        type=Choice(['android', 'common', 'linux', 'osx', 'sunos', 'windows']),
        help='Override current operating system.')
@option('-u',
        '--update',
        is_flag=True,
        help='Update local cache with all pages.')
@argument('command', nargs=-1)
@pass_context
def cli(ctx, config, command, platform, update):
    '''Collaborative cheatsheets for console commands.

       For subcommands such as `git commit`, just keep as it is:

           tldr git commit
    '''
    page_cache = PageCache(timeout=config['cache']['timeout'],
                           location_base=DEFAULT_CACHE_DIR,
                           download_url=config['cache']['download_url'],
                           proxy_url=config['proxy_url'])
    if update:
        page_cache.update()
        secho('Finish cache update.', fg='green', bold=True)

    if not command:
        if not update:
            secho(ctx.get_help())
        return
    else:
        command = '-'.join(command)

    config['platform'] = platform or guess_os()
    page_finder = PageFinder(source_url=config['page_source'],
                             platform=config['platform'],
                             language=config['language'],
                             proxy_url=config['proxy_url'])
    page_content = None
    if config['cache']['enabled']:
        page_content = page_cache.get(command, config['platform'])
    if not page_content:
        result = page_finder.find(command)
        if result:
            page_cache.set(**result)
        page_content = result.get('content')

    if page_content:
        Formatter.output(page_content, category='markdown')
    else:
        Formatter.output('There is no available pages right now.')
        Formatter.output(
            'Create an issue here: https://github.com/tldr-pages/tldr/issues')
        sys.exit(1)
