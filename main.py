import os
import sys
import shutil
import stat
from pathlib import Path
import click

from version import __version__, __author__, __description__


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


@click.group()
@click.version_option(version=__version__, prog_name="pybs")
def cli():
    """pybootstrap: A tool to initialize a Python project with helper scripts."""
    pass


@cli.command()
@click.option('--dir', 'directory', default=None, type=click.Path(),
              help="Create and initialize in a new directory. Defaults to the current directory.")
@click.option('--no-git', is_flag=True, help="Skip Git repository initialization prompt.")
@click.option('--no-run', is_flag=True, help="Only generate py_bootstrap.sh, skip Run.sh.")
def init(directory, no_git, no_run):
    """Initializes a project with py_bootstrap.sh and Run.sh."""
    
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
        files_to_copy = []
        
        if not no_run:
            files_to_copy.append("Run.sh")
        files_to_copy.append("py_bootstrap.sh")
        
        click.echo("Creating helper scripts...")
        
        for filename in files_to_copy:
            source_file = template_dir / filename
            dest_file = target_path / filename

            if not source_file.exists():
                click.secho(f"  - Warning: Template file '{filename}' not found in bundle. Skipping.", fg='yellow')
                continue

            if dest_file.exists():
                if not click.confirm(f"  - '{filename}' already exists. Overwrite?"):
                    click.echo(f"    -> Skipped '{filename}'.")
                    continue
            
            shutil.copy(source_file, dest_file)
            
            current_mode = os.stat(dest_file).st_mode
            os.chmod(dest_file, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            click.secho(f"  - Created and made executable: {dest_file.name}", fg='green')

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


if __name__ == '__main__':
    cli()
