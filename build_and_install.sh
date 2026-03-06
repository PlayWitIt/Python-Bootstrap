#!/bin/bash

# --- Configuration for your App (Build & Install) ---
APP_NAME_FRIENDLY="PyBootstrap Tool"      # User-friendly name for messages
PYTHON_SCRIPT_NAME="main.py"              # Our CLI script
PYINSTALLER_APP_NAME="pybs_executable"    # Name for PyInstaller output folder
COMMAND_NAME="pybs"                       # The command users will type

# --- Behavior Configuration ---
# Set to true to always rebuild the .spec file from the Python script, skipping the prompt.
# Set to false to be prompted if an existing .spec file is found.
FORCE_REBUILD_SPEC=true # Always rebuild, simpler for this tool

# --- PyInstaller Data/Assets Configuration (OPTIONAL) ---
# **Simple Asset Bundling:**
# If your application has a common assets folder (e.g., for images, templates)
# located directly in your project root (where this script is), specify its name here.
# This folder will be copied into your application bundle under the SAME NAME.
# Example: COMMON_ASSETS_FOLDER_NAME="assets"
# Example: COMMON_ASSETS_FOLDER_NAME="data_files"
# If you have NO such common folder, or your needs are more complex, leave this EMPTY:
COMMON_ASSETS_FOLDER_NAME=""

# **Advanced Asset Bundling:**
# Use this ONLY if COMMON_ASSETS_FOLDER_NAME is empty or insufficient for your needs.
# For more complex scenarios (multiple distinct folders/files, different destination names in bundle),
# you can directly specify the full PyInstaller --add-data flags here.
# Each flag should be separated by a space. Ensure proper quoting for paths with spaces.
# THIS IS THE CRUCIAL PART. We are bundling the 'templates' directory.
# The format is "SOURCE:DESTINATION_IN_BUNDLE"
ADVANCED_ASSETS_PYINSTALLER_FLAGS="--add-data \"templates:templates\""

# --- PyInstaller General Options (for building from .py script) ---
# These are applied when building FROM THE PYTHON SCRIPT.
# For .spec file builds, only a minimal set of runtime flags will be used (see PYINSTALLER_SPEC_BUILD_OPTIONS).
# We want a single file executable for our command line tool.
PYINSTALLER_GENERAL_OPTIONS="--onefile --noconfirm --log-level=INFO"

# --- PyInstaller Options for .spec file builds ---
# Only general runtime flags should go here.
# Structural options (like --add-data, --onefile) MUST be in the .spec file itself.
PYINSTALLER_SPEC_BUILD_OPTIONS="--noconfirm --log-level=INFO" # Add --clean if desired
# --- End Configuration ---

