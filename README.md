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
    - Finds your script (main.py, app.py, etc.)
    - Remembers your choice for next time

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
ℹ️  Starting project setup...
ℹ️  Creating virtual environment...
ℹ️  Installing dependencies...
✅ Project ready! Just run ./Run.sh

$ echo 'print("Hello!")' > main.py

$ ./Run.sh
[INFO] Found '.venv' directory.
[INFO] Activating virtual environment...
[INFO] Running main.py...
Hello!
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

### Initialize a new project

```bash
# In a new directory
pybs init --dir my_project

# Or in current directory
pybs init
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

### pybs init

```bash
pybs init                    # Current directory
pybs init --dir my_project   # New directory
pybs init --no-run          # Skip Run.sh generation
pybs --version             # Show version
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
