# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Add language option.
- TBC

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
