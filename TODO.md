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




### 📝 Notes

That's a great question. The ideas in the `TODO.md` are a solid starting point, but they mostly focus on iterative improvements to the existing features. I have many more ideas that could expand the scope and power of `pybootstrap` significantly.

Here is a more expansive list of potential future directions, categorized by theme:

---

### Category 1: User Experience & CLI Enhancements

These ideas make the tool more intuitive, helpful, and pleasant to use.

1.  **Tab Completion:**
    *   **What:** Implement shell completion scripts (`pybs completion bash|zsh|fish`).
    *   **Why:** Allows users to press `Tab` to autocomplete commands (`pybs in<TAB>` -> `pybs init`) and options (`pybs init --d<TAB>` -> `pybs init --dir `). This is a hallmark of a professional CLI tool.

2.  **`pybs update-scripts` Command:**
    *   **What:** A command that can be run inside an already initialized project to replace the existing `Run.sh` and `py_bootstrap.sh` with the latest versions from the installed `pybs` tool.
    *   **Why:** As you add features and bug fixes to the template scripts, this allows users to easily upgrade their existing projects without having to manually copy files.

3.  **Better Visual Feedback:**
    *   **What:** Use more color and structure in the output. For example, print a summary table at the end of `init` showing what was created. Use spinners or progress bars for long-running tasks in `py_bootstrap.sh`.
    *   **Why:** Makes the tool's actions clearer and provides a more polished user experience.

---

### Category 2: Project Lifecycle & Maintenance

These ideas extend the tool's usefulness beyond the initial setup.

1.  **`pybs doctor` Command:**
    *   **What:** A diagnostic command that can be run in a project directory to check for common problems.
    *   **Why:** It could detect issues like:
        *   The virtual environment directory (`.venv`) exists but is not listed in `.gitignore`.
        *   Packages are installed in the virtual environment but are missing from `requirements.txt`.
        *   The Python version specified in `.python-version` doesn't match the one in the active virtual environment.

2.  **Dependency Management Helpers:**
    *   **What:** Commands like `pybs add <package>`, `pybs remove <package>`, and `pybs freeze`.
    *   **Why:** This would turn `pybs` into a convenient wrapper around `pip`. `pybs add requests` would automatically activate the venv, run `pip install requests`, and add `"requests"` to `requirements.txt`.

3.  **Script Management Helpers:**
    *   **What:** A command like `pybs set-main my_app.py`.
    *   **Why:** Provides a programmatic way to update `Run.sh`'s primary script variable without having to rely on the interactive prompt or manually editing the file.

---

### Category 3: Extensibility & Power-User Features

These ideas make the tool more flexible and customizable for advanced users.

1.  **User-Defined Templates:**
    *   **What:** Allow users to create their own sets of scripts in a local directory (e.g., `~/.config/pybs/templates/web-app/`). Then they could run `pybs init --template web-app`.
    *   **Why:** This is a massive power-up. It turns `pybs` from a tool with one opinion into a fully-fledged scaffolding engine that users can adapt to their specific needs (FastAPI, Flask, data science, etc.).

2.  **Post-Initialization Hooks:**
    *   **What:** In `py_bootstrap.sh`, look for an optional, user-created script like `post_bootstrap.sh` and execute it at the end of the process.
    *   **Why:** Allows users to add their own custom setup steps (e.g., creating specific subdirectories, fetching API keys from a vault) without having to modify the core template script.

---

### Category 4: Integration with Other Tools

These ideas make `pybootstrap` a better citizen in the modern development ecosystem.

1.  **IDE/Editor Integration:**
    *   **What:** A command like `pybs generate-vscode-settings`.
    *   **Why:** This would create a `.vscode/settings.json` file that automatically configures VSCode to use the Python interpreter from the project's `.venv`. This immediately enables correct linting, debugging, and code completion, which is a huge friction point for beginners.

2.  **Docker Integration:**
    *   **What:** A command `pybs generate-dockerfile`.
    *   **Why:** It could inspect the project, detect the Python version from the environment, and generate a basic, multi-stage `Dockerfile` and a `.dockerignore` file. This would drastically lower the barrier to containerizing the application.

3.  **Task Runner Integration:**
    *   **What:** A command `pybs generate-makefile` or `pybs generate-justfile`.
    *   **Why:** It could create a simple `Makefile` with common targets like `setup`, `run`, `lint`, `clean`, and `install`. This provides a standardized, discoverable set of commands for interacting with the project.

4.  **Distribution/Packaging Helper:**
    *   **What:** A command `pybs generate-pyproject`.
    *   **Why:** This brings back the spirit of your original `build_and_install.sh` in a more modern way. It would generate a basic `pyproject.toml` file, preparing the user's project for packaging and distribution via PyPI.

These ideas represent a potential roadmap, moving `pybootstrap` from a great utility to an indispensable part of a developer's toolkit.
