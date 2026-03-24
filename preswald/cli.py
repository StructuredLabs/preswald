import os
import sys

import click


@click.group()
@click.version_option()
def cli():
    """
    Preswald CLI - Write Python. Export HTML. Share anywhere.
    """
    pass


def _create_default_init_files(target_dir: str, project_slug: str):
    """Create default project files in the target directory using templates."""
    from importlib.resources import as_file, files

    # Read and write hello.py from template
    with as_file(files("preswald").joinpath("templates/hello.py.template")) as path:
        with open(path) as f:
            hello_content = f.read()
        with open(os.path.join(target_dir, "hello.py"), "w") as f:
            f.write(hello_content)

    # Read and write preswald.toml from template
    with as_file(
        files("preswald").joinpath("templates/preswald.toml.template")
    ) as path:
        with open(path) as f:
            toml_content = f.read().format(project_slug=project_slug)
        with open(os.path.join(target_dir, "preswald.toml"), "w") as f:
            f.write(toml_content)

    # Read and write secrets.toml from template
    with as_file(files("preswald").joinpath("templates/secrets.toml.template")) as path:
        with open(path) as f:
            secrets_content = f.read()
        with open(os.path.join(target_dir, "secrets.toml"), "w") as f:
            f.write(secrets_content)

    # Read and write sample.csv from template
    with as_file(files("preswald").joinpath("templates/sample.csv.template")) as path:
        with open(path) as f:
            sample_data = f.read()
        with open(os.path.join(target_dir, "data", "sample.csv"), "w") as f:
            f.write(sample_data)


@cli.command()
@click.argument("name", default="preswald_project")
def init(name):
    """
    Initialize a new Preswald project.
    Creates a directory with basic project structure.
    """
    from preswald.utils import generate_slug

    try:
        os.makedirs(name, exist_ok=True)
        os.makedirs(os.path.join(name, "images"), exist_ok=True)
        os.makedirs(os.path.join(name, "data"), exist_ok=True)

        # Generate a unique slug for the project
        project_slug = generate_slug(name)

        # Copy default branding files
        import shutil
        from importlib.resources import as_file, files

        with as_file(files("preswald").joinpath("static/favicon.ico")) as path:
            shutil.copy2(path, os.path.join(name, "images", "favicon.ico"))

        with as_file(files("preswald").joinpath("static/logo.png")) as path:
            shutil.copy2(path, os.path.join(name, "images", "logo.png"))

        # Create basic project files
        _create_default_init_files(name, project_slug)

        click.echo(f"Initialized a new Preswald project in '{name}/'")
        click.echo(f"Project slug: {project_slug}")
    except Exception as e:
        click.echo(f"Error initializing project: {e}")


def _resolve_script(script_arg):
    """Resolve the script path, checking preswald.toml if no script argument given.

    Returns (script_path, config_path_or_none) or calls sys.exit on failure.
    """
    import tomli

    # If a script argument is provided directly, use it
    if script_arg:
        if not os.path.exists(script_arg):
            click.echo(f"Error: Script '{script_arg}' not found.")
            sys.exit(1)
        # Check for preswald.toml in the script's directory (optional)
        script_dir = os.path.dirname(os.path.abspath(script_arg))
        config_path = os.path.join(script_dir, "preswald.toml")
        return script_arg, config_path if os.path.exists(config_path) else None

    # No script arg -- look for preswald.toml in current directory
    config_path = "preswald.toml"
    if not os.path.exists(config_path):
        click.echo("Error: No script specified and no preswald.toml found.")
        click.echo("Usage: preswald dev <script.py>  or  run from a project directory.")
        sys.exit(1)

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
    except Exception as e:
        click.echo(f"Error reading preswald.toml: {e}")
        sys.exit(1)

    if "project" not in config or "entrypoint" not in config["project"]:
        click.echo(
            "Error: entrypoint not defined in preswald.toml under [project] section."
        )
        sys.exit(1)

    script = config["project"]["entrypoint"]
    if not os.path.exists(script):
        click.echo(f"Error: Entrypoint script '{script}' not found.")
        sys.exit(1)

    return script, config_path


@cli.command()
@click.argument("script", default=None, required=False)
@click.option("--port", default=8501, help="Port to run the server on.")
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default=None,
    help="Set the logging level (overrides config file)",
)
@click.option(
    "--disable-new-tab",
    is_flag=True,
    default=False,
    help="Disable automatically opening a new browser tab",
)
def dev(script, port, log_level, disable_new_tab):
    """
    Run a Preswald app in development mode.

    You can either pass a script directly (preswald dev app.py) or run from a
    project directory containing preswald.toml.
    """
    from preswald.main import start_server
    from preswald.utils import configure_logging, read_port_from_config

    script_path, config_path = _resolve_script(script)

    if config_path:
        log_level = configure_logging(config_path=config_path, level=log_level)
        port = read_port_from_config(config_path=config_path, port=port)

    url = f"http://localhost:{port}"
    click.echo(f"Running '{script_path}' on {url}")

    try:
        if not disable_new_tab:
            import webbrowser

            webbrowser.open(url)

        start_server(script=script_path, port=port)

    except Exception as e:
        click.echo(f"Error: {e}")