# --- Log File Setup ---
# Sanitize app name for log file (replace non-alphanumeric/hyphen/underscore with underscore)
LOG_FILE_SANITIZED_APP_NAME=$(echo "$PYINSTALLER_APP_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE_NAME="build_install_${LOG_FILE_SANITIZED_APP_NAME}.log"

# Function to log messages to console and file
log_message() {
    echo "$@" | tee -a "$LOG_FILE_NAME"
}

# Initialize log file
echo "Build and Install script started at $(date)" > "$LOG_FILE_NAME"
log_message "Logging to: $PWD/$LOG_FILE_NAME"
log_message "-----------------------------------------------------"


# --- Sanity Checks for Configuration ---
check_config_names() {
    local has_error_flag=false # Use a different name to avoid conflict with `e` alias if set
    local name_var_value="$1"
    local name_var_name="$2"

    if [[ "$name_var_value" =~ [^a-zA-Z0-9_.-] || "$name_var_value" =~ \  ]]; then
        log_message "WARNING: Configuration variable '$name_var_name' (\"$name_var_value\") contains spaces or potentially problematic characters."
        log_message "         It's recommended to use only alphanumeric characters, underscores, hyphens, or dots."
    fi
    if [ -z "$name_var_value" ]; then
        log_message "ERROR: Configuration variable '$name_var_name' cannot be empty."
        has_error_flag=true
    fi

    if $has_error_flag; then # Check the flag
        log_message "Configuration errors found. Exiting."
        exit 1
    fi
}

log_message "Performing configuration sanity checks..."
check_config_names "$PYINSTALLER_APP_NAME" "PYINSTALLER_APP_NAME"
check_config_names "$COMMAND_NAME" "COMMAND_NAME"

if [ ! -f "$PYTHON_SCRIPT_NAME" ]; then # Assumes PYTHON_SCRIPT_NAME is relative to project root
    log_message "ERROR: PYTHON_SCRIPT_NAME ('$PYTHON_SCRIPT_NAME') does not point to an existing file in the project root."
    log_message "       Please ensure it's correctly set and the script is run from the project root."
    exit 1
fi
log_message "Configuration sanity checks passed (or warnings issued)."
log_message "-----------------------------------------------------"


# --- Main Script Body ---
log_message "Attempting to build and install $APP_NAME_FRIENDLY ($COMMAND_NAME command)..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# --- Construct PyInstaller Asset Options (for .py builds) ---
_CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD=""
if [ -n "$COMMON_ASSETS_FOLDER_NAME" ]; then
    if [ -d "$PROJECT_ROOT/$COMMON_ASSETS_FOLDER_NAME" ]; then
        # Ensure quotes are part of the string for eval later
        _CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD="--add-data \"$COMMON_ASSETS_FOLDER_NAME:$COMMON_ASSETS_FOLDER_NAME\""
        log_message "INFO: For .py builds, will attempt to bundle common assets: '$COMMON_ASSETS_FOLDER_NAME' as '$_CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD'"
    else
        log_message "WARNING: COMMON_ASSETS_FOLDER_NAME ('$COMMON_ASSETS_FOLDER_NAME') is set, but directory not found at '$PROJECT_ROOT/$COMMON_ASSETS_FOLDER_NAME'. No assets will be added via this option for .py builds."
    fi
elif [ -n "$ADVANCED_ASSETS_PYINSTALLER_FLAGS" ]; then
    _CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD="$ADVANCED_ASSETS_PYINSTALLER_FLAGS"
    log_message "INFO: For .py builds, using advanced asset configuration flags: '$_CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD'"
else
    log_message "INFO: No common or advanced asset bundling configured for .py builds."
fi

# Final options FOR BUILDING FROM PYTHON SCRIPT
PYINSTALLER_OPTIONS_FOR_PY_BUILD="${PYINSTALLER_GENERAL_OPTIONS}${_CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD:+ }${_CONSTRUCTED_ASSETS_OPTION_FOR_PY_BUILD}"
log_message "PyInstaller options for .py builds (before --name/script): $PYINSTALLER_OPTIONS_FOR_PY_BUILD"
log_message "-----------------------------------------------------"
# --- End Construct PyInstaller Asset Options ---

# --- Virtual Environment Activation ---
VENV_ACTIVATED=false
ORIGINAL_VIRTUAL_ENV="$VIRTUAL_ENV"

try_activate_venv() {
    local venv_dir_name="$1"
    local venv_path="$PROJECT_ROOT/$venv_dir_name"
    local activate_script="$venv_path/bin/activate"

    if [ -f "$activate_script" ]; then
        log_message "Attempting to activate virtual environment: $venv_path"
        if [ -n "$VIRTUAL_ENV" ]; then
            type deactivate &>/dev/null && deactivate
        fi
        # shellcheck source=/dev/null
        source "$activate_script"
        if [ -n "$VIRTUAL_ENV" ] && [ "$VIRTUAL_ENV" = "$venv_path" ]; then
            log_message "Successfully activated virtual environment: $VIRTUAL_ENV"
            VENV_ACTIVATED=true
            return 0
        else
            log_message "Warning: Sourced '$activate_script', but VIRTUAL_ENV is not set as expected."
            log_message "Current VIRTUAL_ENV: $VIRTUAL_ENV (Expected: $venv_path)"
            if [ -n "$ORIGINAL_VIRTUAL_ENV" ]; then
                log_message "Attempting to restore original VIRTUAL_ENV state is complex and not fully implemented."
            fi
            return 1
        fi
    else
        return 1
    fi
}

log_message "" # Blank line for readability in log
log_message "-----------------------------------------------------"
log_message " Step -1: Virtual Environment Setup"
log_message "-----------------------------------------------------"

if try_activate_venv "venv"; then
    : # Successfully activated 'venv'
elif try_activate_venv ".venv"; then
    : # Successfully activated '.venv'
else
    log_message "Common virtual environment directories ('venv', '.venv') not found or failed to activate."
    read -r -p "Enter your virtual environment directory name (e.g., my_env, or press Enter to skip): " USER_VENV_NAME >&2
    if [ -n "$USER_VENV_NAME" ]; then
        if ! try_activate_venv "$USER_VENV_NAME"; then
            log_message "Failed to activate user-specified virtual environment: $PROJECT_ROOT/$USER_VENV_NAME"
            log_message "Proceeding without an active virtual environment managed by this script."
        fi
    else
        log_message "Skipping virtual environment activation as per user request."
        log_message "Proceeding using system Python or any pre-activated environment."
    fi
fi

if $VENV_ACTIVATED; then
    log_message "Using activated virtual environment for subsequent steps."
else
    log_message "No script-managed virtual environment activated. Dependencies will be handled by system Python or pre-existing environment."
fi
log_message "" # Blank line


# --- Pre-requisite: Check and Install PyInstaller if needed ---
log_message "-----------------------------------------------------"
log_message " Step 0A: PyInstaller Check & Installation"
log_message "-----------------------------------------------------"
if ! command -v pyinstaller &> /dev/null; then
    log_message "PyInstaller command could not be found."
    log_message "Attempting to install PyInstaller..."

    PIP_COMMAND=""
    if command -v pip3 &> /dev/null; then PIP_COMMAND="pip3";
    elif command -v pip &> /dev/null; then PIP_COMMAND="pip";
    else
        log_message "Error: Neither 'pip3' nor 'pip' command found. Cannot install PyInstaller."
        exit 1
    fi

    log_message "Using '$PIP_COMMAND' to install PyInstaller."
    INSTALL_CMD_STR="$PIP_COMMAND install --disable-pip-version-check pyinstaller click"
    INSTALL_TARGET_MSG="into the active virtual environment."

    if ! $VENV_ACTIVATED; then
        INSTALL_CMD_STR="$PIP_COMMAND install --user --disable-pip-version-check pyinstaller click"
        INSTALL_TARGET_MSG="for the current user (via --user)."
    fi

    log_message "Installing PyInstaller & Click $INSTALL_TARGET_MSG"
    PIP_INSTALL_OUTPUT=$(eval "$INSTALL_CMD_STR" 2>&1) # Capture output
    PIP_INSTALL_EXIT_CODE=$?
    echo "$PIP_INSTALL_OUTPUT" | tee -a "$LOG_FILE_NAME" # Log the captured output

    if [ $PIP_INSTALL_EXIT_CODE -eq 0 ]; then
        log_message "PyInstaller/Click installed successfully."
        if ! $VENV_ACTIVATED && [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            log_message "Adding '$HOME/.local/bin' to PATH for this script session."
            export PATH="$HOME/.local/bin:$PATH"
        fi
        if ! command -v pyinstaller &> /dev/null; then
            log_message "Error: PyInstaller was installed, but the 'pyinstaller' command is still not found in PATH."
            if ! $VENV_ACTIVATED; then
                 log_message "This might happen if '$HOME/.local/bin' is not in your system's PATH."
                 log_message "Please open a new terminal session or add '$HOME/.local/bin' to your PATH manually and try again."
            else
                 log_message "This is unexpected within an active virtual environment. Please check the venv."
            fi
            exit 1
        fi
        log_message "PyInstaller is now available."
    else
        log_message "Error: Failed to install PyInstaller/Click using '$PIP_COMMAND'. Exit code: $PIP_INSTALL_EXIT_CODE."
        log_message "Please install PyInstaller and click manually and try again."
        exit 1
    fi
else
    log_message "PyInstaller is already available."
    if $VENV_ACTIVATED && [[ "$(command -v pyinstaller)" != "$VIRTUAL_ENV/bin/pyinstaller"* ]]; then
        log_message "Warning: PyInstaller found, but it might not be from the active virtual environment ($VIRTUAL_ENV)."
        log_message "Found at: $(command -v pyinstaller)"
    fi
fi


# --- 0B. Build the Package with PyInstaller ---
log_message "" # Blank line
log_message "-----------------------------------------------------"
log_message " Step 0B: Building $APP_NAME_FRIENDLY with PyInstaller"
log_message "-----------------------------------------------------"

SOURCE_PYTHON_FILE="$PROJECT_ROOT/$PYTHON_SCRIPT_NAME"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

SPEC_FILE_NAME="${PYINSTALLER_APP_NAME}.spec"
POTENTIAL_SPEC_FILE="$PROJECT_ROOT/$SPEC_FILE_NAME"

PYINSTALLER_BUILD_CMD_STR="" # This will hold the final pyinstaller command string
BUILD_FROM_SPEC_FLAG=false # Renamed to avoid confusion with internal shell commands

if ! $FORCE_REBUILD_SPEC && [ -f "$POTENTIAL_SPEC_FILE" ]; then
    log_message "An existing .spec file was found: $POTENTIAL_SPEC_FILE"
    while true; do
        read -r -p "Do you want to use this existing .spec file for the build? (yes/no/abort): " yn_spec_prompt >&2
        case $yn_spec_prompt in
            [Yy]* ) BUILD_FROM_SPEC_FLAG=true; log_message "User chose to use existing .spec file."; break;;
            [Nn]* ) BUILD_FROM_SPEC_FLAG=false; log_message "User chose to regenerate .spec file."; break;;
            [Aa]* ) log_message "Build aborted by user."; exit 0;;
            * ) echo "Please answer yes, no, or abort." >&2;; # Not logged, just console feedback for prompt retry
        esac
    done
