import os
import sys
import tempfile

import click

from preswald.engine.telemetry import TelemetryService


# Create a temporary directory for IPC
TEMP_DIR = os.path.join(tempfile.gettempdir(), "preswald")
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize telemetry service
telemetry = TelemetryService()


@click.group()
@click.version_option()
def cli():
    """
    Preswald CLI - A lightweight framework for interactive data apps.
    """
    pass


@cli.command()
@click.argument("name", default="preswald_project")
def init(name):
    """
    Initialize a new Preswald project.

    This creates a directory with boilerplate files like `hello.py` and `preswald.toml`.
    """
    from preswald.utils import generate_slug, read_template

    try:
        os.makedirs(name, exist_ok=True)
        os.makedirs(os.path.join(name, "images"), exist_ok=True)
        os.makedirs(os.path.join(name, "data"), exist_ok=True)

        # Generate a unique slug for the project
        project_slug = generate_slug(name)

        # Copy default branding files from package resources
        import shutil
        from importlib.resources import as_file, files

        # Using a context manager to get the actual file path
        with as_file(files("preswald").joinpath("static/favicon.ico")) as path:
            shutil.copy2(path, os.path.join(name, "images", "favicon.ico"))

        with as_file(files("preswald").joinpath("static/logo.png")) as path:
            shutil.copy2(path, os.path.join(name, "images", "logo.png"))

        file_templates = {
            "hello.py": "hello.py",
            "preswald.toml": "preswald.toml",
            "secrets.toml": "secrets.toml",
            ".gitignore": "gitignore",
            "workbook.md": "workbook.md",
            "pyproject.toml": "pyproject.toml",
            "data/sample.csv": "sample.csv",
        }

        for file_name, template_name in file_templates.items():
            content = read_template(template_name)

            # Replace the default slug in preswald.toml with the generated one
            if file_name == "preswald.toml":
                content = content.replace(
                    'slug = "preswald-project"', f'slug = "{project_slug}"'
                )

            with open(os.path.join(name, file_name), "w") as f:
                f.write(content)

        # Track initialization
        telemetry.track_command(
            "init", {"project_name": name, "project_slug": project_slug}
        )

        click.echo(f"Initialized a new Preswald project in '{name}/' 🎉!")
        click.echo(f"Project slug: {project_slug}")
    except Exception as e:
        click.echo(f"Error initializing project: {e} ❌")


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
    Run a Preswald app from the current directory.

    Looks for preswald.toml in the current directory and runs the script specified in the entrypoint.
    """
    config_path = "preswald.toml"
    if not os.path.exists(config_path):
        click.echo("Error: preswald.toml not found in current directory. ❌")
        click.echo("Make sure you're in a Preswald project directory.")
        return

    import tomli

    from preswald.main import start_server
    from preswald.utils import configure_logging, read_port_from_config

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
    except Exception as e:
        click.echo(f"Error reading preswald.toml: {e} ❌")
        return

    if "project" not in config or "entrypoint" not in config["project"]:
        click.echo(
            "Error: entrypoint not defined in preswald.toml under [project] section. ❌"
        )
        return

    script = config["project"]["entrypoint"]
    if not os.path.exists(script):
        click.echo(f"Error: Entrypoint script '{script}' not found. ❌")
        return

    log_level = configure_logging(config_path=config_path, level=log_level)
    port = read_port_from_config(config_path=config_path, port=port)

    # Track run command
    telemetry.track_command(
        "run",
        {
            "script": script,
            "port": port,
            "log_level": log_level,
            "disable_new_tab": disable_new_tab,
        },
    )

    url = f"http://localhost:{port}"
    click.echo(f"Running '{script}' on {url} with log level {log_level}  🎉!")

    try:
        if not disable_new_tab:
            import webbrowser

            webbrowser.open(url)

        start_server(script=script, port=port)

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("script", default=None, required=False)
@click.option(
    "--target",
    type=click.Choice(["local", "gcp", "aws", "structured"], case_sensitive=False),
    default="local",
    help="Target platform for deployment.",
)
@click.option("--port", default=8501, help="Port for deployment.")
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default=None,
    help="Set the logging level (overrides config file)",
)
@click.option(
    "--github",
    help="GitHub username for structured deployment",
)
@click.option(
    "--api-key",
    help="Structured Cloud API key for structured deployment",
)
def deploy(script, target, port, log_level, github, api_key):  # noqa: C901
    """
    Deploy your Preswald app.

    This allows you to share the app within your local network or deploy to production.
    If no script is provided, it will use the entrypoint defined in preswald.toml.
    """
    try:
        if target == "aws":
            click.echo(
                "\nWe're working on supporting AWS soon! Please enjoy some ☕ and 🍌 in the meantime"
            )
            return

        # First try to read from preswald.toml in current directory
        config_path = "preswald.toml"
        if os.path.exists(config_path):
            import tomli

            try:
                with open(config_path, "rb") as f:
                    config = tomli.load(f)
                if "project" in config and "entrypoint" in config["project"]:
                    script = script or config["project"]["entrypoint"]
            except Exception as e:
                click.echo(f"Warning: Error reading preswald.toml: {e}")
                # Continue with provided script argument if config reading fails

        if not script:
            click.echo(
                "Error: No script specified and no entrypoint found in preswald.toml ❌"
            )
            click.echo(
                "Either provide a script argument or define entrypoint in preswald.toml"
            )
            return

        if not os.path.exists(script):
            click.echo(f"Error: Script '{script}' not found. ❌")
            return

        from preswald.deploy import deploy as deploy_app
        from preswald.utils import configure_logging, read_port_from_config

        config_path = os.path.join(os.path.dirname(script), "preswald.toml")
        log_level = configure_logging(config_path=config_path, level=log_level)
        port = read_port_from_config(config_path=config_path, port=port)

        # Track deployment
        telemetry.track_command(
            "deploy",
            {
                "script": script,
                "target": target,
                "port": port,
                "log_level": log_level,
                "has_github": bool(github),
                "has_api_key": bool(api_key),
            },
        )

        if target == "structured":
            click.echo("Starting production deployment... 🚀")
            try:
                for status_update in deploy_app(
                    script,
                    target,
                    port=port,
                    github_username=github.lower() if github else None,
                    api_key=api_key,
                ):
                    status = status_update.get("status", "")
                    message = status_update.get("message", "")

                    if "App is available here" in message:
                        continue

                    custom_subdomain_str = "Custom domain assigned at "
                    if custom_subdomain_str in message:
                        custom_subdomain_str = "Custom domain assigned at "
                        custom_subdomain_url = (
                            "https://" + message[len(custom_subdomain_str) :]
                        )
                        message = custom_subdomain_str + custom_subdomain_url

                    if status == "error":
                        click.echo(click.style(f"❌ {message}", fg="red"))
                    elif status == "success":
                        click.echo(click.style(f"✅ {message}", fg="green"))
                    else:
                        click.echo(f"i {message}")

            except Exception as e:
                click.echo(click.style(f"Deployment failed: {e!s} ❌", fg="red"))
                return
        else:
            url = deploy_app(script, target, port=port)

            # Deployment Success Message
            success_message = f"""

            ===========================================================\n
            🎉 Deployment successful! ✅

            🌐 Your app is live and running at:
            {url}

            💡 Next Steps:
                - Open the URL above in your browser to view your app

            🚀 Deployment Summary:
                - App: {script}
                - Environment: {target}
                - Port: {port}
            """

            click.echo(click.style(success_message, fg="green"))

    except Exception as e:
        click.echo(click.style(f"Deployment failed: {e!s} ❌", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--target",
    type=click.Choice(["local", "gcp", "aws", "structured"], case_sensitive=False),
    default="local",
    help="Target platform to stop the deployment from.",
)
def stop(target):
    """
    Stop the currently running deployment.

    This command must be run from the same directory as your Preswald app.
    """
    try:
        from preswald.deploy import cleanup_gcp_deployment, stop_structured_deployment

        # Track stop command
        telemetry.track_command("stop", {"target": target})
        config_path = "preswald.toml"
        if not os.path.exists(config_path):
            click.echo("Error: preswald.toml not found in current directory. ❌")
            click.echo("Make sure you're in a Preswald project directory.")
            return

        current_dir = os.getcwd()
        print(f"Current directory: {current_dir}")
        if target == "structured":
            try:
                response_json = stop_structured_deployment(current_dir)
                click.echo(response_json["message"])
                click.echo(
                    click.style(
                        "✅ Production deployment stopped successfully.", fg="green"
                    )
                )
            except Exception as e:
                click.echo(click.style(f"❌ {e!s}", fg="red"))
        if target == "gcp":
            try:
                click.echo("Starting GCP deployment cleanup... 🧹")
                for status_update in cleanup_gcp_deployment(current_dir):
                    status = status_update.get("status", "")
                    message = status_update.get("message", "")

                    if status == "error":
                        click.echo(click.style(f"❌ {message}", fg="red"))
                    elif status == "success":
                        click.echo(click.style(f"✅ {message}", fg="green"))
                    else:
                        click.echo(f"i {message}")
                click.echo(
                    click.style(
                        "✅ GCP deployment cleaned up successfully!", fg="green"
                    )
                )
            except Exception as e:
                click.echo(click.style(f"❌ GCP cleanup failed: {e!s}", fg="red"))
                sys.exit(1)
        else:
            from preswald.deploy import stop_local_deployment

            stop_local_deployment(current_dir)
            click.echo("Deployment stopped successfully. 🛑 ")
    except Exception:
        sys.exit(1)


@cli.command()
def deployments():
    """
    Show all deployments for your Preswald app.

    This command displays information about your deployments on Structured Cloud.
    Must be run from the directory containing your Preswald app.
    """
    try:
        script = os.path.join(os.getcwd(), ".env.structured")
        if not os.path.exists(script):
            click.echo(
                click.style(
                    "Error: No Preswald app found in current directory. ❌", fg="red"
                )
            )
            return

        # Track deployments command
        telemetry.track_command("deployments", {})

        from preswald.deploy import get_structured_deployments

        try:
            result = get_structured_deployments(script)

            # Print user info
            user = result.get("user", {})
            click.echo("\n" + click.style("User Information:", fg="blue", bold=True))
            click.echo(f"Username: {user.get('username')}")
            click.echo(f"Email: {user.get('email')}")

            # Print deployments
            deployments = result.get("deployments", [])
            click.echo("\n" + click.style("Deployments:", fg="blue", bold=True))

            if not deployments:
                click.echo("No active deployments found.")
            else:
                for deployment in deployments:
                    status_color = "green" if deployment.get("isActive") else "yellow"
                    click.echo(
                        "\n"
                        + click.style(
                            f"Deployment ID: {deployment.get('id')}", bold=True
                        )
                    )
                    click.echo(f"App ID: {deployment.get('appId')}")
                    click.echo(
                        click.style(
                            f"Status: {deployment.get('status')}", fg=status_color
                        )
                    )
                    click.echo(f"Created: {deployment.get('createdAt')}")
                    click.echo(f"Last Updated: {deployment.get('updatedAt')}")
                    click.echo(
                        click.style(
                            f"Active: {deployment.get('isActive')}", fg=status_color
                        )
                    )

            # Print meta info
            meta = result.get("meta", {})
            click.echo("\n" + click.style("Meta Information:", fg="blue", bold=True))
            click.echo(f"Total Deployments: {meta.get('total')}")
            click.echo(f"Last Updated: {meta.get('timestamp')}")

        except Exception as e:
            click.echo(click.style(f"❌ {e!s}", fg="red"))
            sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error showing deployments: {e} ❌", fg="red"))
        sys.exit(1)


@cli.command()
@click.pass_context
def tutorial(ctx):
    """
    Run the Preswald tutorial app.

    This command runs the tutorial app located in the package's tutorial directory.
    """
    import contextlib

    import preswald

    package_dir = os.path.dirname(preswald.__file__)
    tutorial_dir = os.path.join(package_dir, "tutorial")

    if not os.path.exists(tutorial_dir):
        click.echo(f"Error: Tutorial directory '{tutorial_dir}' not found. ❌")
        click.echo("👉 The tutorial files may be missing from your installation.")
        return

    # Track tutorial command
    telemetry.track_command("tutorial", {})

    click.echo("🚀 Launching the Preswald tutorial app! 🎉")

    # Use context manager to temporarily change directory
    with contextlib.chdir(tutorial_dir):
        # Invoke the 'run' command from the tutorial directory
        ctx.invoke(run, port=8501)


if __name__ == "__main__":
    cli()
