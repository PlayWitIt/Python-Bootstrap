import os
import sys
import shutil
import stat
from pathlib import Path
import click

def get_template_dir() -> Path:
    """
    Finds the bundled template directory, whether running from source
    or from a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False):
        # We are running in a bundle (packaged by PyInstaller).
        # The templates are in a folder named 'templates' next to the executable.
        base_path = Path(sys._MEIPASS)
        template_dir = base_path / 'templates'
    else:
        # We are running in a normal Python environment.
        base_path = Path(__file__).resolve().parent
        template_dir = base_path / 'templates'
    
    if not template_dir.exists():
        raise FileNotFoundError(f"FATAL: Template directory not found at {template_dir}")
        
    return template_dir

@click.group()
def cli():
    """pybootstrap: A tool to initialize a Python project with helper scripts."""
    pass

@cli.command()
@click.option('--dir', 'directory', default=None, type=click.Path(),
              help="Create and initialize in a new directory. Defaults to the current directory.")
def init(directory):
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
        files_to_copy = ["py_bootstrap.sh", "Run.sh"]
        
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
            
            # Make the script executable for the user, group, and others
            current_mode = os.stat(dest_file).st_mode
            os.chmod(dest_file, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            click.secho(f"  - Created and made executable: {dest_file.name}", fg='green')

        click.echo("\n✅ Initialization complete!")
        click.echo("\nNext steps:")
        if directory:
             click.echo(f"1. Navigate into your project: cd {directory}")
        click.echo("2. Set up your Python environment by running: ./py_bootstrap.sh")
        click.echo("3. Create your main python file (e.g., main.py, app.py).")
        click.echo("4. Run your application using: ./Run.sh")

    except Exception as e:
        click.secho(f"\nAn error occurred: {e}", fg='red')
        sys.exit(1)


if __name__ == '__main__':
    cli()
