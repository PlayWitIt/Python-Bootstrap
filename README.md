# pybootstrap (`pybs`)

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/PlayWitIt/Python-Bootstrap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Just want to start coding? Skip the setup.**

pybootstrap gets you from "I want to write Python" to "running code" in seconds. No tedious setup, no remembering venv commands - just code.

---

## The "Why"

You know how to use venv. But every single time you start a new project:
1. Create a project directory
2. `python -m venv .venv`
3. `source .venv/bin/activate`
4. Install dependencies
5. Create requirements.txt
6. Create .gitignore
7. Initialize Git
8. Next time: remember to activate the environment

**That's 7 steps before you write a single line of code.**

pybootstrap automates all of it - one command, and you're ready to code.

## Who is this for?

- **Everyone**: Whether you barely know Python or you've been coding for years, setup is repetitive and time-consuming.
- **Professionals**: You know venv - you just don't want to repeat the same commands every time.
- **Non-technical users**: Don't want to touch the terminal? Just run the scripts.

## Core Features

- **One-Command Setup**: Run `pybs init`, done.
- **Intelligent Environment** (`py_bootstrap.sh`):
    - Auto-detects pyenv, conda, or system Python
    - Creates and activates virtual environment
    - Installs dependencies from requirements.txt
    - Optional Git initialization with .gitignore
- **Zero-Config Running** (`Run.sh`):
    - Just run `./Run.sh` - always works
    - Auto-activates your venv
    - Finds your script (main.py, app.py, etc.) in any subdirectory
    - Shows interactive menu if no default script found
    - Remembers your choice for next time
    - Color-coded output for easy reading

## Quick Demo

```text
$ pybs init --dir my_project
Working inside new directory: /home/user/my_project
Creating helper scripts...
  - Created and made executable: py_bootstrap.sh
  - Created and made executable: Run.sh

Initialization complete!

Next steps:
1. cd my_project
2. Create your requirements.txt with your dependencies
3. Run: ./py_bootstrap.sh
4. Run: ./Run.sh

$ cd my_project

$ ./py_bootstrap.sh
=== Project Setup ===
[INFO] Detecting Python...
[SUCCESS] Using: Python 3.12.0 (pyenv)
[INFO] Creating virtual environment...
[INFO] Installing dependencies...
[SUCCESS] Project ready! Just run ./Run.sh

$ echo 'print("Hello!")' > main.py

$ ./Run.sh
=== Virtual Environment ===
[INFO] Checking for virtual environment...
[SUCCESS] Found: .venv

=== Script Selection ===
[SUCCESS] Found 'main.py'

=== Execution ===
Running: main.py
Using:   /home/user/my_project/.venv/bin/python

Hello!

=== Complete ===
[SUCCESS] Script finished successfully (exit code: 0)
```

## Installation

### Easiest Way (No Terminal Needed)

1. Download `py_bootstrap.sh` and `Run.sh` from this repository
2. Double-click `py_bootstrap.sh` - it opens a terminal and sets up your project
3. Double-click `Run.sh` to run your code

That's it. No installation, no commands to remember.

### From Terminal

```bash
git clone https://github.com/PlayWitIt/Python-Bootstrap.git
cd Python-Bootstrap
pip install .
```

Now use `pybs` anywhere.

### From PyPI

```bash
pip install PythonBootstraper
```

## Usage

### Initialize a new project (both scripts)

```bash
# In a new directory
pybs init --dir my_project

# Or in current directory
pybs init
```

### Create only the bootstrap script

```bash
# Just py_bootstrap.sh (for environment setup)
pybs bootstrap

# Or in a new directory
pybs bootstrap --dir my_project
```

### Create only the run script

```bash
# Just Run.sh (for running code)
pybs run

# Or in a new directory
pybs run --dir my_project
```

### Set up the environment

```bash
# Just run this once per project
./py_bootstrap.sh

# It will:
# - Create a virtual environment
# - Install dependencies from requirements.txt
# - Ask about Git (optional)
```

### Run your code

```bash
./Run.sh

# That's it. No need to:
# - Remember to activate venv
# - Know which python to use
# - Remember file names
```

## How It Works

### `py_bootstrap.sh` (One-time setup)
Creates your project environment:
- Detects best Python version (pyenv → conda → system)
- Creates `.venv` directory
- Installs your dependencies
- Optionally initializes Git

### `Run.sh` (Every time you run)
Executes your code:
- Finds your virtual environment
- Activates it automatically
- Locates your main script
- Runs it

No activation commands. No path hunting. Just code.

## Options

### pybs init (both scripts)

```bash
pybs init                    # Current directory
pybs init --dir my_project   # New directory
pybs init --force            # Overwrite existing scripts
```

### pybs bootstrap (only py_bootstrap.sh)

```bash
pybs bootstrap                    # Current directory
pybs bootstrap --dir my_project   # New directory
pybs bootstrap --force            # Overwrite existing
```

### pybs run (only Run.sh)

```bash
pybs run                    # Current directory
pybs run --dir my_project   # New directory
pybs run --force            # Overwrite existing
```

### pybs exec (run scripts directly)

```bash
pybs exec myscript.py              # Run a script (auto-finds venv)
pybs exec myscript.py --arg value  # Pass arguments to script
pybs exec --no-venv                # Use system Python
pybs exec                          # Run main.py or app.py if no script specified
```

### Other

```bash
pybs --version             # Show version
pybs --help                # Show help
```

## Requirements

- Python 3.8+
- Linux or macOS
- Windows: Use WSL (see below)

### Windows Users: Use WSL

If you're on Windows, PyBootstrap works best with **WSL (Windows Subsystem for Linux)**:

1. **Install WSL** (one-time):
   ```powershell
   # Open PowerShell as Administrator and run:
   wsl --install
   ```
   Restart your computer when prompted.

2. **Open WSL** and install Python:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv git
   ```

3. **Use PyBootstrap normally**:
   ```bash
   pip install PythonBootstraper
   pybs init --dir myproject
   cd myproject
   ./py_bootstrap.sh
   ```

**Why WSL?** The bootstrap scripts are bash-based, which run natively on Linux/macOS. WSL gives you a full Linux environment on Windows with minimal setup.

**Alternative:** You can also run these scripts in Git Bash, but some features (like auto-opening a terminal) may not work fully.

## License

MIT License - see [LICENSE](LICENSE) file.