# Keep 'run' as an alias for backwards compatibility
@cli.command()
@click.option("--port", default=8501, help="Port to run the server on.")
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default=None,
    help="Set the logging level (overrides config file)",
)
@click.option(
    "--disable-new-tab",
    is_flag=True,
    default=False,
    help="Disable automatically opening a new browser tab",
)
def run(port, log_level, disable_new_tab):
    """
    Run a Preswald app (alias for 'dev').

    Looks for preswald.toml in the current directory and runs the script specified in the entrypoint.
    """
    from preswald.main import start_server
    from preswald.utils import configure_logging, read_port_from_config

    script_path, config_path = _resolve_script(None)

    if config_path:
        log_level = configure_logging(config_path=config_path, level=log_level)
        port = read_port_from_config(config_path=config_path, port=port)

    url = f"http://localhost:{port}"
    click.echo(f"Running '{script_path}' on {url}")

    try:
        if not disable_new_tab:
            import webbrowser

            webbrowser.open(url)

        start_server(script=script_path, port=port)

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.pass_context
def tutorial(ctx):
    """
    Run the Preswald tutorial app.

    This command runs the tutorial app located in the package's tutorial directory.
    """
    import preswald

    package_dir = os.path.dirname(preswald.__file__)
    tutorial_dir = os.path.join(package_dir, "tutorial")

    if not os.path.exists(tutorial_dir):
        click.echo(f"Error: Tutorial directory '{tutorial_dir}' not found.")
        click.echo("The tutorial files may be missing from your installation.")
        return

    click.echo("Launching the Preswald tutorial app!")

    # Save current directory
    current_dir = os.getcwd()
    try:
        # Change to tutorial directory
        os.chdir(tutorial_dir)
        # Invoke the 'run' command from the tutorial directory
        ctx.invoke(run, port=8501)
    finally:
        # Change back to original directory
        os.chdir(current_dir)


@cli.command()
@click.argument("script", default=None, required=False)
@click.option(
    "--format",
    type=click.Choice(["pdf", "html"]),
    required=True,
    help="Export format - pdf creates a static report, html creates an interactive web app",
)
@click.option("--output", type=click.Path(), help="Path to the output directory")
@click.option(
    "--client",
    type=click.Choice(["auto", "websocket", "postmessage", "comlink"]),
    default="comlink",
    help="Communication client to use - auto will choose based on context",
)
def export(script, format, output, client):
    """Export the current Preswald app as a PDF report or HTML app."""
    import tomli

    script_path, config_path = _resolve_script(script)

    if format == "pdf":
        output_path = output or "preswald_report.pdf"
        click.echo(f"Rendering '{script_path}'...")

        from preswald.main import render_once
        from preswald.utils import export_app_to_pdf

        layout = render_once(script_path)

        click.echo(
            f"Render complete. Found {len(layout['rows'])} rows of components."
        )

        component_ids = []
        for row in layout["rows"]:
            for component in row:
                cid = component.get("id")
                ctype = component.get("type")
                if cid and ctype:
                    component_ids.append({"id": cid, "type": ctype})

        # Pass the component IDs to the export function
        export_app_to_pdf(component_ids, output_path)

        click.echo(f"\nExport complete. PDF saved to: {output_path}")

    elif format == "html":
        # Create output directory
        output_dir = output or "preswald_export"

        click.echo(f"Exporting '{script_path}' to HTML...")

        try:
            from preswald.utils import (
                prepare_html_export,
            )

            # Determine project root from script location
            project_root = os.path.dirname(os.path.abspath(script_path)) if not config_path else "."

            prepare_html_export(
                script_path=script_path,
                output_dir=output_dir,
                project_root_dir=project_root,
                client_type=client,
            )

            click.echo(f"""
Export complete! Your interactive HTML app is ready:

   {output_dir}/
      index.html           # The main HTML file
      project_fs.json      # Your project files
      assets/             # Required JavaScript and CSS

Note: The app needs to be served via HTTP server - opening index.html directly won't work.
""")

        except Exception as e:
            click.echo(f"Export failed: {e!s}")
            return


if __name__ == "__main__":
    cli()
