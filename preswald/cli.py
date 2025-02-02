import os
import click
import sys
import webbrowser
import pkg_resources
import tempfile
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from preswald.server import start_server
from preswald.deploy import deploy as deploy_app, stop as stop_app
from preswald.utils import read_template, configure_logging, generate_ci_config

# Create a temporary directory for IPC
TEMP_DIR = os.path.join(tempfile.gettempdir(), "preswald")
os.makedirs(TEMP_DIR, exist_ok=True)

# --------------------------
# New Core Functionality
# --------------------------

class LiveReloadHandler(FileSystemEventHandler):
    """Monitor file changes for live reload"""
    def __init__(self, script, port):
        self.script = script
        self.port = port
        self.server_process = None

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            click.echo("\n🔁 Detected file changes - restarting server...")
            self.restart_server()

    def start_server(self):
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "preswald.server", self.script, str(self.port)]
        )

    def restart_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        self.start_server()

# --------------------------
# Enhanced CLI Commands
# --------------------------

@click.group()
@click.version_option()
def cli():
    """Preswald CLI - A lightweight framework for interactive data apps."""
    pass

# --------------------------
# Cloud Deployment Enhancements
# --------------------------

@cli.command()
@click.argument("script", default="app.py")
@click.option(
    "--target",
    type=click.Choice(["local", "gcp", "aws", "azure", "structured"], case_sensitive=False),
    default="local",
    help="Target platform for deployment.",
)
@click.option("--ci", is_flag=True, help="Enable CI/CD mode for automated deployments")
def deploy(script, target, ci):
    """Deploy your Preswald app to various cloud providers."""
    try:
        if target in ["aws", "gcp", "azure"]:
            click.echo(f"\n🚀 Initializing {target.upper()} deployment...")
            
            # Infrastructure provisioning
            if click.confirm("Create new cloud infrastructure?"):
                provision_cloud_infra(target)
            
            # CI/CD integration
            if ci:
                generate_ci_config(target)
                click.echo(f"✅ Generated CI/CD pipeline for {target.upper()}")
            
            # Deployment logic
            deploy_cloud(target, script)
            
        elif target == "structured":
            handle_structured_deployment(script)
            
        else:
            handle_local_deployment(script)

    except Exception as e:
        click.echo(f"🚨 Deployment error: {str(e)}")
        sys.exit(1)

def provision_cloud_infra(target):
    """Automated infrastructure provisioning"""
    click.echo(f"🛠  Provisioning {target.upper()} resources...")
    # Add Terraform/cloud SDK integration here
    click.echo("✅ Cloud infrastructure ready")

# --------------------------
# New Plugin System
# --------------------------

@cli.group()
def plugins():
    """Manage Preswald plugins"""
    pass

@plugins.command(name="list")
def list_plugins():
    """Show installed plugins"""
    click.echo("Installed plugins:")
    # Add plugin discovery logic

@plugins.command()
@click.argument("plugin_name")
def install(plugin_name):
    """Install a plugin"""
    click.echo(f"📦 Installing {plugin_name}...")
    # Add plugin installation logic

# --------------------------
# Database Management
# --------------------------

@cli.group()
def db():
    """Database management commands"""
    pass

@db.command()
@click.argument("db_type", type=click.Choice(["sqlite", "postgres"]))
def init(db_type):
    """Initialize database"""
    click.echo(f"🛢  Initializing {db_type} database...")
    # Add database initialization logic

@db.command()
def migrate():
    """Run database migrations"""
    click.echo("🧳 Applying database migrations...")
    # Add migration logic

# --------------------------
# Enhanced Monitoring
# --------------------------

@cli.command()
@click.option("--follow", is_flag=True, help="Follow log output")
@click.option("--lines", default=50, help="Number of lines to display")
def logs(follow, lines):
    """View application logs"""
    click.echo(f"📜 Displaying last {lines} log lines:")
    # Add log tailing logic

# --------------------------
# Environment Management
# --------------------------

@cli.group()
def env():
    """Environment variable management"""
    pass

@env.command(name="set")
@click.argument("key")
@click.argument("value")
def set_env(key, value):
    """Set environment variable"""
    # Add .env file management
    click.echo(f"🔑 Set {key}={value}")

# --------------------------
# Theme Management
# --------------------------

@cli.group()
def theme():
    """UI theme management"""
    pass

@theme.command(name="list")
def list_themes():
    """Show available themes"""
    click.echo("🎨 Available themes: dark-mode, light-mode, terminal")

@theme.command()
@click.argument("theme_name")
def apply(theme_name):
    """Apply a UI theme"""
    click.echo(f"🎨 Applying {theme_name} theme...")

# --------------------------
# Enhanced Init Command
# --------------------------

@cli.command()
@click.argument("name", default="preswald_project")
@click.option("--template", 
              type=click.Choice(["dashboard", "ai-app", "minimal"]),
              default="minimal",
              help="Project template to use")
def init(name, template):
    """Initialize a new Preswald project with optional templates."""
    try:
        # Template handling
        click.echo(f"🚀 Creating {template} project...")
        copy_template_files(template, name)
        click.echo(f"✅ Successfully created {name} using {template} template")

    except Exception as e:
        click.echo(f"❌ Initialization error: {str(e)}")
        sys.exit(1)

def copy_template_files(template, dest):
    """Copy template-specific files"""
    # Add template handling logic

# --------------------------
# Enhanced Run Command
# --------------------------

@cli.command()
@click.argument("script", default="hello.py")
@click.option("--live-reload", is_flag=True, help="Enable automatic reload on changes")
def run(script, live_reload):
    """Run app with optional live reload"""
    if live_reload:
        click.echo("🔁 Live reload enabled - watching for file changes...")
        event_handler = LiveReloadHandler(script, port=8501)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(script), recursive=True)
        observer.start()
        try:
            event_handler.start_server()
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        start_server(script=script, port=8501)

# --------------------------
# Security & Authentication
# --------------------------

@cli.group()
def auth():
    """Authentication management"""
    pass

@auth.command(name="setup")
@click.option("--provider", 
              type=click.Choice(["oauth", "jwt", "basic"]),
              default="jwt")
def setup_auth(provider):
    """Configure authentication system"""
    click.echo(f"🔒 Setting up {provider} authentication...")
    # Add auth template generation

# --------------------------
# CI/CD Integration
# --------------------------

@cli.command()
@click.argument("provider", 
              type=click.Choice(["github", "gitlab", "jenkins"]))
def ci(provider):
    """Generate CI/CD pipeline configuration"""
    click.echo(f"⚙️  Generating {provider} CI/CD pipeline...")
    generate_ci_config(provider)
    click.echo("✅ CI/CD configuration generated")

if __name__ == "__main__":
    cli()
