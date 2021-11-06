# Py-tldr

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![test](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml)

Py-tldr is a new Python client for tldr pages based on [Click](https://github.com/pallets/click).

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

## Support

Python: 3.6, 3.7, 3.8, 3.9

OS: Not fully tested on Windows so there's uncertainty with color rendering.

## Changelog

See [CHANGELOG](docs/CHANGELOG.md)

## License

[MIT](docs/LICENSE)

## Credits

This package was created with [cookiecutter](https://github.com/audreyr/cookiecutter) and [iamgodot/gen-pyckage](https://github.com/iamgodot/gen-pyckage) project template.
