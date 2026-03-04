#!/usr/bin/env bash

# ==============================================================================
# Script to robustly activate a Python virtual environment (if found)
# and run a Python script (main.py, app.py, or myapp.py).
#
# Features:
# - Exits immediately on error, unset variable, or pipe failure.
# - Optionally launches itself in a new terminal if not already in one.
# - Automatically detects virtual environment: '.venv' (preferred) or 'venv'.
# - If a venv directory is found but misconfigured (e.g., no activate script
#   or python executable), it errors out.
# - If no venv is found, it gracefully uses the system Python.
# - Automatically detects Python script to run: 'main.py' (preferred),
#   'app.py' (secondary), or 'myapp.py' (tertiary). If none are found, it
#   prompts the user and can permanently update itself with the new choice.
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

# Python script names in order of preference
SCRIPT_PRIMARY="test.py"
SCRIPT_SECONDARY="app.py"
SCRIPT_TERTIARY="myapp.py"
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
    # Use a specific environment variable to avoid infinite loops.
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
                # Konsole might need --hold or similar if -e closes immediately after script,
                # but the read command in INNER_COMMAND_STRING should handle this.
                TERMINAL_LAUNCH_CMD=(konsole -e bash -c "$INNER_COMMAND_STRING")
            elif command -v xfce4-terminal &> /dev/null; then
                 TERMINAL_LAUNCH_CMD=(xfce4-terminal --hold --command="bash -c '$INNER_COMMAND_STRING'") # Added --hold for safety
            elif command -v xterm &> /dev/null; then
                TERMINAL_LAUNCH_CMD=(xterm -hold -e bash -c "$INNER_COMMAND_STRING") # Added -hold for safety
            # Add other terminal emulators here if needed
            # elif command -v mate-terminal &> /dev/null; then
            #    TERMINAL_LAUNCH_CMD=(mate-terminal -- bash -c "$INNER_COMMAND_STRING")
            # elif command -v terminator &> /dev/null; then
            #    TERMINAL_LAUNCH_CMD=(terminator -e "bash -c '$INNER_COMMAND_STRING'")
            fi

            if [ ${#TERMINAL_LAUNCH_CMD[@]} -gt 0 ]; then
                echo "Using: ${TERMINAL_LAUNCH_CMD[0]} to re-launch..."
                # Pass the original script path and its arguments to the new terminal instance
                "${TERMINAL_LAUNCH_CMD[@]}" "$SCRIPT_PATH_FOR_RELAUNCH" "$@"
                exit_status=$?
                # This part will only be reached if the terminal emulator itself failed to launch
                # or if the inner command somehow exited in a way that the terminal closed immediately
                # AND the terminal command itself reported an error.
                if [ $exit_status -ne 0 ]; then
                    echo "Failed to launch in new terminal (terminal emulator exit code: $exit_status)." >&2
                fi
                exit "$exit_status" # Exit with the terminal emulator's exit status
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
PYTHON_EXECUTABLE="python3" # Default to system python3 if no venv is found/used
                            # Changed to python3 as it's more common now.
                            # Use "python" if you specifically need the 'python' symlink.
# --- Helper Functions ---
# Function to print error messages to stderr and exit
error_exit() {
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
    # VENV_DIR_TO_USE remains empty, PYTHON_EXECUTABLE will default to "python3"
fi

# 2. Determine Python executable and activate venv if one was identified
if [ -n "$VENV_DIR_TO_USE" ]; then # -n checks if the string is not empty (i.e., a venv dir was found)
    ACTIVATE_SCRIPT="$VENV_DIR_TO_USE/bin/activate"
    # Prefer python3 in venv as well, but fall back to python if python3 isn't there
    # This is more robust for venvs created with older 'virtualenv' or specific flags.
    if [ -f "$VENV_DIR_TO_USE/bin/python3" ]; then
        EXPECTED_VENV_PYTHON="$VENV_DIR_TO_USE/bin/python3"
    elif [ -f "$VENV_DIR_TO_USE/bin/python" ]; then
        EXPECTED_VENV_PYTHON="$VENV_DIR_TO_USE/bin/python"
    else
        EXPECTED_VENV_PYTHON="" # Will be caught by the check below
    fi


    if [ ! -f "$ACTIVATE_SCRIPT" ]; then
        error_exit "Virtual environment directory '$VENV_DIR_TO_USE' found, but its activation script '$ACTIVATE_SCRIPT' is missing. Please ensure it's a valid virtual environment."
    fi

    if [ -z "$EXPECTED_VENV_PYTHON" ] || [ ! -f "$EXPECTED_VENV_PYTHON" ]; then
        error_exit "Virtual environment directory '$VENV_DIR_TO_USE' found, and '$ACTIVATE_SCRIPT' exists, but a Python executable ('$VENV_DIR_TO_USE/bin/python3' or '$VENV_DIR_TO_USE/bin/python') is missing. The venv seems corrupted or improperly created."
    fi

    info "Activating virtual environment '$VENV_DIR_TO_USE'..."
    # shellcheck source=/dev/null
    source "$ACTIVATE_SCRIPT" # `set -e` will cause exit if source fails

    PYTHON_EXECUTABLE="$EXPECTED_VENV_PYTHON"
    info "Will use Python interpreter from virtual environment: $PYTHON_EXECUTABLE"
else
    # Check if the default PYTHON_EXECUTABLE exists in PATH
    if ! command -v "$PYTHON_EXECUTABLE" &> /dev/null; then
        # If python3 is not found, try python
        if command -v "python" &> /dev/null; then
            PYTHON_EXECUTABLE="python"
            info "Default '$PYTHON_EXECUTABLE' (python3) not found. Falling back to 'python'."
        else
            error_exit "No virtual environment found, and neither 'python3' nor 'python' executables are available in the system PATH. Please install Python or ensure it's in your PATH."
        fi
    fi
    info "Will attempt to use system Python: $PYTHON_EXECUTABLE (as found in PATH)."
fi

# 3. Determine Python script to run
info "Looking for Python script to run..."
if [ -f "$SCRIPT_PRIMARY" ]; then
    PYTHON_SCRIPT_TO_RUN="$SCRIPT_PRIMARY"
    info "Found '$SCRIPT_PRIMARY' to run."
elif [ -f "$SCRIPT_SECONDARY" ]; then
    PYTHON_SCRIPT_TO_RUN="$SCRIPT_SECONDARY"
    info "Found '$SCRIPT_SECONDARY' to run."
elif [ -f "$SCRIPT_TERTIARY" ]; then
    PYTHON_SCRIPT_TO_RUN="$SCRIPT_TERTIARY"
    info "Found '$SCRIPT_TERTIARY' to run."
else
    info "None of '$SCRIPT_PRIMARY', '$SCRIPT_SECONDARY', or '$SCRIPT_TERTIARY' were found."
    while true; do
        # Direct prompt to stderr to avoid polluting stdout, which might be piped.
        read -r -p "Please enter the name of the Python script to run (or press Enter to abort): " USER_INPUT_SCRIPT_NAME >&2

        if [ -z "$USER_INPUT_SCRIPT_NAME" ]; then
            error_exit "No script specified. Aborting."
        fi

        if [ -f "$USER_INPUT_SCRIPT_NAME" ]; then
            PYTHON_SCRIPT_TO_RUN="$USER_INPUT_SCRIPT_NAME"
            info "Using user-specified script: '$PYTHON_SCRIPT_TO_RUN'"

            # Ask user if they want to make this change permanent
            read -r -p "Update this Run.sh script to use '$PYTHON_SCRIPT_TO_RUN' as the default? [y/N]: " confirm_update >&2
            if [[ "$confirm_update" =~ ^[Yy](es)?$ ]]; then
                info "Attempting to self-update..."
                # Create a temporary file safely
                temp_file=$(mktemp)
                if [ $? -ne 0 ]; then
                    echo "[WARNING] Could not create temporary file for self-update. Script will not be modified." >&2
                else
                    # Use sed to replace the SCRIPT_PRIMARY line and write to the temp file.
                    # Using '|' as a delimiter is safer if the filename contains slashes.
                    sed "s|^SCRIPT_PRIMARY=.*|SCRIPT_PRIMARY=\"$PYTHON_SCRIPT_TO_RUN\"|" "$0" > "$temp_file"

                    # Check if the sed command was successful and the temp file is not empty
                    if [ -s "$temp_file" ]; then
                        # Safely replace the original script with the updated version
                        mv "$temp_file" "$0"
                        # Ensure the script remains executable
                        chmod +x "$0"
                        info "Script updated successfully. '$PYTHON_SCRIPT_TO_RUN' is now the primary target."
                    else
                        echo "[WARNING] Self-update failed: could not generate new script content." >&2
                        # Clean up the empty temp file
                        rm -f "$temp_file"
                    fi
                fi
            fi
            break # Exit loop, we found a valid script.
        else
            echo "[ERROR] File '$USER_INPUT_SCRIPT_NAME' not found. Please try again." >&2
        fi
    done
fi

# 4. Run the Python script
info "Running $PYTHON_SCRIPT_TO_RUN using $PYTHON_EXECUTABLE..."
# Pass all script arguments ($@) to the Python script
"$PYTHON_EXECUTABLE" "$PYTHON_SCRIPT_TO_RUN" "$@"

# 5. Done
info "Script execution finished successfully."

exit 0
