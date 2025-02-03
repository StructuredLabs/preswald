import os
import shutil
import subprocess
from pathlib import Path
import logging
import pkg_resources
import json
import requests
import zipfile
from typing import Generator
from datetime import datetime
import io

from preswald.utils import read_template

logger = logging.getLogger(__name__)

# Default Structured Cloud service URL
STRUCTURED_CLOUD_SERVICE_URL = os.getenv('STRUCTURED_CLOUD_SERVICE_URL', 'http://127.0.0.1:8080')


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


def check_gcloud_installation() -> bool:
    """
    Check if the Google Cloud SDK is installed and accessible.
    Returns True if gcloud is installed, False otherwise.
    """
    try:
        subprocess.run(["gcloud", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_gcloud_auth() -> bool:
    """
    Check if the user is authenticated with Google Cloud.
    Returns True if authenticated, False otherwise.
    """
    try:
        # Try to get the current account
        result = subprocess.run(
            ["gcloud", "auth", "list", "--format=value(account)"],
            check=True,
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def setup_gcloud() -> None:
    """
    Guide the user through setting up Google Cloud SDK and authentication.
    Raises an exception if setup fails.
    """
    if not check_gcloud_installation():
        print(
            "\nGoogle Cloud SDK not found. You'll need to install it to deploy to Cloud Run."
        )
        print("\nInstallation instructions:")
        print("1. Visit https://cloud.google.com/sdk/docs/install")
        print("2. Follow the installation steps for your operating system")
        print("3. Run this deployment command again")
        raise Exception("Please install Google Cloud SDK first")

    if not check_gcloud_auth():
        print("\nYou need to authenticate with Google Cloud.")
        print("Opening browser for authentication...")

        try:
            # Run authentication command
            subprocess.run(["gcloud", "auth", "login"], check=True)

            # Configure Docker auth
            print("\nConfiguring Docker authentication...")
            subprocess.run(["gcloud", "auth", "configure-docker"], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Authentication failed: {str(e)}")


def ensure_project_selected() -> str:
    """
    Ensure a Google Cloud project is selected.
    Returns the project ID.
    """
    try:
        project_id = subprocess.check_output(
            ["gcloud", "config", "get-value", "project"], text=True
        ).strip()

        if not project_id:
            print("\nNo Google Cloud project selected.")
            print("Available projects:")

            # List available projects
            subprocess.run(["gcloud", "projects", "list"], check=True)

            # Prompt for project ID
            project_id = input("\nEnter the project ID you want to use: ").strip()

            # Set the project
            subprocess.run(
                ["gcloud", "config", "set", "project", project_id], check=True
            )

        return project_id

    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get or set project: {str(e)}")


def deploy_to_cloud_run(deploy_dir: Path, container_name: str, port: int = 8501) -> str:
    """
    Deploy a Preswald app to Google Cloud Run.

    Args:
        deploy_dir: Path to the deployment directory containing the Docker context
        container_name: Name to use for the container

    Returns:
        str: The URL where the app is deployed
    """
    try:
        # First, ensure Google Cloud SDK is set up properly
        setup_gcloud()

        # Ensure a project is selected
        project_id = ensure_project_selected()

        region = "us-west1"  # Default region, could be made configurable
        gcr_image = f"gcr.io/{project_id}/{container_name}"

        print(f"Pushing image to Google Container Registry...")

        # Tag and push the image
        subprocess.run(
            ["docker", "tag", container_name, gcr_image], check=True, cwd=deploy_dir
        )
        subprocess.run(["docker", "push", gcr_image], check=True, cwd=deploy_dir)

        print(f"Deploying to Cloud Run...")

        # Deploy to Cloud Run
        subprocess.run(
            [
                "gcloud",
                "run",
                "deploy",
                container_name,
                "--image",
                gcr_image,
                "--platform",
                "managed",
                "--region",
                region,
                "--allow-unauthenticated",  # Makes the service publicly accessible
                "--port",
                f"{port}",  # Match the port your app uses
            ],
            check=True,
            text=True,
            capture_output=True,
        )

        url_result = subprocess.run(
            [
                "gcloud",
                "run",
                "services",
                "describe",
                container_name,  # Same name used in deployment
                "--platform",
                "managed",
                "--region",
                region,
                "--format=value(status.url)",
            ],
            check=True,
            text=True,
            capture_output=True,
        )

        return url_result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if "not installed" in str(e):
            raise Exception(
                "Google Cloud SDK not found. Please install from: "
                "https://cloud.google.com/sdk/docs/install"
            )
        raise Exception(f"Cloud Run deployment failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Deployment failed: {str(e)}")


def deploy_to_prod(script_path: str, port: int = 8501) -> Generator[dict, None, None]:
    """
    Deploy a Preswald app to production via Structured Cloud service.
    
    Args:
        script_path: Path to the Preswald application script
        port: Port number for the deployment
        
    Returns:
        Generator yielding deployment status updates
    """
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    env_file = script_dir / '.env.structured'
    
    if not env_file.exists():
        # Get GitHub credentials from user
        github_username = input("Enter your GitHub username: ")
        structured_cloud_api_key = input("Enter your Structured Cloud API key: ")
        
        # Generate a unique app ID (using timestamp)
        app_id = f"app_{int(datetime.now().timestamp())}"
        
        # Create and populate .env.structured file
        with open(env_file, 'w') as f:
            f.write(f"GITHUB_USERNAME={github_username}\n")
            f.write(f"STRUCTURED_CLOUD_API_KEY={structured_cloud_api_key}\n") 
            f.write(f"APP_ID={app_id}\n")
    else:
        # Read credentials from existing env file
        credentials = {}
        with open(env_file, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                credentials[key] = value
        github_username = credentials['GITHUB_USERNAME']
        structured_cloud_api_key = credentials['STRUCTURED_CLOUD_API_KEY']
        app_id = credentials['APP_ID']
    
    # Create a temporary zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the script directory and add all files
        for root, _, files in os.walk(script_dir):
            for file in files:
                # Skip .preswald_deploy directory
                if '.preswald_deploy' in root:
                    continue
                    
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, script_dir)
                zip_file.write(file_path, arc_name)
    
    # Prepare the zip file for sending
    zip_buffer.seek(0)
    files = {'deployment': ('app.zip', zip_buffer, 'application/zip')}
    
    # Send the deployment request with credentials
    try:
        response = requests.post(
            f"{STRUCTURED_CLOUD_SERVICE_URL}/deploy",
            files=files,
            data={
                'github_username': github_username,
                'structured_cloud_api_key': structured_cloud_api_key,
                'app_id': app_id
            },
            stream=True
        )
        response.raise_for_status()
        
        # Process SSE stream
        for line in response.iter_lines():
            if line:
                # SSE lines start with "data: "
                if line.startswith(b'data: '):
                    data = json.loads(line[6:].decode('utf-8'))
                    yield data
                    
    except requests.RequestException as e:
        yield {
            'status': 'error',
            'message': f'Deployment failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
        raise Exception(f"Production deployment failed: {str(e)}")


def deploy_to_gcp(script_path: str, port: int = 8501) -> str:
    """
    Deploy a Preswald app to Google Cloud Run.
    This function creates a Docker container locally and deploys it to Cloud Run.

    Args:
        script_path: Path to the Preswald application script
        port: Port number for the deployment

    Returns:
        str: The URL where the application is deployed on Cloud Run
    """
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    container_name = get_container_name(script_path)
    deploy_dir = get_deploy_dir(script_path)
    
    # Get preswald version for exact version matching
    preswald_version = pkg_resources.get_distribution("preswald").version
    
    # Clear out old deployment directory contents while preserving the directory itself
    for item in deploy_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
            
    # Copy everything from script's directory to deployment directory
    for item in script_dir.iterdir():
        if item.name == ".preswald_deploy":
            continue
        if item.is_file():
            shutil.copy2(item, deploy_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, deploy_dir / item.name)
            
    # Rename main script to app.py if needed
    if Path(script_path).name != "app.py":
        shutil.move(deploy_dir / Path(script_path).name, deploy_dir / "app.py")
        
    # Create startup script
    startup_template = read_template("run.py")
    startup_script = startup_template.format(port=port)
    with open(deploy_dir / "run.py", "w") as f:
        f.write(startup_script)
        
    # Create Dockerfile
    dockerfile_template = read_template("Dockerfile")
    dockerfile_content = dockerfile_template.format(
        port=port, preswald_version=preswald_version
    )
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
        
        # Build the Docker image for GCP (using linux/amd64 platform)
        print(f"Building Docker image {container_name} for GCP deployment...")
        subprocess.run(
            [
                "docker",
                "build",
                "--platform",
                "linux/amd64",
                "-t",
                container_name,
                ".",
            ],
            check=True,
            cwd=deploy_dir,
        )
        
        # Deploy to Cloud Run
        return deploy_to_cloud_run(deploy_dir, container_name, port=port)
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Docker operation failed: {str(e)}")
    except FileNotFoundError:
        raise Exception(
            "Docker not found. Please install Docker Desktop from "
            "https://www.docker.com/products/docker-desktop"
        )


def deploy(script_path: str, target: str = "local", port: int = 8501) -> str | Generator[dict, None, None]:
    """
    Deploy a Preswald app.

    Args:
        script_path: Path to the Preswald application script
        target: Deployment target ("local", "gcp", "aws", or "prod")
        port: Port number for the deployment

    Returns:
        str | Generator: URL where the application can be accessed for local/cloud deployments,
                        or a Generator yielding deployment status for production deployments
    """
    if target == "structured":
        return deploy_to_prod(script_path, port)
    elif target == "gcp":
        return deploy_to_gcp(script_path, port)
    elif target == "local":
        script_path = os.path.abspath(script_path)
        script_dir = Path(script_path).parent
        container_name = get_container_name(script_path)
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
            if item.name == ".preswald_deploy":
                continue
            # Copy files and directories
            if item.is_file():
                shutil.copy2(item, deploy_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, deploy_dir / item.name)
        # Rename the main script to app.py if it's not already named that
        if Path(script_path).name != "app.py":
            shutil.move(deploy_dir / Path(script_path).name, deploy_dir / "app.py")
        # Create startup script
        startup_template = read_template("run.py")
        startup_script = startup_template.format(port=port)
        with open(deploy_dir / "run.py", "w") as f:
            f.write(startup_script)
        # Create Dockerfile
        dockerfile_template = read_template("Dockerfile")
        dockerfile_content = dockerfile_template.format(
            port=port, preswald_version=preswald_version
        )
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
                ["docker", "build", "-t", container_name, "."],
                check=True,
                cwd=deploy_dir,
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
                    f"{port}:{port}",
                    container_name,
                ],
                check=True,
                cwd=deploy_dir,
            )
            return f"http://localhost:{port}"
        except subprocess.CalledProcessError as e:
            raise Exception(f"Docker operation failed: {str(e)}")
        except FileNotFoundError:
            raise Exception(
                "Docker not found. Please install Docker Desktop from "
                "https://www.docker.com/products/docker-desktop"
            )
    else:
        raise ValueError(f"Unsupported deployment target: {target}")


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
