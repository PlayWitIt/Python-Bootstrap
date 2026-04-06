#!/usr/bin/env bash
# shellcheck shell=bash

# ==============================================================================
# Script to robustly activate a Python virtual environment (if found)
# and run a user-selected Python script from the current directory.
#
# Features:
# - Exits immediately on error, unset variable, or pipe failure.
# - Optionally launches itself in a new terminal if not already in one.
# - Automatically detects virtual environment: '.venv' (preferred) or 'venv'.
# - If a venv directory is found but misconfigured, it errors out.
# - If no venv is found, it gracefully uses the system Python.
# - Scans the current directory for all `.py` files and presents a
#   simple, numbered menu for the user to choose which script to run.
# - If a venv is used, it explicitly calls the venv's Python interpreter.
# - Provides clear informational and error messages.
# ==============================================================================

# --- Script Configuration ---
# Toggle whether to attempt launching in a new terminal if not run from one.
# Set to "false" to disable this feature.
LAUNCH_IN_TERMINAL="true"

# Preferred venv directory names
VENV_DIR_PRIMARY=".venv"
VENV_DIR_SECONDARY="venv"
# --- End Configuration ---


# Strict mode
# -e: Exit immediately if a command exits with a non-zero status.
# -u: Treat unset variables as an error when substituting.
# -o pipefail: The return value of a pipeline is the status of the last
#              command to exit with a non-zero status, or zero if no
#              command exited with a non-zero status.
set -euo pipefail

