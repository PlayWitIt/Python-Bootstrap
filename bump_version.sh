#!/bin/bash
# Build script - only updates files that need version bump

OLD_VERSION=$(grep 'version = "' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $OLD_VERSION"

read -p "Enter new version: " NEW_VERSION

# Update pyproject.toml
sed -i "s/version = \"$OLD_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update version.py
sed -i "s/__version__ = \"$OLD_VERSION\"/__version__ = \"$NEW_VERSION\"/" PythonBootstraper/version.py

# Update main.py (backup if different)
CURRENT_MAIN=$(grep '__version__ = "' PythonBootstraper/main.py | head -1 | sed 's/__version__ = "\(.*\)"/\1/')
if [ "$CURRENT_MAIN" != "$NEW_VERSION" ]; then
    sed -i "s/__version__ = \"$CURRENT_MAIN\"/__version__ = \"$NEW_VERSION\"/" PythonBootstraper/main.py
fi

echo "Updated to $NEW_VERSION"
echo ""
echo "Now run:"
echo "  1. pyinstaller --noconfirm pybs.spec"
echo "  2. python -m build --sdist --wheel"
echo "  3. twine upload dist/*"