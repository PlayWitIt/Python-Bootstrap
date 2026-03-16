# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-03

### Added
- `--version` flag to CLI
- `--no-run` flag to skip Run.sh generation
- `pyproject.toml` for proper Python packaging
- ShellCheck directives for bash best practices
- Centralized version management in `version.py`
- Fixed package data include for templates

### Changed
- Removed auto-addition of PyQt6 dependency
- Cleaned up debug echo statements from terminal auto-launch
- Dynamic Conda path detection instead of hardcoded path
- Improved README documentation
- Better error handling in CLI

### Fixed
- Fixed undefined variable `_IN_TERMINAL_ALREADY` warning
- Fixed junk text at top of templates/Run.sh

### Removed

## [0.1.0] - 2024-01-01

### Added
- Initial release
- `pybs init` command
- `py_bootstrap.sh` for environment setup
- `Run.sh` for easy script execution
- Support for pyenv, conda, and system Python
- Git repository initialization option
- Terminal auto-launch feature
