import os
import sys
import shutil
import stat
import subprocess
from pathlib import Path
import click

__version__ = "1.2.0"
__author__ = "PlayWitIt"
__description__ = "A tool to initialize a Python project with robust helper scripts"


def get_template_dir() -> Path:
    """
    Finds the bundled template directory, whether running from source
    or from a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
        template_dir = base_path / 'templates'
    else:
        base_path = Path(__file__).resolve().parent
        template_dir = base_path / 'templates'
    
    if not template_dir.exists():
        raise FileNotFoundError(f"FATAL: Template directory not found at {template_dir}")
        
    return template_dir


def find_venv() -> Path | None:
    """Find existing virtual environment (.venv or venv)."""
    if Path(".venv").exists():
        return Path(".venv")
    if Path("venv").exists():
        return Path("venv")
    return None


def find_python_script(preferred: list[str] = None) -> Path | None:
    """Find a Python script to run."""
    if preferred:
        for name in preferred:
            p = Path(name)
            if p.exists():
                return p
    
    # Find all .py files in current dir and subdirs
    py_files = sorted(Path('.').glob('**/*.py'))
    # Filter out venv directories
    py_files = [f for f in py_files if '.venv' not in str(f) and '/venv/' not in str(f)]
    
    if py_files:
        return py_files[0]
    return None


def copy_script(source_file: Path, dest_file: Path, force: bool = False) -> bool:
    """Copy a script and make it executable. Returns True if copied, False if skipped."""
    if not source_file.exists():
        click.secho(f"  - Warning: Template file '{source_file.name}' not found in bundle.", fg='yellow')
        return False

    if dest_file.exists():
        if not force:
            if not click.confirm(f"  - '{dest_file.name}' already exists. Overwrite?"):
                click.echo(f"    -> Skipped '{dest_file.name}'.")
                return False
        else:
            click.echo(f"  - Overwriting existing '{dest_file.name}' (--force)")
    
    shutil.copy(source_file, dest_file)
    
    current_mode = os.stat(dest_file).st_mode
    os.chmod(dest_file, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    click.secho(f"  - Created and made executable: {dest_file.name}", fg='green')
    return True


@click.group()
@click.version_option(version=__version__, prog_name="pybs")
def cli():
    """pybootstrap: A tool to initialize a Python project with helper scripts."""
    pass


@cli.command()
@click.option('--dir', 'directory', default=None, type=click.Path(),
              help="Create and initialize in a new directory. Defaults to the current directory.")
@click.option('--force', '-f', is_flag=True, help="Overwrite existing scripts without prompting.")
def init(directory, force):
    """Initialize a project with both py_bootstrap.sh and Run.sh."""
    
    target_path = Path.cwd()
    if directory:
        target_path = target_path / directory
        if target_path.exists() and not target_path.is_dir():
            click.secho(f"Error: '{target_path}' exists and is not a directory.", fg='red')
            sys.exit(1)
        target_path.mkdir(exist_ok=True)
        click.echo(f"Working inside new directory: {target_path}")
    else:
        click.echo(f"Working inside current directory: {target_path}")

    try:
        template_dir = get_template_dir()
        
        click.echo("Creating helper scripts...")
        
        copy_script(template_dir / "Run.sh", target_path / "Run.sh", force)
        copy_script(template_dir / "py_bootstrap.sh", target_path / "py_bootstrap.sh", force)

        click.echo("\n" + "="*50)
        click.secho("Initialization complete!", fg='green', bold=True)
        click.echo("="*50)
        click.echo("\nNext steps:")
        if directory:
             click.echo(f"1. cd {directory}")
        click.echo("2. Create your requirements.txt with your dependencies")
        click.echo("3. Run: ./py_bootstrap.sh")
        click.echo("4. Run: ./Run.sh")

    except Exception as e:
        click.secho(f"\nAn error occurred: {e}", fg='red')
        sys.exit(1)


@cli.command()
@click.option('--dir', 'directory', default=None, type=click.Path(),
              help="Create and initialize in a new directory. Defaults to the current directory.")
@click.option('--force', '-f', is_flag=True, help="Overwrite existing scripts without prompting.")
def bootstrap(directory, force):
    """Create only the py_bootstrap.sh script (for environment setup)."""
    
    target_path = Path.cwd()
    if directory:
        target_path = target_path / directory
        if target_path.exists() and not target_path.is_dir():
            click.secho(f"Error: '{target_path}' exists and is not a directory.", fg='red')
            sys.exit(1)
        target_path.mkdir(exist_ok=True)
        click.echo(f"Working inside new directory: {target_path}")
    else:
        click.echo(f"Working inside current directory: {target_path}")

    try:
        template_dir = get_template_dir()
        
        click.echo("Creating py_bootstrap.sh...")
        
        copy_script(template_dir / "py_bootstrap.sh", target_path / "py_bootstrap.sh", force)

        click.echo("\n" + "="*50)
        click.secho("Bootstrap script created!", fg='green', bold=True)
        click.echo("="*50)
        click.echo("\nNext steps:")
        if directory:
             click.echo(f"1. cd {directory}")
        click.echo("2. Create your requirements.txt with your dependencies")
        click.echo("3. Run: ./py_bootstrap.sh")

    except Exception as e:
        click.secho(f"\nAn error occurred: {e}", fg='red')
        sys.exit(1)


@cli.command()
@click.option('--dir', 'directory', default=None, type=click.Path(),
              help="Create and initialize in a new directory. Defaults to the current directory.")
@click.option('--force', '-f', is_flag=True, help="Overwrite existing scripts without prompting.")
def run(directory, force):
    """Create only the Run.sh script (for running Python scripts)."""
    
    target_path = Path.cwd()
    if directory:
        target_path = target_path / directory
        if target_path.exists() and not target_path.is_dir():
            click.secho(f"Error: '{target_path}' exists and is not a directory.", fg='red')
            sys.exit(1)
        target_path.mkdir(exist_ok=True)
        click.echo(f"Working inside new directory: {target_path}")
    else:
        click.echo(f"Working inside current directory: {target_path}")

    try:
        template_dir = get_template_dir()
        
        click.echo("Creating Run.sh...")
        
        copy_script(template_dir / "Run.sh", target_path / "Run.sh", force)

        click.echo("\n" + "="*50)
        click.secho("Run script created!", fg='green', bold=True)
        click.echo("="*50)
        click.echo("\nNext steps:")
        if directory:
             click.echo(f"1. cd {directory}")
        click.echo("2. Run: ./Run.sh")

    except Exception as e:
        click.secho(f"\nAn error occurred: {e}", fg='red')
        sys.exit(1)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('script', required=False)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--no-venv', is_flag=True, help="Use system Python instead of venv.")
def exec(script, args, no_venv):
    """Run a Python script directly without needing Run.sh.
    
    Example: pybs exec myscript.py --arg1 value
    """
    target_path = Path.cwd()
    
    # Find Python script
    script_path = None
    if script:
        script_path = Path(script)
        if not script_path.exists():
            click.secho(f"Error: Script '{script}' not found.", fg='red')
            sys.exit(1)
    else:
        script_path = find_python_script(['main.py', 'app.py', 'myapp.py'])
        if not script_path:
            click.secho("Error: No Python script found. Specify one or create main.py", fg='red')
            sys.exit(1)
    
    click.echo(f"Running: {script_path}")
    
    # Find or create venv
    venv_path = None
    if not no_venv:
        venv_path = find_venv()
    
    python_exe = None
    if venv_path:
        venv_python = venv_path / 'bin' / 'python'
        if venv_python.exists():
            python_exe = str(venv_python)
            click.echo(f"Using venv: {venv_path}")
    
    if not python_exe:
        python_exe = 'python3'
        click.echo("Using system Python")
    
    # Run the script
    try:
        result = subprocess.run(
            [python_exe, str(script_path)] + list(args),
            cwd=target_path
        )
        sys.exit(result.returncode)
    except Exception as e:
        click.secho(f"Error running script: {e}", fg='red')
        sys.exit(1)


# Shell completions
def bash_complete( incompletions, command, point ):
    """Generate bash completions."""
    # This would be enhanced with proper click completion
    pass


if __name__ == '__main__':
    cli()