else
    if $FORCE_REBUILD_SPEC && [ -f "$POTENTIAL_SPEC_FILE" ]; then
        log_message "FORCE_REBUILD_SPEC is true. Will regenerate .spec file."
    elif ! [ -f "$POTENTIAL_SPEC_FILE" ]; then
        log_message "No existing .spec file found. Will build from Python script."
    fi
    # BUILD_FROM_SPEC_FLAG remains false (default)
fi

if $BUILD_FROM_SPEC_FLAG; then
    log_message "Using existing .spec file: $POTENTIAL_SPEC_FILE for the build."
    # Use PYINSTALLER_SPEC_BUILD_OPTIONS when building from .spec file
    PYINSTALLER_BUILD_CMD_STR="pyinstaller $PYINSTALLER_SPEC_BUILD_OPTIONS \"$POTENTIAL_SPEC_FILE\""

    log_message "Cleaning up previous build output directories (dist/$PYINSTALLER_APP_NAME, build/$PYINSTALLER_APP_NAME)..."
    rm -rf "$DIST_DIR/$PYINSTALLER_APP_NAME"
    rm -rf "$BUILD_DIR/$PYINSTALLER_APP_NAME"
else # Build from Python script
    log_message "Building from Python script: $SOURCE_PYTHON_FILE."
    log_message "Any existing .spec file ($SPEC_FILE_NAME) will be overwritten if PyInstaller generates one."
    log_message "Cleaning up previous build artifacts (dist, build, and .spec file)..."
    rm -rf "$DIST_DIR"
    rm -rf "$BUILD_DIR"
    rm -f "$POTENTIAL_SPEC_FILE" # Remove old spec if building from .py

    # Use PYINSTALLER_OPTIONS_FOR_PY_BUILD when building from .py script
    PYINSTALLER_BUILD_CMD_STR="pyinstaller $PYINSTALLER_OPTIONS_FOR_PY_BUILD --name \"$COMMAND_NAME\" \"$SOURCE_PYTHON_FILE\""
