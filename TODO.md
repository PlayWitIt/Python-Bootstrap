# TODO - Future Improvements

## Planned Features

### Windows Support
- Add `.bat` or PowerShell equivalents for `py_bootstrap.sh` and `Run.sh`
- Support Windows-native virtual environments

### Config File
- Store defaults in a config file (e.g., preferred script name, venv location)
- `~/.pybsrc` or `pyproject.toml` section

### Doctor Command
- `pybs doctor` - Diagnose common issues:
  - Missing venv
  - Broken symlinks
  - Missing dependencies
  - Permission issues

## Completed Features (v1.2.0)

- [x] `pybs exec <script.py>` - Run scripts directly
- [x] `--force` flag - Skip overwrite confirmation
- [x] Bash completions - Shell auto-complete support