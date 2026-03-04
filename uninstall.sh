#!/bin/bash

# --- Configuration (SHOULD MATCH YOUR INSTALLER SCRIPT) ---
APP_NAME_FRIENDLY="PyBootstrap Tool"
PYINSTALLER_APP_NAME="pybs_executable"
COMMAND_NAME="pybs"
# --- End Configuration ---

# --- Log File Setup ---
# Sanitize app name for log file
LOG_FILE_SANITIZED_APP_NAME=$(echo "$PYINSTALLER_APP_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE_NAME="uninstall_${LOG_FILE_SANITIZED_APP_NAME}.log"

log_message() {
    echo "$@" | tee -a "$LOG_FILE_NAME"
}

echo "Uninstall script started at $(date)" > "$LOG_FILE_NAME" # Overwrite/start new log
log_message "Logging to: $PWD/$LOG_FILE_NAME"
log_message "-----------------------------------------------------"


# --- Sanity Checks for Configuration ---
check_config_names() {
    local has_error_flag=false
    local name_var_value="$1"
    local name_var_name="$2"
    if [[ "$name_var_value" =~ [^a-zA-Z0-9_.-] || "$name_var_value" =~ \  ]]; then
        log_message "WARNING: Configuration variable '$name_var_name' (\"$name_var_value\") contains spaces or potentially problematic characters."
    fi
    if [ -z "$name_var_value" ]; then
        log_message "ERROR: Configuration variable '$name_var_name' cannot be empty."
        has_error_flag=true
    fi
    if $has_error_flag; then
        log_message "Configuration errors found. Exiting."
        exit 1
    fi
}

log_message "Performing configuration sanity checks..."
check_config_names "$PYINSTALLER_APP_NAME" "PYINSTALLER_APP_NAME (for artifact cleanup)"
check_config_names "$COMMAND_NAME" "COMMAND_NAME (for symlink removal)"
log_message "Configuration sanity checks passed (or warnings issued)."
log_message "-----------------------------------------------------"


log_message "Attempting to uninstall $APP_NAME_FRIENDLY ($COMMAND_NAME command)..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

INSTALL_TARGET_DIR="/usr/local/bin"
INSTALL_LINK_NAME="$INSTALL_TARGET_DIR/$COMMAND_NAME"

DIST_DIR="$PROJECT_ROOT/dist" # Path to dist folder
BUILD_DIR="$PROJECT_ROOT/build" # Path to build folder
SPEC_FILE_NAME="${PYINSTALLER_APP_NAME}.spec"
SPEC_FILE_PATH="$PROJECT_ROOT/$SPEC_FILE_NAME"

# --- 1. Remove the Symbolic Link ---
log_message ""
log_message "-----------------------------------------------------"
log_message " Step 1: Removing Symbolic Link"
log_message "-----------------------------------------------------"

if [ -L "$INSTALL_LINK_NAME" ]; then
    log_message "Symbolic link found at '$INSTALL_LINK_NAME'."
    read -r -p "Are you sure you want to remove this symbolic link? (yes/no): " yn_link >&2
    if [[ "$yn_link" =~ ^[Yy](es)?$ ]]; then
        log_message "User confirmed. Attempting to remove symbolic link '$INSTALL_LINK_NAME' with sudo..."
        SUDO_RM_LINK_OUTPUT=$(sudo rm -f "$INSTALL_LINK_NAME" 2>&1)
        SUDO_RM_LINK_EXIT_CODE=$?
        echo "$SUDO_RM_LINK_OUTPUT" | tee -a "$LOG_FILE_NAME"
        if [ $SUDO_RM_LINK_EXIT_CODE -eq 0 ]; then
            log_message "Symbolic link '$INSTALL_LINK_NAME' removed successfully."
        else
            log_message "Error: Failed to remove symbolic link '$INSTALL_LINK_NAME'. Exit code: $SUDO_RM_LINK_EXIT_CODE."
            log_message "You may need to remove it manually with: sudo rm -f \"$INSTALL_LINK_NAME\""
        fi
    else
        log_message "Skipping removal of symbolic link."
    fi
elif [ -f "$INSTALL_LINK_NAME" ]; then
    log_message "Warning: A regular file (not a symbolic link) exists at '$INSTALL_LINK_NAME'."
    read -r -p "This script normally removes a symbolic link. Are you sure you want to remove this file? (yes/no): " yn_file >&2
    if [[ "$yn_file" =~ ^[Yy](es)?$ ]]; then
        log_message "User confirmed. Attempting to remove file '$INSTALL_LINK_NAME' with sudo..."
        SUDO_RM_FILE_OUTPUT=$(sudo rm -f "$INSTALL_LINK_NAME" 2>&1)
        SUDO_RM_FILE_EXIT_CODE=$?
        echo "$SUDO_RM_FILE_OUTPUT" | tee -a "$LOG_FILE_NAME"
        if [ $SUDO_RM_FILE_EXIT_CODE -eq 0 ]; then
            log_message "File '$INSTALL_LINK_NAME' removed successfully."
        else
            log_message "Error: Failed to remove file '$INSTALL_LINK_NAME'. Exit code: $SUDO_RM_FILE_EXIT_CODE."
        fi
    else
        log_message "Skipping removal of file '$INSTALL_LINK_NAME'."
    fi
else
    log_message "No symbolic link or file found at '$INSTALL_LINK_NAME'. Nothing to remove from target directory."
fi

# --- 2. Optionally Clean Up Build Artifacts ---
log_message ""
log_message "-----------------------------------------------------"
log_message " Step 2: Clean Up Build Artifacts (Optional)"
log_message "-----------------------------------------------------"

ARTIFACTS_TO_CLEAN=()
# Check for PYINSTALLER_APP_NAME specific dist/build folders first, then generic ones
PYINSTALLER_DIST_SUBDIR="$DIST_DIR/$PYINSTALLER_APP_NAME"
PYINSTALLER_BUILD_SUBDIR="$BUILD_DIR/$PYINSTALLER_APP_NAME"

if [ -d "$DIST_DIR" ]; then ARTIFACTS_TO_CLEAN+=("$DIST_DIR"); fi
if [ -d "$BUILD_DIR" ]; then ARTIFACTS_TO_CLEAN+=("$BUILD_DIR"); fi
if [ -f "$SPEC_FILE_PATH" ]; then ARTIFACTS_TO_CLEAN+=("$SPEC_FILE_PATH"); fi

if [ ${#ARTIFACTS_TO_CLEAN[@]} -gt 0 ]; then
    log_message "The following build artifacts were found in your project directory ($PROJECT_ROOT):"
    for item in "${ARTIFACTS_TO_CLEAN[@]}"; do
        # Show path relative to project root for clarity
        log_message "  - ${item#"$PROJECT_ROOT/"}"
    done
    log_message "" # Blank line
    read -r -p "Do you want to remove these build artifacts? (yes/no): " yn_artifacts >&2
    if [[ "$yn_artifacts" =~ ^[Yy](es)?$ ]]; then
        log_message "User confirmed. Removing build artifacts..."
        CLEANUP_SUCCESS=true
        for item in "${ARTIFACTS_TO_CLEAN[@]}"; do
            log_message "  Removing '${item#"$PROJECT_ROOT/"}'..."
            RM_OUTPUT=$(rm -rf "$item" 2>&1) # Capture rm output
            RM_EXIT_CODE=$?
            if [ $RM_EXIT_CODE -eq 0 ]; then
                # If rm was successful and produced output (e.g. verbose mode if enabled, though unlikely for -rf), log it.
                if [ -n "$RM_OUTPUT" ]; then echo "$RM_OUTPUT" | tee -a "$LOG_FILE_NAME"; fi
                log_message "    Removed '${item#"$PROJECT_ROOT/"}'."
            else
                echo "$RM_OUTPUT" | tee -a "$LOG_FILE_NAME" # Log error output from rm
                log_message "    Error: Failed to remove '${item#"$PROJECT_ROOT/"}'. Exit code: $RM_EXIT_CODE."
                CLEANUP_SUCCESS=false
            fi
        done
        if $CLEANUP_SUCCESS; then
            log_message "Build artifacts cleaned up successfully."
        else
            log_message "Some errors occurred during artifact cleanup. Please check above."
        fi
    else
        log_message "Skipping removal of build artifacts."
    fi
else
    log_message "No common build artifacts (dist, build, .spec file for '$PYINSTALLER_APP_NAME') found in '$PROJECT_ROOT'."
fi

log_message ""
log_message "-----------------------------------------------------"
log_message " $APP_NAME_FRIENDLY uninstallation process complete."
log_message "-----------------------------------------------------"
log_message "Uninstall script finished at $(date)"
exit 0