fi

log_message "Running PyInstaller with command: $PYINSTALLER_BUILD_CMD_STR"
# Execute PyInstaller and capture its stdout/stderr to log file AND console
# Using subshell to capture output, then process with tee
(eval "$PYINSTALLER_BUILD_CMD_STR") 2>&1 | tee -a "$LOG_FILE_NAME"
PYINSTALLER_EXIT_CODE=${PIPESTATUS[0]} # Get exit code of eval (the first command in pipe)

if [ $PYINSTALLER_EXIT_CODE -ne 0 ]; then
  log_message "Error: PyInstaller build failed with exit code $PYINSTALLER_EXIT_CODE. Please check the output above."
  exit 1
fi
log_message "PyInstaller build successful."
log_message "" # Blank line


# --- Installation Steps ---
log_message "-----------------------------------------------------"
log_message " Step 1: Installing $COMMAND_NAME"
log_message "-----------------------------------------------------"

# In our case, building from .py always happens, and we set --onefile
# So the executable will be at dist/COMMAND_NAME
APP_EXE_FINAL_PATH="$DIST_DIR/$COMMAND_NAME"

INSTALL_TARGET_DIR="/usr/local/bin"
INSTALL_LINK_NAME="$INSTALL_TARGET_DIR/$COMMAND_NAME"

