# Py-tldr

[![test](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/iamgodot/py-tldr/actions/workflows/test.yml)
[![release](https://github.com/iamgodot/py-tldr/actions/workflows/release.yml/badge.svg)](https://github.com/iamgodot/py-tldr/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

New Python client for tldr pages

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

python3.6+

## Changelog

[Here](docs/CHANGELOG.md)

## License

[MIT](docs/LICENSE)

## Credits

This package was created with [cookiecutter](https://github.com/audreyr/cookiecutter) and [iamgodot/gen-pyckage](https://github.com/iamgodot/gen-pyckage) project template.
