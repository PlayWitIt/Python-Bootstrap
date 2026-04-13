# Development Notes

## Version Bumping & Publishing to PyPI

When you make changes and want to publish a new version:

### Option 1: Use bump_version.sh (Recommended)

```bash
cd /home/play/Code/Published/PythonBootstraper

# Run the version bump script - it will prompt for new version
./bump_version.sh
```

This updates:
- `pyproject.toml`
- `PythonBootstraper/version.py`
- `PythonBootstraper/main.py` (fallback)

Then continue with build steps below.

---

### Option 2: Manual Bump

If you prefer manual control:

```bash
cd /home/play/Code/Published/PythonBootstraper

# 1. Update version in these 3 files (keep them in sync!):
#    - pyproject.toml (line: version = "X.Y.Z")
#    - PythonBootstraper/version.py (line: __version__ = "X.Y.Z")
#    - PythonBootstraper/main.py (line: __version__ = "X.Y.Z" in fallback)

# Use sed to update all at once:
NEW_VERSION="1.2.3"
sed -i "s/__version__ = \".[^\"]*\"/__version__ = \"$NEW_VERSION\"/" PythonBootstraper/version.py PythonBootstraper/main.py
sed -i "s/version = \".[^\"]*\"/version = \"$NEW_VERSION\"/" pyproject.toml
```

---

### Build & Publish (after version bump)

```bash
# 2. Build PyInstaller binary (for testing)
rm -rf build dist
pyinstaller --noconfirm pybs.spec

# 3. Test the binary
./dist/pybs --version

# 4. Build package for PyPI
rm -rf dist/*
python -m build --sdist --wheel

# 5. Verify package
python -m twine check dist/*

# 6. Upload to PyPI (get token from pypi.org)
# Token: pypi-AgEIcHlwaS5vcmcC...
TWINE_USERNAME=__token__ TWINE_PASSWORD="YOUR_TOKEN_HERE" twine upload dist/*

# 7. Install and verify on this machine
pip install --upgrade --force-reinstall PythonBootstraper
pybs --version
```

---

## PyPI Token

Get from: https://pypi.org/manage/account/

Create a new token with scope "Upload packages" and save it securely.

---

## Git Workflow

```bash
# After making changes and before publishing:
git add -A
git commit -m "Description of changes"
git push
```

---

## Build & Publish (Complete Steps)

After committing changes, run these commands in order:

```bash
# 1. Navigate to project
cd /home/play/Code/Published/PythonBootstraper

# 2. Clean previous builds
rm -rf build dist

# 3. Build PyInstaller binary
pyinstaller --noconfirm pybs.spec

# 4. Test the binary works
./dist/pybs --version

# 5. Build package for PyPI (sdist + wheel)
python -m build --sdist --wheel

# 6. Verify package is valid
python -m twine check dist/*

# 7. Upload to PyPI (get token from https://pypi.org/manage/account/)
# Replace YOUR_TOKEN with your actual token from PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD="YOUR_TOKEN" twine upload dist/*

# 8. Verify installation on this machine
pip install --upgrade --force-reinstall PythonBootstraper
pybs --version
```

That's it! The new version is now live on PyPI.