if [ ! -f "$APP_EXE_FINAL_PATH" ]; then
  log_message "Error: Bundled application not found at '$APP_EXE_FINAL_PATH' after PyInstaller run."
  exit 1
fi

if [ ! -d "$INSTALL_TARGET_DIR" ]; then
  log_message "Warning: Target directory '$INSTALL_TARGET_DIR' does not exist."
  log_message "Attempting to create '$INSTALL_TARGET_DIR' with sudo..."
  SUDO_MKDIR_OUTPUT=$(sudo mkdir -p "$INSTALL_TARGET_DIR" 2>&1)
  SUDO_MKDIR_EXIT_CODE=$?
  echo "$SUDO_MKDIR_OUTPUT" | tee -a "$LOG_FILE_NAME"
  if [ $SUDO_MKDIR_EXIT_CODE -ne 0 ]; then
      log_message "Error: Failed to create '$INSTALL_TARGET_DIR'. Exit code: $SUDO_MKDIR_EXIT_CODE."
      exit 1
  fi
fi

if [ ! -w "$INSTALL_TARGET_DIR" ]; then
    log_message "Warning: You may not have write permissions for '$INSTALL_TARGET_DIR'."
    log_message "The script will attempt to use 'sudo' to create the symbolic link."
fi

if [ -L "$INSTALL_LINK_NAME" ] || [ -f "$INSTALL_LINK_NAME" ]; then
  log_message "'$INSTALL_LINK_NAME' already exists."
  log_message "Attempting to remove existing '$INSTALL_LINK_NAME' with sudo..."
  SUDO_RM_OUTPUT=$(sudo rm -f "$INSTALL_LINK_NAME" 2>&1)
  SUDO_RM_EXIT_CODE=$?
  echo "$SUDO_RM_OUTPUT" | tee -a "$LOG_FILE_NAME"
  if [ $SUDO_RM_EXIT_CODE -ne 0 ]; then
      log_message "Error: Failed to remove existing file/link. Exit code: $SUDO_RM_EXIT_CODE."
      exit 1
  fi
fi

log_message "Creating symbolic link: $INSTALL_LINK_NAME -> $APP_EXE_FINAL_PATH"
SUDO_LN_OUTPUT=$(sudo ln -s "$APP_EXE_FINAL_PATH" "$INSTALL_LINK_NAME" 2>&1)
SUDO_LN_EXIT_CODE=$?
echo "$SUDO_LN_OUTPUT" | tee -a "$LOG_FILE_NAME"
if [ $SUDO_LN_EXIT_CODE -ne 0 ]; then
    log_message "Error creating symbolic link. Exit code: $SUDO_LN_EXIT_CODE."
    exit 1
fi

if [ -L "$INSTALL_LINK_NAME" ] && [ "$(readlink "$INSTALL_LINK_NAME")" = "$APP_EXE_FINAL_PATH" ]; then
  log_message "" # Blank line
  log_message "-----------------------------------------------------"
  log_message " $APP_NAME_FRIENDLY ($COMMAND_NAME) built and installed successfully!"
  log_message " You should now be able to run '$COMMAND_NAME' from any terminal."
  log_message "-----------------------------------------------------"
else
  log_message "Error: Failed to create the symbolic link correctly."
  log_message "Please check permissions for '$INSTALL_TARGET_DIR' or try creating the link manually:"
  log_message "sudo ln -s \"$APP_EXE_FINAL_PATH\" \"$INSTALL_LINK_NAME\""
  exit 1
fi

if $VENV_ACTIVATED ; then
    if [ -n "$ORIGINAL_VIRTUAL_ENV" ] && [ "$ORIGINAL_VIRTUAL_ENV" != "$VIRTUAL_ENV" ]; then
        log_message "Script changed the active virtual environment. The original was: $ORIGINAL_VIRTUAL_ENV"
        log_message "You might need to manually reactivate it or open a new terminal."
    elif [ "$ORIGINAL_VIRTUAL_ENV" = "" ] ; then
        type deactivate &>/dev/null && deactivate
        log_message "Deactivated script-managed virtual environment."
    fi
fi

log_message "Build and Install script finished at $(date)"
exit 0
