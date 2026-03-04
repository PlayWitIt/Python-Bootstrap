# pybootstrap (`pybs`)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/PlayWitIt/Python-Bootstrap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool to quickly initialize a new Python project with robust, intelligent environment setup and execution scripts.

---

## The "Why"

Starting a new Python project often involves the same repetitive boilerplate:
1.  Create a project directory.
2.  Set up a virtual environment (`.venv` or `conda`).
3.  Activate the environment.
4.  Install dependencies.
5.  Create a `.gitignore` file.
6.  Initialize a Git repository.
7.  Remember to activate the environment every time you want to run your script.

`pybootstrap` automates this entire process with a single command, dropping two powerful, pre-configured shell scripts into your project that handle everything for you.

## Core Features

-   **One-Command Init**: Run `pybs init` to instantly bootstrap your project.
-   **Intelligent Environment Setup** (`py_bootstrap.sh`):
    -   Automatically detects and uses `pyenv`, `conda`, or system Python.
    -   Cleans up old virtual environments.
    -   Creates a fresh `.venv` or prompts for a Conda environment.
    -   Installs dependencies from `requirements.txt`.
    -   Optionally initializes a Git repository and creates a comprehensive `.gitignore`.
-   **Smart & Simple Execution** (`Run.sh`):
    -   A single, universal command (`./Run.sh`) to run your project.
    -   Automatically activates the correct virtual environment (`.venv` or `conda`).
    -   Automatically finds your main script (`main.py`, `app.py`, etc.).
    -   **Self-correcting**: If it can't find the main script, it will ask you for the correct name and offer to permanently update itself for future runs.
-   **Cross-Platform**: The generated scripts are designed for Linux and macOS environments.

## Quick Demo

Here's what a typical workflow looks like:

```text
$ pybs init --dir my_awesome_project
Working inside new directory: /home/user/code/my_awesome_project
Creating helper scripts...
  - Created and made executable: py_bootstrap.sh
  - Created and made executable: Run.sh

✅ Initialization complete!

Next steps:
1. Navigate into your project: cd my_awesome_project
2. Set up your Python environment by running: ./py_bootstrap.sh
3. Create your main python file (e.g., main.py, app.py).
4. Run your application using: ./Run.sh

$ cd my_awesome_project

$ ./py_bootstrap.sh
ℹ️  Starting project setup...
ℹ️  Step 1: Cleaning up old local virtual environment ('.venv')...
...
ℹ️  Step 2: Determining Python environment type and creating it...
...
ℹ️  Using system Python to create a standard venv.
...
ℹ️  Step 3: Activating environment for script session and installing dependencies...
...
ℹ️  Step 4: Optional Git Repository Initialization and .gitignore creation...
Do you want to initialize a Git repository in this directory? [y/N]: y
...
✅ Project setup complete!
   Environment setup method: venv
   ...
   To activate the environment in your current terminal session for development, run:
   source ".venv/bin/activate"

$ # Create your app file
$ echo 'print("Hello, pybootstrap!")' > app.py

$ ./Run.sh
[INFO] Looking for virtual environment...
[INFO] Found '.venv' directory.
[INFO] Activating virtual environment '.venv'...
[INFO] Will use Python interpreter from virtual environment: .../.venv/bin/python3
[INFO] Looking for Python script to run...
[INFO] Found 'app.py' to run.
[INFO] Running app.py using .../.venv/bin/python3...
Hello, pybootstrap!
[INFO] Script execution finished successfully.
```

## Installation (Building `pybs` from Source)

The `pybs` command is built using this repository's source code.

#### Prerequisites
-   Python 3.6+ and `pip`
-   `git` (for cloning)

#### Build and Install Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/PlayWitIt/Python-Bootstrap.git
    cd Python-Bootstrap
    ```

2.  **Run the build script:**
    This script handles everything: it creates a virtual environment, installs dependencies (`pyinstaller` and `click`), and runs PyInstaller to build the single-file executable.
    ```bash
    ./build_and_install.sh
    ```
    The script will use `sudo` at the end to create a symbolic link from the built executable to `/usr/local/bin/pybs`, making the command available system-wide.

3.  **Verify the installation:**
    Open a **new terminal** and run:
    ```bash
    pybs --help
    ```
    You should see the help message for the `pybs` command.

## How to Use `pybs`

Once installed, you can use the `pybs` command to initialize new projects.

#### Initialize in a new directory:

This is the recommended approach. It creates a new folder and places the helper scripts inside.
```bash
pybs init --dir my-new-project
```

#### Initialize in the current directory:

Useful if you have already created and navigated into your project folder.
```bash
mkdir my-project
cd my-project
pybs init
```

## The Generated Scripts Explained

### `py_bootstrap.sh`

This script is your **one-time setup tool**. You run it once at the beginning of a project.

-   **Purpose**: To create a clean, consistent, and correct Python virtual environment.
-   **Features**:
    -   **Environment Detection**: It intelligently checks for `pyenv`, then `conda`, then falls back to your system `python3` to create the environment. This ensures the most appropriate Python version is used.
    -   **Dependency Management**: It finds your `requirements.txt` file and installs all listed packages. If the file doesn't exist, the sanitization step is skipped.
    -   **Git Initialization**: It will ask if you want to initialize a Git repository and create a standard, robust `.gitignore` file for Python projects.

### `Run.sh`

This is your **day-to-day run command**. You use it every time you want to execute your application.

-   **Purpose**: To run your main Python script without you having to manually activate the virtual environment every time.
-   **Features**:
    -   **Automatic Activation**: It detects your `.venv` (or other venv/conda environment) and activates it in a sub-shell before running your code, ensuring all your dependencies are available.
    -   **Script Discovery**: It automatically looks for `main.py`, `app.py`, or `myapp.py` to execute.
    -   **Self-Correction**: If it can't find one of the default scripts, it will prompt you to enter the correct filename. It then gives you the option to **permanently save this new filename** as the default by modifying the `Run.sh` script itself.

## Customization

You can easily customize the scripts that `pybs` generates.

1.  Navigate to your cloned `pybootstrap` source directory.
2.  Edit the shell scripts inside the `templates/` folder (`py_bootstrap.sh` and `Run.sh`).
3.  Re-run the build script to package your changes into the `pybs` command:
    ```bash
    ./build_and_install.sh
    ```
    The next time you run `pybs init`, it will generate your newly customized scripts.

## Uninstallation

To remove the `pybs` command from your system and clean up build artifacts:
1.  Navigate to your cloned `pybootstrap` source directory.
2.  Run the uninstall script:
    ```bash
    ./uninstall.sh
    ```
    This will remove the symbolic link from `/usr/local/bin` and ask if you want to delete the `dist/`, `build/`, and `.spec` files.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
