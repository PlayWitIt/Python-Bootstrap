# pybootstrap (`pybs`) Project TODO

[//]: # App_Name
### 💡 Ideas / Wishlist
- [ ] **Windows Support**: Generate equivalent `.bat` or `.ps1` scripts for `py_bootstrap` and `Run` to provide native Windows compatibility.
- [ ] **Template System**: Implement a `--template` flag for `pybs init` (e.g., `pybs init --template fastapi`) that can pull from a collection of project templates (web, data science, etc.) instead of just the default scripts.
- [ ] **Interactive Mode**: Add an `pybs init --interactive` mode that walks the user through setup questions (Initialize Git?, default Python version?, environment manager preference?, etc.).
- [ ] **Dependency Helper Command**: Create a `pybs add <package>` command that automatically adds a dependency to `requirements.txt` and installs it into the detected virtual environment.
- [ ] **Non-interactive Mode for CI/CD**: Add a `--yes` or `--no-input` flag to `py_bootstrap.sh` to allow it to run non-interactively in automated environments, accepting all defaults.

### 📝 Planned Features
- [ ] **Global Configuration File**: Support a `~/.pybsrc` file for users to set personal defaults (e.g., preferred Python version, default to `conda`, disable Git init).
- [ ] **`pybs version` Command**: Add a simple `pybs version` command to display the installed version of the tool.
- [ ] **More Granular `init`**: Allow `pybs init --no-run` or `--no-bootstrap` to generate only one of the two scripts if desired.
- [ ] **Improved Script Discovery in `Run.sh`**: Allow users to configure the list of default script names (`SCRIPT_PRIMARY`, etc.) via command-line arguments or an environment variable.
- [ ] **Pre-commit Hook Integration**: Add an option in `py_bootstrap.sh` to automatically set up a basic `.pre-commit-config.yaml` with common hooks like `black` and `ruff`.

### 🔧 In Progress
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]

### 🐞 Known Bugs
- [ ] **Non-standard Conda Paths**: `py_bootstrap.sh` may struggle to find and initialize Conda if it's installed in a non-standard directory or if the user's shell profile (`.bashrc`, etc.) is not configured correctly.
- [ ] **Terminal Relaunch Limitations**: The list of supported terminal emulators for auto-relaunch is not exhaustive and will fail for less common terminals (e.g., `terminator`, `alacritty`).
- [ ] **`Run.sh` Self-Update Fragility**: The `sed` command in `Run.sh` could fail if a user provides a script name containing special characters that interfere with the substitution.
- [ ]
- [ ]

### 🧹 Cleanup / Refactor
- [ ] **Consolidate Relaunch Logic**: The terminal auto-relaunch logic is duplicated across `py_bootstrap.sh` and `Run.sh`. This could be refactored into a single, source-able helper function if it becomes more complex.
- [ ] **Break Out `main.py` Logic**: Refactor the main `init` function in `main.py` by moving file I/O and permission-setting logic into smaller, dedicated helper functions to improve readability.
- [ ] **Improve `py_bootstrap.sh` Dependency Logic**: The current script blindly adds `PyQt6` if `requirements.txt` is missing. This could be improved to be more generic or prompt the user for a "core" dependency.
- [ ] **Add More Build Script Comments**: Enhance `build_and_install.sh` with more detailed comments explaining the purpose of each PyInstaller flag and build step.
- [ ] **Standardize Shell Script Functions**: Ensure helper functions across all `.sh` files follow a consistent naming convention and output format.