# --- Self-launch in terminal if not already in one (and feature is enabled) ---
if [ "$LAUNCH_IN_TERMINAL" = "true" ]; then
    # shellcheck disable=SC2034
    if [ "${_IN_TERMINAL_ALREADY:-false}" != "true" ]; then
        # Check if standard input is a terminal
        if ! [ -t 0 ]; then
            echo "Script not launched in a terminal. Attempting to re-launch in a new terminal..."
            SCRIPT_PATH_FOR_RELAUNCH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

            TERMINAL_LAUNCH_CMD=()

            # The inner command string ensures the loop-prevention variable is set,
            # executes the script, captures its exit code, displays a message,
            # waits for a key press, and then exits with the original script's code.
            INNER_COMMAND_STRING="export _IN_TERMINAL_ALREADY=true; \"\$0\" \"\$@\"; RES=\$?; echo; echo \"--- Script execution finished (Exit Code: \$RES) ---\"; read -rsp $'Press any key to close this terminal window...\n' -n1 key; exit \$RES"

            if command -v gnome-terminal &> /dev/null; then
                TERMINAL_LAUNCH_CMD=(gnome-terminal -- bash -c "$INNER_COMMAND_STRING")
            elif command -v konsole &> /dev/null; then
                TERMINAL_LAUNCH_CMD=(konsole -e bash -c "$INNER_COMMAND_STRING")
            elif command -v xfce4-terminal &> /dev/null; then
                 TERMINAL_LAUNCH_CMD=(xfce4-terminal --hold --command="bash -c '$INNER_COMMAND_STRING'")
            elif command -v xterm &> /dev/null; then
                TERMINAL_LAUNCH_CMD=(xterm -hold -e bash -c "$INNER_COMMAND_STRING")
            # Add other terminal emulators here if needed
            fi

            if [ ${#TERMINAL_LAUNCH_CMD[@]} -gt 0 ]; then
                echo "Using: ${TERMINAL_LAUNCH_CMD[0]} to re-launch..."
                # Pass the original script path and its arguments to the new terminal instance
                "${TERMINAL_LAUNCH_CMD[@]}" "$SCRIPT_PATH_FOR_RELAUNCH" "$@"
                exit_status=$?
                if [ $exit_status -ne 0 ]; then
                    echo "Failed to launch in new terminal (terminal emulator exit code: $exit_status)." >&2
                fi
                exit "$exit_status"
            else
                echo "ERROR: No suitable terminal emulator (gnome-terminal, konsole, xfce4-terminal, xterm) found." >&2
                echo "Please run this script from an existing terminal, or set LAUNCH_IN_TERMINAL to \"false\" at the top of the script." >&2
                if command -v zenity &> /dev/null; then
                    zenity --error --text="No suitable terminal emulator found.\nPlease run this script from an existing terminal or disable the auto-launch feature." --title="Script Error"
                elif command -v kdialog &> /dev/null; then
                    kdialog --error "No suitable terminal emulator found.\nPlease run this script from an existing terminal or disable the auto-launch feature." --title "Script Error"
                fi
                exit 1
            fi
        fi
    fi
fi
# --- End of self-launch logic ---


# Variables to be determined by the script
VENV_DIR_TO_USE=""
PYTHON_SCRIPT_TO_RUN=""
PYTHON_EXECUTABLE="python3"

# --- Helper Functions ---
# Function to print error messages to stderr and exit
error_exit() {
    echo ""
    echo "[ERROR] $1" >&2
    exit 1
}

# Function to print informational messages to stdout
info() {
    echo "[INFO] $1"
}
# --- End Helper Functions ---

# --- Main Script Logic ---

# 1. Determine virtual environment directory to use
info "Looking for virtual environment..."
if [ -d "$VENV_DIR_PRIMARY" ]; then
    VENV_DIR_TO_USE="$VENV_DIR_PRIMARY"
    info "Found '$VENV_DIR_PRIMARY' directory."
elif [ -d "$VENV_DIR_SECONDARY" ]; then
    VENV_DIR_TO_USE="$VENV_DIR_SECONDARY"
    info "Found '$VENV_DIR_SECONDARY' directory."
else
    info "No standard virtual environment ('$VENV_DIR_PRIMARY' or '$VENV_DIR_SECONDARY') found."
fi

# 2. Determine Python executable and activate venv if one was identified
if [ -n "$VENV_DIR_TO_USE" ]; then
    ACTIVATE_SCRIPT="$VENV_DIR_TO_USE/bin/activate"
    if [ -f "$VENV_DIR_TO_USE/bin/python3" ]; then
        EXPECTED_VENV_PYTHON="$VENV_DIR_TO_USE/bin/python3"
    elif [ -f "$VENV_DIR_TO_USE/bin/python" ]; then
        EXPECTED_VENV_PYTHON="$VENV_DIR_TO_USE/bin/python"
    else
        EXPECTED_VENV_PYTHON=""
    fi

    if [ ! -f "$ACTIVATE_SCRIPT" ]; then
        error_exit "Virtual environment directory '$VENV_DIR_TO_USE' found, but its activation script '$ACTIVATE_SCRIPT' is missing."
    fi

    if [ -z "$EXPECTED_VENV_PYTHON" ] || [ ! -f "$EXPECTED_VENV_PYTHON" ]; then
        error_exit "Virtual environment directory '$VENV_DIR_TO_USE' found, but a Python executable ('.../bin/python3' or '.../bin/python') is missing."
    fi

    info "Activating virtual environment '$VENV_DIR_TO_USE'..."
    # shellcheck source=/dev/null
    source "$ACTIVATE_SCRIPT"

    PYTHON_EXECUTABLE="$EXPECTED_VENV_PYTHON"
    info "Will use Python interpreter from virtual environment: $PYTHON_EXECUTABLE"
else
    if ! command -v "$PYTHON_EXECUTABLE" &> /dev/null; then
        if command -v "python" &> /dev/null; then
            PYTHON_EXECUTABLE="python"
            info "Default 'python3' not found. Falling back to 'python'."
        else
            error_exit "No virtual environment found, and neither 'python3' nor 'python' are in the system PATH."
        fi
    fi
    info "Will attempt to use system Python: $PYTHON_EXECUTABLE (as found in PATH)."
fi

# 3. Find Python scripts and ask the user to choose one
info "Looking for Python scripts..."
# Find all .py files in the current directory and store them in an array
# Using mapfile is a safe way to handle filenames with spaces or special characters
mapfile -t python_files < <(find . -maxdepth 1 -type f -name "*.py" -printf "%f\n")

if [ ${#python_files[@]} -eq 0 ]; then
    error_exit "No Python scripts (.py files) found in the current directory."
fi

# Use the 'select' command to create a simple and robust interactive menu
PS3=$'\nPlease select the Python script to run (enter the number): '
select chosen_script in "${python_files[@]}"; do
    if [[ -n "$chosen_script" ]]; then
        PYTHON_SCRIPT_TO_RUN="$chosen_script"
        info "You have selected: '$PYTHON_SCRIPT_TO_RUN'"
        break # Exit the loop once a valid selection is made
    else
        echo "Invalid selection. Please enter a number from the list." >&2
    fi
done

# 4. Run the Python script
info "Running $PYTHON_SCRIPT_TO_RUN using $PYTHON_EXECUTABLE..."
# Pass all script arguments ($@) to the Python script
"$PYTHON_EXECUTABLE" "$PYTHON_SCRIPT_TO_RUN" "$@"

# 5. Done
info "Script execution finished successfully."

exit 0
