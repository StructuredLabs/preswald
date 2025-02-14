import os
import sys
import tempfile
import webbrowser

import click
import pkg_resources

from preswald.deploy import cleanup_gcp_deployment, stop_structured_deployment
from preswald.deploy import deploy as deploy_app
from preswald.deploy import stop as stop_app
from preswald.main import start_server
from preswald.utils import configure_logging, read_template


# Create a temporary directory for IPC
TEMP_DIR = os.path.join(tempfile.gettempdir(), "preswald")
os.makedirs(TEMP_DIR, exist_ok=True)


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
    try:
        os.makedirs(name, exist_ok=True)
        os.makedirs(os.path.join(name, "images"), exist_ok=True)
        os.makedirs(os.path.join(name, "data"), exist_ok=True)

        # Copy default branding files from package resources
        import shutil

        default_static_dir = pkg_resources.resource_filename("preswald", "static")
        default_favicon = os.path.join(default_static_dir, "favicon.ico")
        default_logo = os.path.join(default_static_dir, "logo.png")

        shutil.copy2(default_favicon, os.path.join(name, "images", "favicon.ico"))
        shutil.copy2(default_logo, os.path.join(name, "images", "logo.png"))

        file_templates = {
            "hello.py": "hello.py",
            "preswald.toml": "preswald.toml",
            "secrets.toml": "secrets.toml",
            ".gitignore": "gitignore",
            "README.md": "readme.md",
            "pyproject.toml": "pyproject.toml",
            "data/sample.csv": "sample.csv",
        }

        for file_name, template_name in file_templates.items():
            content = read_template(template_name)
            with open(os.path.join(name, file_name), "w") as f:
                f.write(content)

        click.echo(f"Initialized a new Preswald project in '{name}/' 🎉!")
    except Exception as e:
        click.echo(f"Error initializing project: {e} ❌")


@cli.command()
@click.argument("script", default="hello.py")
@click.option("--port", default=8501, help="Port to run the server on.")
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default=None,
    help="Set the logging level (overrides config file)",
)
def run(script, port, log_level):
    """
    Run a Preswald app.

    By default, it runs the `hello.py` script on localhost:8501.
    """
    if not os.path.exists(script):
        click.echo(f"Error: Script '{script}' not found. ❌")
        return

    config_path = os.path.join(os.path.dirname(script), "preswald.toml")
    log_level = configure_logging(config_path=config_path, level=log_level)

    url = f"http://localhost:{port}"
    click.echo(f"Running '{script}' on {url} with log level {log_level}  🎉!")

    # ipc_file = os.path.join(TEMP_DIR, f"preswald_connections_{os.getpid()}.json")
    # os.environ["PRESWALD_IPC_FILE"] = ipc_file

    # celery_cmd = [
    #     "celery",
    #     "-A", "preswald.celery_app",
    #     "worker",
    #     "--loglevel", log_level.lower(),
    #     "--concurrency", "1",
    #     "--pool", "solo",
    #     "--without-heartbeat",
    #     "--without-mingle",
    #     "--without-gossip"
    # ]

    try:
        # click.echo("Starting Celery worker...")
        # celery_process = subprocess.Popen(
        #     celery_cmd,
        #     env=dict(
        #         os.environ,
        #         SCRIPT_PATH=os.path.abspath(script),
        #         PYTHONPATH=os.getcwd(),
        #         PYTHONUNBUFFERED="1"
        #     )
        # )

        # # Wait for Celery to start
        # import time
        # time.sleep(2)

        # if celery_process.poll() is not None:
        #     out, err = celery_process.communicate()
        #     click.echo(f"Error starting Celery worker: {err}")
        #     return

        webbrowser.open(url)

        # try:
        start_server(script=script, port=port)
        # finally:
        #     click.echo("Shutting down Celery worker...")
        #     celery_process.terminate()
        #     celery_process.wait(timeout=5)

        #     try:
        #         if os.path.exists(ipc_file):
        #             os.remove(ipc_file)
        #     except Exception as e:
        #         click.echo(f"Error removing IPC file: {e}")

    except Exception as e:
        click.echo(f"Error: {e}")
        # if 'celery_process' in locals():
        #     celery_process.terminate()
        #     celery_process.wait(timeout=5)


