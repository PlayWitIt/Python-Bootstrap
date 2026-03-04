# Contributing to PyBootstrap

Thank you for your interest in contributing to PyBootstrap!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/PlayWitIt/Python-Bootstrap.git
   cd Python-Bootstrap
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest
```

## Code Style

This project uses:
- **Black** for Python formatting
- **Ruff** for Python linting
- **ShellCheck** for bash scripts

Format code:
```bash
black .
ruff check . --fix
```

## Building

```bash
./build_and_install.sh
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Bugs

Please open an issue at: https://github.com/PlayWitIt/Python-Bootstrap/issues
