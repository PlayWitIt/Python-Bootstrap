# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-04-13

### Added
- `pybs exec <script.py>` - Run Python scripts directly without needing Run.sh
- `pybs exec myscript.py --arg1 value` - Pass arguments to scripts
- `pybs exec --no-venv` - Use system Python instead of venv
- `--force` / `-f` flag to all commands - Overwrite existing scripts without prompting
- Bash completion script (`templates/pybs-completion.bash`)
- TODO.md for future roadmap

### Changed
- All commands now support `--force` flag for batch operations

## [1.1.2] - 2026-04-13

### Added
- `pybs init` - Initialize with both scripts (existing behavior)
- `pybs bootstrap` - Create only py_bootstrap.sh
- `pybs run` - Create only Run.sh

### Changed
- Updated Run.sh with colored output (INFO, SUCCESS, ERROR, section headers)
- Updated py_bootstrap.sh with colored output matching Run.sh
- Both scripts now have Ctrl+C interrupt handling
- Removed debug code from templates
- py_bootstrap.sh now supports double-click auto-launch

## [1.1.0] - 2026-04-13

### Added
- Enhanced Run.sh UI with color-coded output (INFO, SUCCESS, ERROR, section headers)
- Ctrl+C interrupt handling with user-friendly message
- Scans all subdirectories for Python scripts (not limited to 2 levels)
- Excludes .venv and venv folders from script search

### Changed
- Improved script detection logic using `printf "%P\n"` for proper relative paths
- Simplified and cleaned up Run.sh code
- Updated auto-launch terminal messages for consistency

### Fixed
- Run.sh now correctly finds Python scripts in nested folders

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
