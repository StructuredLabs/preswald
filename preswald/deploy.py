import os
import shutil
import tempfile
import subprocess
from pathlib import Path
import logging
import toml
import pkg_resources
import json

logger = logging.getLogger(__name__)


def get_deploy_dir(script_path: str) -> Path:
    """
    Creates and returns a persistent deployment directory next to the script.
    This directory will store all deployment-related files.
    """
    script_dir = Path(script_path).parent
    deploy_dir = script_dir / ".preswald_deploy"
    deploy_dir.mkdir(exist_ok=True)
    return deploy_dir


def get_container_name(script_path: str) -> str:
    """Generate a consistent container name for a given script"""
    return f"preswald-app-{Path(script_path).stem}"


def stop_existing_container(container_name: str) -> None:
    """Stop and remove any existing container with the same name"""
    try:
        # Stop the container if it's running
        subprocess.run(
            ["docker", "stop", container_name],
            check=False,  # Don't raise error if container doesn't exist
            capture_output=True,
        )
        # Remove the container
        subprocess.run(
            ["docker", "rm", container_name], check=False, capture_output=True
        )
    except Exception as e:
        logger.warning(f"Error cleaning up container: {e}")


def deploy(script_path: str) -> str:
    """
    Deploy a Preswald app locally using Docker.

    This function creates a Docker container that will run your Preswald application.
    It maintains a deployment directory next to your script for rebuilding and updating.

    Args:
        script_path: Path to the Preswald application script

    Returns:
        str: The URL where the application can be accessed
    """
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    container_name = get_container_name(script_path)

    # Get the deployment directory
    deploy_dir = get_deploy_dir(script_path)

    # Get preswald version for exact version matching
    preswald_version = pkg_resources.get_distribution("preswald").version

    # First, clear out the old deployment directory contents while preserving the directory itself
    for item in deploy_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    # Copy everything from the script's directory to the deployment directory
    for item in script_dir.iterdir():
        # Skip the deployment directory itself to avoid recursive copying
        if item.name == '.preswald_deploy':
            continue
            
        # Copy files and directories
        if item.is_file():
            shutil.copy2(item, deploy_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, deploy_dir / item.name)
            
    # Rename the main script to app.py if it's not already named that
    if Path(script_path).name != 'app.py':
        shutil.move(deploy_dir / Path(script_path).name, deploy_dir / 'app.py')

    # Create startup script
    startup_script = """
from preswald.server import start_server
import os

script_path = os.environ.get('SCRIPT_PATH', '/app/app.py')
port = int(os.environ.get('PORT', 8501))

start_server(script=script_path, port=port)
"""
    with open(deploy_dir / "run.py", "w") as f:
        f.write(startup_script)

    # Create Dockerfile
    dockerfile_content = f"""
FROM python:3.12-slim

WORKDIR /app

# Install nodejs and npm (needed for frontend)
RUN apt-get update && apt-get install -y nodejs npm

# Install preswald with exact version
RUN pip install preswald=={preswald_version}
RUN pip install setuptools

# Copy app and assets
COPY . .

EXPOSE 8501

ENV PYTHONPATH=/app
ENV SCRIPT_PATH=/app/app.py
ENV PORT=8501

# Use startup script that calls start_server
CMD ["python", "run.py"]
"""
    with open(deploy_dir / "Dockerfile", "w") as f:
        f.write(dockerfile_content)

    # Store deployment info
    deployment_info = {
        "script": script_path,
        "container_name": container_name,
        "preswald_version": preswald_version,
    }
    with open(deploy_dir / "deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    try:
        # Stop any existing container
        print(f"Stopping existing deployment (if any)...")
        stop_existing_container(container_name)

        # Build the Docker image
        print(f"Building Docker image {container_name}...")
        subprocess.run(
            ["docker", "build", "-t", container_name, "."], check=True, cwd=deploy_dir
        )

        # Start the container
        print("Starting container...")
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                container_name,
                "-p",
                "8501:8501",
                container_name,
            ],
            check=True,
            cwd=deploy_dir,
        )

        return "http://localhost:8501"

    except subprocess.CalledProcessError as e:
        raise Exception(f"Docker operation failed: {str(e)}")
    except FileNotFoundError:
        raise Exception(
            "Docker not found. Please install Docker Desktop from "
            "https://www.docker.com/products/docker-desktop"
        )


def stop(script_path: str = None) -> None:
    """
    Stop a running Preswald deployment.

    If script_path is provided, stops that specific deployment.
    Otherwise, looks for a deployment in the current directory.
    """
    if script_path:
        script_path = os.path.abspath(script_path)
        deploy_dir = get_deploy_dir(script_path)
    else:
        # Look for deployment in current directory
        deploy_dir = Path.cwd() / ".preswald_deploy"

    if not deploy_dir.exists():
        raise Exception("No deployment found")

    try:
        with open(deploy_dir / "deployment.json") as f:
            info = json.load(f)
            container_name = info["container_name"]

        print(f"Stopping deployment {container_name}...")
        stop_existing_container(container_name)
        print("Deployment stopped successfully")

    except Exception as e:
        raise Exception(f"Failed to stop deployment: {e}")
