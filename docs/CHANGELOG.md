# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.4] - 2023-02-06
### Changed
- Use `setuptools` as build backend.
- Fix version issues.

## [0.6.3] - 2023-02-06
### Changed
- Migrate from `setup.cfg` to `pyproject.toml`.
- Use `pdm` as dependency management tool.
### Removed
- Remove support for Python3.6.

## [0.6.2] - 2022-05-03
### Changed
- Fix page finding with multiple languages.

## [0.6.1] - 2022-05-02
### Changed
- Update description in README.md.

## [0.6.0] - 2022-05-02
### Added
- Add `language` option for cli.

## [0.5.3] - 2022-05-02
### Added
- Config validation.
### Changed
- Fix page matching logic.

## [0.5.2] - 2022-03-28
### Removed
- `DEBUG` env for exception hook.

## [0.5.1] - 2022-03-28
### Changed
- Fix 404 response boolean evaluation.
- Rename `build` as `rebuild` in Makefile.

## [0.5.0] - 2022-03-28
### Added
- Better prompts against network conditions.
- `DEBUG` env for exception hook.
- Massive code refactor.

## [0.4.0] - 2021-11-06
### Added
- Add spinners for better user experience.

## [0.3.0] - 2021-11-06
### Removed
- Remove `Rich` since it's too heavy and not ideal for MarkDown rendering.

### Changed
- Refactor `Formatter` to process&render page content.
- Encapsulate `secho` as info&warn functions.

## [0.2.3] - 2021-10-23
### Added
- Use `tox` for test integration.
- Use `black` for formatting.
- Use `tbump` for version bumping.

## [0.2.2] - 2021-10-20
### Changed
- Fix `importlib.metadata` import error.

## [0.2.1] - 2021-10-20
### Changed
- Exclude more folders for flake8.
- Make an editable install for ci test.

## [0.2.0] - 2021-10-20
### Added
- Test passing badge.

### Changed
- Use static medadata with setup.cfg.

## [0.1.0] - 2021-10-14
### Added
- Initial project structure.
