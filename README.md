# Py-tldr

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![test](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml)

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
  --config FILE                   Specify a config file to use.
  -p, --platform [android|common|linux|osx|sunos|windows]
                                  Override current operating system.
  -u, --update                    Update local cache with all pages.
  -h, --help                      Show this message and exit.
```

By default a config file will be generated in `~/.config/tldr`:

```toml
page_source = "https://raw.githubusercontent.com/tldr-pages/tldr/master/pages"
language = "en"
proxy_url = ""

[cache]
enabled = true
timeout = 24
download_url = "https://tldr-pages.github.io/assets/tldr.zip"
```

Cache is enabled implicitly, with 24 hours as expiration time.

A proxy url can be set for convenience, proxy envs such as HTTP_PROXY will also work.

## Support

Python: 3.6, 3.7, 3.8, 3.9

OS: Not fully tested on Windows so there's uncertainty with color rendering.

## Changelog

See [CHANGELOG](docs/CHANGELOG.md)

## License

[MIT](docs/LICENSE)

## Credits

This package was created with [cookiecutter](https://github.com/audreyr/cookiecutter) and [iamgodot/gen-pyckage](https://github.com/iamgodot/gen-pyckage) project template.
