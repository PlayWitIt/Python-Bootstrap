import os
import sys
import shutil
import stat
from pathlib import Path
import click

__version__ = "1.1.2"
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


def copy_script(source_file: Path, dest_file: Path) -> bool:
    """Copy a script and make it executable. Returns True if copied, False if skipped."""
    if not source_file.exists():
        click.secho(f"  - Warning: Template file '{source_file.name}' not found in bundle.", fg='yellow')
        return False

    if dest_file.exists():
        if not click.confirm(f"  - '{dest_file.name}' already exists. Overwrite?"):
            click.echo(f"    -> Skipped '{dest_file.name}'.")
            return False
    
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
def init(directory):
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
        
        copy_script(template_dir / "Run.sh", target_path / "Run.sh")
        copy_script(template_dir / "py_bootstrap.sh", target_path / "py_bootstrap.sh")

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
def bootstrap(directory):
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
        
        copy_script(template_dir / "py_bootstrap.sh", target_path / "py_bootstrap.sh")

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
def run(directory):
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
        
        copy_script(template_dir / "Run.sh", target_path / "Run.sh")

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


if __name__ == '__main__':
    cli()