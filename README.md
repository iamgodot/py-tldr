# Py-tldr

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![test](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml)

Py-tldr is a new Python client for [tldr pages](https://github.com/tldr-pages/tldr) based on [Click](https://github.com/pallets/click).

![](images/demo.gif)

## Installation

```bash
pip install py-tldr
```

## Usage

```
$ tldr --help

Usage: tldr [OPTIONS] [COMMAND]...

  Collaborative cheatsheets for console commands.

  For subcommands such as `git commit`, just keep as it is:

      tldr git commit

Options:
  -v, --version                   Show version info and exit.
  --edit-config                   Open config file with an editor.
  -p, --platform [android|common|linux|osx|sunos|windows]
                                  Override current operating system.
  -L, --language TEXT             Specify language of the page(with no
                                  fallbacks), e.g. `en`.
  -u, --update                    Update local cache with all pages.
  -h, --help                      Show this message and exit.
```

Config file should be located as `~/.config/tldr/config.toml`, you can use `--edit-config` to create a default one, which will contain the following content:

```toml
page_source = "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages"
language = "en"
platform = 'linux'
proxy_url = ""

[cache]
enabled = true
timeout = 24
download_url = "https://tldr.sh/assets/tldr.zip"
```

Cache is enabled implicitly, with 24 hours as expiration time by default.

A proxy url can be set for convenience, proxy envs such as `HTTP_PROXY` will also work.

## Support

Python: 3.7, 3.8, 3.9

OS: Not tested on Windows.

## Changelog

See [CHANGELOG](docs/CHANGELOG.md)

## License

[MIT](docs/LICENSE)

## Credits

This package was created with [cookiecutter](https://github.com/audreyr/cookiecutter) and [iamgodot/create-python-app](https://github.com/iamgodot/create-python-app) project template.
