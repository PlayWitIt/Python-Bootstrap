#!/bin/bash

# --- Configuration (SHOULD MATCH YOUR INSTALLER SCRIPT) ---
APP_NAME_FRIENDLY="PyBootstrap Tool"
PYINSTALLER_APP_NAME="pybs_executable"
COMMAND_NAME="pybs"
# --- End Configuration ---

# --- Log File Setup ---
LOG_FILE_SANITIZED_APP_NAME=$(echo "$PYINSTALLER_APP_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE_NAME="uninstall_${LOG_FILE_SANITIZED_APP_NAME}.log"

log_message() {
    echo "$@" | tee -a "$LOG_FILE_NAME"
}

echo "Uninstall script started at $(date)" > "$LOG_FILE_NAME"
log_message "Logging to: $PWD/$LOG_FILE_NAME"
log_message "-----------------------------------------------------"

log_message "Attempting to uninstall $APP_NAME_FRIENDLY ($COMMAND_NAME command)..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

INSTALL_TARGET_DIR="/usr/local/bin"
INSTALL_LINK_NAME="$INSTALL_TARGET_DIR/$COMMAND_NAME"

DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"
SPEC_FILE_NAME="${PYINSTALLER_APP_NAME}.spec"
SPEC_FILE_PATH="$PROJECT_ROOT/$SPEC_FILE_NAME"

REMOVED_SOMETHING=false

# --- 1. Find and remove the command from anywhere in PATH ---
log_message ""
log_message "-----------------------------------------------------"
log_message " Step 1: Finding and removing $COMMAND_NAME from system"
log_message "-----------------------------------------------------"

CMD_PATH=$(which "$COMMAND_NAME" 2>/dev/null || type -p "$COMMAND_NAME" 2>/dev/null || echo "")

if [ -n "$CMD_PATH" ]; then
    log_message "Found $COMMAND_NAME at: $CMD_PATH"
    
    if [[ "$CMD_PATH" == *"pyenv"*"/shims/"* ]]; then
        log_message "Detected pyenv shim. Removing the binary..."
        ACTUAL_BIN=$(pyenv which "$COMMAND_NAME" 2>/dev/null || echo "")
        if [ -n "$ACTUAL_BIN" ] && [ -f "$ACTUAL_BIN" ]; then
            log_message "Removing pyenv binary: $ACTUAL_BIN"
            rm -f "$ACTUAL_BIN"
            [ $? -eq 0 ] && REMOVED_SOMETHING=true
        fi
        log_message "Removing pyenv shim: $CMD_PATH"
        rm -f "$CMD_PATH"
        [ $? -eq 0 ] && REMOVED_SOMETHING=true
    elif [[ "$CMD_PATH" == "$HOME/.local/bin/"* ]]; then
        log_message "Removing from ~/.local/bin: $CMD_PATH"
        rm -f "$CMD_PATH"
        [ $? -eq 0 ] && REMOVED_SOMETHING=true
    elif [[ "$CMD_PATH" == "$INSTALL_TARGET_DIR"* ]]; then
        log_message "Removing from $INSTALL_TARGET_DIR: $CMD_PATH"
        sudo rm -f "$CMD_PATH"
        [ $? -eq 0 ] && REMOVED_SOMETHING=true
    else
        log_message "Removing from $CMD_PATH"
        sudo rm -f "$CMD_PATH"
        [ $? -eq 0 ] && REMOVED_SOMETHING=true
    fi
else
    log_message "$COMMAND_NAME not found in PATH"
fi

if [ -L "$INSTALL_LINK_NAME" ] || [ -f "$INSTALL_LINK_NAME" ]; then
    log_message "Removing symlink at $INSTALL_LINK_NAME"
    sudo rm -f "$INSTALL_LINK_NAME"
    [ $? -eq 0 ] && REMOVED_SOMETHING=true
fi

# --- 2. Clean Up Build Artifacts ---
log_message ""
log_message "-----------------------------------------------------"
log_message " Step 2: Cleaning up build artifacts"
log_message "-----------------------------------------------------"

ARTIFACTS_TO_CLEAN=()

[ -d "$DIST_DIR" ] && ARTIFACTS_TO_CLEAN+=("$DIST_DIR")
[ -d "$BUILD_DIR" ] && ARTIFACTS_TO_CLEAN+=("$BUILD_DIR")
[ -f "$SPEC_FILE_PATH" ] && ARTIFACTS_TO_CLEAN+=("$SPEC_FILE_PATH")

if [ ${#ARTIFACTS_TO_CLEAN[@]} -gt 0 ]; then
    for item in "${ARTIFACTS_TO_CLEAN[@]}"; do
        log_message "Removing '$item'..."
        rm -rf "$item"
        [ $? -eq 0 ] && REMOVED_SOMETHING=true
    done
else
    log_message "No build artifacts found in project directory"
fi

log_message ""
log_message "-----------------------------------------------------"
if $REMOVED_SOMETHING; then
    log_message " $APP_NAME_FRIENDLY uninstallation complete."
else
    log_message " $APP_NAME_FRIENDLY was not found or already removed."
fi
log_message "-----------------------------------------------------"
log_message "Uninstall script finished at $(date)"
exit 0