@cli.command()
@click.argument("script", default="app.py")
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
def deploy(script, target, port, log_level):
    """
    Deploy your Preswald app.

    This allows you to share the app within your local network or deploy to production.
    """
    try:
        if target == "aws":
            click.echo(click.style(
                "\n📢 AWS Deployment Status",
                fg="yellow", bold=True
            ))
            click.echo(click.style(
                "We're working on supporting AWS soon! Please enjoy some ☕ and 🍌 in the meantime\n",
                fg="yellow"
            ))
            return

        if not os.path.exists(script):
            click.echo(click.style("Error: ", fg="red", bold=True) + 
                      click.style(f"Script '{script}' not found. ❌", fg="red"))
            return

        config_path = os.path.join(os.path.dirname(script), "preswald.toml")
        log_level = configure_logging(config_path=config_path, level=log_level)

        if target == "structured":
            click.echo(click.style("\n🚀 Production Deployment", fg="blue", bold=True))
            click.echo("=" * 50)
            try:
                for status_update in deploy_app(script, target, port=port):
                    # Ensure status_update is a dictionary
                    if not isinstance(status_update, dict):
                        continue
                        
                    status = status_update.get("status", "")
                    message = status_update.get("message", "")

                    prefix = {
                        "error": click.style("❌ ERROR:", fg="red", bold=True),
                        "success": click.style("✅ SUCCESS:", fg="green", bold=True),
                        "info": click.style("ℹ️  INFO:", fg="blue", bold=True)
                    }.get(status, click.style("ℹ️  INFO:", fg="blue", bold=True))
                    
                    click.echo(f"{prefix} {message}")

            except Exception as e:
                click.echo("\n" + "=" * 50)
                click.echo(click.style("❌ Deployment Failed", fg="red", bold=True))
                click.echo(click.style(f"Error: {e!s}", fg="red"))
                click.echo("=" * 50 + "\n")
                return
        else:
            url = deploy_app(script, target, port=port)

            # Deployment Success Message
            header = click.style("\n🎉 Deployment Successful!", fg="green", bold=True)
            divider = click.style("=" * 60, fg="green")
            
            details = f"""
{header}
{divider}

🌐 Access Your Application
   URL: {click.style(url, fg="bright_green", bold=True)}

📋 Deployment Details
   • Script: {click.style(script, fg="bright_green")}
   • Environment: {click.style(target, fg="bright_green")}
   • Port: {click.style(str(port), fg="bright_green")}

💡 Next Steps
   1. Open the URL above in your browser
   2. Start using your deployed application
   3. Monitor the application logs for any issues

{divider}
"""
            click.echo(details)

    except Exception as e:
        click.echo(click.style("\n❌ Deployment Error", fg="red", bold=True))
        click.echo(click.style(f"Details: {e}", fg="red"))
        click.echo("\n")


@cli.command()
@click.argument("script", default="app.py")
@click.option(
    "--target",
    type=click.Choice(["local", "gcp", "aws", "structured"], case_sensitive=False),
    default="local",
    help="Target platform to stop the deployment from.",
)
def stop(script, target):
    """
    Stop the currently running deployment.

    This command must be run from the same directory as your Preswald app.
    """
    try:
        if not os.path.exists(script):
            click.echo(f"Error: Script '{script}' not found. ❌")
            return

        if target == "structured":
            try:
                stop_structured_deployment(script)
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
                for status_update in cleanup_gcp_deployment(script):
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
            stop_app(script)
            click.echo("Deployment stopped successfully. 🛑 ")
    except Exception as e:
        click.echo(f"Error stopping deployment: {e} ❌")
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

    This command runs the tutorial app located in the 'tutorial/hello.py' file.
    """
    tutorial_script = os.path.join("tutorial", "hello.py")

    if not os.path.exists(tutorial_script):
        click.echo(f"Error: Tutorial script '{tutorial_script}' not found. ❌")
        click.echo("👉 Please run this command from the root directory of the project.")
        return

    click.echo("🚀 Launching the Preswald tutorial app! 🎉")

    # Invoke the 'run' command with 'tutorial/hello.py'
    ctx.invoke(run, script=tutorial_script)


if __name__ == "__main__":
    cli()
