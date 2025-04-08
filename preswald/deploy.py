import io
import json
import logging
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, Union

import requests
import toml

from preswald.utils import get_project_slug


logger = logging.getLogger(__name__)

# Default Structured Cloud service URL
# STRUCTURED_CLOUD_SERVICE_URL = os.getenv('STRUCTURED_CLOUD_SERVICE_URL', 'http://127.0.0.1:8080')
STRUCTURED_CLOUD_SERVICE_URL = "https://deployer.preswald.com"


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
    script_dir = Path(script_path).parent
    with open(script_dir / "preswald.toml") as f:
        preswald_toml = f.read()
    config = toml.loads(preswald_toml)
    container_name = f"preswald-app-{config['project']['slug']}"
    container_name = container_name.lower()
    container_name = re.sub(r"[^a-z0-9-]", "", container_name)
    container_name = container_name.strip("-")
    return container_name


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
            raise Exception(f"Authentication failed: {e!s}") from e


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
        raise Exception(f"Failed to get or set project: {e!s}") from e


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

        print("Pushing image to Google Container Registry...")

        # Tag and push the image
        subprocess.run(
            ["docker", "tag", container_name, gcr_image], check=True, cwd=deploy_dir
        )
        subprocess.run(["docker", "push", gcr_image], check=True, cwd=deploy_dir)

        print("Deploying to Cloud Run...")

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
            ) from e
        raise Exception(f"Cloud Run deployment failed: {e!s}") from e
    except Exception as e:
        raise Exception(f"Deployment failed: {e!s}") from e


def deploy_to_prod(  # noqa: C901
    script_path: str,
    port: int = 8501,
    github_username: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Generator[dict, None, None]:
    """
    Deploy a Preswald app to production via Structured Cloud service.

    Args:
        script_path: Path to the Preswald application script
        port: Port number for the deployment
        github_username: Optional GitHub username provided via CLI
        api_key: Optional Structured Cloud API key provided via CLI

    Returns:
        Generator yielding deployment status updates
    """
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    config_path = script_dir / "preswald.toml"
    env_file = script_dir / ".env.structured"

    # Get project slug from preswald.toml
    try:
        project_slug = get_project_slug(config_path)
    except Exception as e:
        yield {
            "status": "error",
            "message": f"Failed to get project slug: {e!s}",
            "timestamp": datetime.now().isoformat(),
        }
        raise Exception(f"Failed to get project slug: {e!s}") from e

    if not env_file.exists():
        # Use provided credentials or get from user input
        if not github_username:
            github_username = input("Enter your GitHub username: ")
        if not api_key:
            structured_cloud_api_key = input("Enter your Structured Cloud API key: ")
        else:
            structured_cloud_api_key = api_key

        # Create and populate .env.structured file
        with open(env_file, "w") as f:
            f.write(f"GITHUB_USERNAME={github_username}\n")
            f.write(f"STRUCTURED_CLOUD_API_KEY={structured_cloud_api_key}\n")
    else:
        # Read credentials from existing env file if not provided via CLI
        credentials = {}
        with open(env_file) as f:
            for line in f:
                key, value = line.strip().split("=")
                credentials[key] = value

        github_username = github_username or credentials["GITHUB_USERNAME"]
        structured_cloud_api_key = api_key or credentials["STRUCTURED_CLOUD_API_KEY"]

    # Create a temporary zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the script directory and add all files
        for root, _, files in os.walk(script_dir):
            for file in files:
                # Skip .preswald_deploy directory
                if ".preswald_deploy" in root:
                    continue

                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, script_dir)
                zip_file.write(file_path, arc_name)

    # Prepare the zip file for sending
    zip_buffer.seek(0)
    files = {"deployment": ("app.zip", zip_buffer, "application/zip")}

    try:
        git_repo_name = (
            subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"], cwd=script_dir
            )
            .decode("utf-8")
            .strip()
        )

        git_repo_name = git_repo_name.split("/")[-1].replace(".git", "")
    except subprocess.CalledProcessError:
        git_repo_name = os.path.basename(script_dir)

    try:
        response = requests.post(
            f"{STRUCTURED_CLOUD_SERVICE_URL}/deploy",
            files=files,
            data={
                "github_username": github_username,
                "structured_cloud_api_key": structured_cloud_api_key,
                "project_slug": project_slug,
                "git_repo_name": git_repo_name,
            },
            stream=True,
        )
        response.raise_for_status()

        # Process SSE stream
        for line in response.iter_lines():
            if line:
                # SSE lines start with "data: "
                if line.startswith(b"data: "):
                    data = json.loads(line[6:].decode("utf-8"))
                    yield data

    except requests.RequestException as e:
        yield {
            "status": "error",
            "message": f"Deployment failed: {e!s}",
            "timestamp": datetime.now().isoformat(),
        }
        raise Exception(f"Production deployment failed: {e!s}") from e


def check_gcloud_auth_for_gcr() -> bool:
    try:
        result = subprocess.run(
            ["gcloud", "auth", "configure-docker", "--quiet"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def authenticate_gcr() -> None:
    try:
        subprocess.run(
            ["gcloud", "auth", "configure-docker", "--quiet"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to authenticate with GCR: {e!s}") from e


def deploy_to_gcp(script_path: str, port: int = 8501) -> str:  # noqa: C901
    """
    Deploy a Preswald app to Google Cloud Run using a simplified Docker approach.

    Args:
        script_path: Path to the Preswald application script
        port: Port number for the deployment

    Returns:
        str: The URL where the app is deployed
    """
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    container_name = get_container_name(script_path)
    deploy_dir = get_deploy_dir(script_path)

    try:
        if not check_gcloud_installation():
            raise Exception(
                "Google Cloud SDK not found. Please install from: "
                "https://cloud.google.com/sdk/docs/install"
            )

        if not check_gcloud_auth():
            print("\nYou need to authenticate with Google Cloud.")
            print("Opening browser for authentication...")
            subprocess.run(["gcloud", "auth", "login"], check=True)

        project_id = ensure_project_selected()
        print(f"\nUsing Google Cloud project: {project_id}")

        if not check_gcloud_auth_for_gcr():
            authenticate_gcr()

        with open(script_dir / "preswald.toml") as f:
            preswald_toml = f.read()
        config = toml.loads(preswald_toml)
        original_port = config["project"]["port"]
        config["project"]["port"] = 8080

        with open(script_dir / "preswald.toml", "w") as f:
            toml.dump(config, f)

        # Clear out old deployment directory contents while preserving the directory itself
        for item in deploy_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        dockerfile_content = """FROM structuredlabs/preswald:latest
COPY . /app/project
"""
        with open(deploy_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)

        for item in script_dir.iterdir():
            if item.name == ".preswald_deploy":
                continue
            if item.is_file():
                shutil.copy2(item, deploy_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, deploy_dir / item.name, dirs_exist_ok=True)

        region = "us-west1"
        gcr_image = f"gcr.io/{project_id}/{container_name}"

        print(f"\nBuilding Docker image {container_name} for GCP deployment...")
        build_cmd = [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "-t",
            container_name,
            "--load",
            ".",
        ]
        print(f"Running build command in {deploy_dir}: {' '.join(build_cmd)}")
        subprocess.run(
            build_cmd,
            check=True,
            cwd=str(deploy_dir),
        )

        print("\nPushing image to Google Container Registry...")
        subprocess.run(
            ["docker", "tag", container_name, gcr_image],
            check=True,
            cwd=str(deploy_dir),
        )

        try:
            subprocess.run(
                ["docker", "push", gcr_image], check=True, cwd=str(deploy_dir)
            )
        except subprocess.CalledProcessError as e:
            if "unauthorized" in str(e) or "authentication required" in str(e):
                print("\nAuthentication failed. Trying to reauthenticate...")
                authenticate_gcr()
                # Try pushing again after reauthentication
                subprocess.run(
                    ["docker", "push", gcr_image], check=True, cwd=str(deploy_dir)
                )
            else:
                raise

        print("\nDeploying to Cloud Run...")
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
                "--allow-unauthenticated",
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
                container_name,
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

        config["project"]["port"] = original_port
        with open(script_dir / "preswald.toml", "w") as f:
            toml.dump(config, f)

        deployed_url = url_result.stdout.strip()
        print(f"\n✨ Successfully deployed to: {deployed_url}")
        return deployed_url

    except subprocess.CalledProcessError as e:
        if "not installed" in str(e):
            raise Exception(
                "Google Cloud SDK not found. Please install from: "
                "https://cloud.google.com/sdk/docs/install"
            ) from e
        elif "unauthorized" in str(e) or "authentication required" in str(e):
            raise Exception(
                "Authentication failed. Please run:\n"
                "1. gcloud auth login\n"
                "2. gcloud auth configure-docker\n"
                "Then try deploying again."
            ) from e
        raise Exception(f"Cloud Run deployment failed: {e!s}") from e
    except FileNotFoundError as e:
        raise Exception(
            "Docker not found. Please install Docker Desktop from "
            "https://www.docker.com/products/docker-desktop"
        ) from e
    except Exception as e:
        raise Exception(f"Deployment failed: {e!s}") from e
    finally:
        try:
            with open(script_dir / "preswald.toml") as f:
                config = toml.loads(f.read())
            config["project"]["port"] = original_port
            with open(script_dir / "preswald.toml", "w") as f:
                toml.dump(config, f)
        except Exception:
            pass


def find_available_port(start_port: int = 8501) -> int:
    import socket

    port = start_port
    while True:
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            port += 1


def deploy_to_local(script_path: str, start_port: int = 8501) -> str:
    script_path = os.path.abspath(script_path)
    script_dir = Path(script_path).parent
    container_name = get_container_name(script_path)

    try:
        # Find an available port
        port = find_available_port(start_port)
        print(f"\nUsing port: {port}")

        # Stop any existing container
        print("Stopping existing deployment (if any)...")
        stop_existing_container(container_name)

        # Start the container with the prebuilt base image
        print("Starting container with prebuilt base image...")
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                container_name,
                "-p",
                f"{port}:{start_port}",
                "-v",
                f"{script_dir}:/app/project",
                "structuredlabs/preswald:latest",
            ],
            check=True,
        )

        return f"http://localhost:{port}"

    except subprocess.CalledProcessError as e:
        raise Exception(f"Docker operation failed: {e!s}") from e
    except FileNotFoundError as e:
        raise Exception(
            "Docker not found. Please install Docker Desktop from "
            "https://www.docker.com/products/docker-desktop"
        ) from e
    except Exception as e:
        raise Exception(f"Local deployment failed: {e!s}") from e


def deploy(
    script_path: str,
    target: str = "local",
    port: int = 8501,
    github_username: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Union[str, Generator[dict, None, None]]:
    """
    Deploy a Preswald app.

    Args:
        script_path: Path to the Preswald application script
        target: Deployment target ("local", "gcp", "aws", or "prod")
        port: Port number for the deployment
        github_username: Optional GitHub username for structured deployment
        api_key: Optional Structured Cloud API key for structured deployment

    Returns:
        str | Generator: URL where the application can be accessed for local/cloud deployments,
                        or a Generator yielding deployment status for production deployments
    """
    if target == "structured":
        return deploy_to_prod(script_path, port, github_username, api_key)
    elif target == "gcp":
        return deploy_to_gcp(script_path, port)
    elif target == "local":
        return deploy_to_local(script_path, port)
    else:
        raise ValueError(f"Unsupported deployment target: {target}")


def stop_local_deployment(script_dir: str) -> None:
    try:
        container_name = get_container_name(Path(script_dir) / "preswald.toml")
        print(f"Stopping local deployment {container_name}...")
        stop_existing_container(container_name)
        print("✅ Local deployment stopped successfully")

    except FileNotFoundError as e:
        raise Exception(f"No deployment configuration found: {e}") from e
    except Exception as e:
        raise Exception(f"Failed to stop local deployment: {e}") from e


def stop_structured_deployment(script_dir: str) -> dict:
    """
    Stop a Preswald app deployed to Structured Cloud service.

    Args:
        script_path: Path to the Preswald application script

    Returns:
        dict: Status of the stop operation
    """
    config_path = Path(script_dir) / "preswald.toml"
    env_file = Path(script_dir) / ".env.structured"

    # Get project slug from preswald.toml
    try:
        project_slug = get_project_slug(config_path)
    except Exception as e:
        raise Exception(f"Failed to get project slug: {e!s}") from e

    if not env_file.exists():
        raise Exception("No deployment found. The .env.structured file is missing.")

    # Read credentials from existing env file
    credentials = {}
    with open(env_file) as f:
        for line in f:
            key, value = line.strip().split("=")
            credentials[key] = value

    github_username = credentials["GITHUB_USERNAME"]
    structured_cloud_api_key = credentials["STRUCTURED_CLOUD_API_KEY"]

    try:
        response = requests.post(
            f"{STRUCTURED_CLOUD_SERVICE_URL}/stop",
            json={
                "github_username": github_username,
                "structured_cloud_api_key": structured_cloud_api_key,
                "project_slug": project_slug,
            },
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise Exception(f"Failed to stop production deployment: {e!s}") from e


def get_structured_deployments(script_path: str) -> dict:
    """
    Get deployments from Structured Cloud service.

    Args:
        script_path: Path to the Preswald application script

    Returns:
        dict: Deployment information including user, organization, and deployments list
    """
    script_dir = Path(script_path).parent
    config_path = script_dir / "preswald.toml"
    env_file = script_dir / ".env.structured"

    # Get project slug from preswald.toml
    try:
        project_slug = get_project_slug(config_path)
    except Exception as e:
        raise Exception(f"Failed to get project slug: {e!s}") from e

    if not env_file.exists():
        raise Exception("No deployment found. The .env.structured file is missing.")

    # Read credentials from existing env file
    credentials = {}
    with open(env_file) as f:
        for line in f:
            key, value = line.strip().split("=")
            credentials[key] = value

    github_username = credentials["GITHUB_USERNAME"]
    structured_cloud_api_key = credentials["STRUCTURED_CLOUD_API_KEY"]

    try:
        response = requests.post(
            f"{STRUCTURED_CLOUD_SERVICE_URL}/deployments",
            json={
                "github_username": github_username,
                "structured_cloud_api_key": structured_cloud_api_key,
                "project_slug": project_slug,
            },
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch deployments: {e!s}") from e


def cleanup_gcp_deployment(script_dir: str):  # noqa: C901
    def log_status(status, message):
        return {
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

    try:
        yield log_status("info", "Gathering deployment information...")
        script_dir = Path(script_dir)

        preswald_toml = script_dir / "preswald.toml"
        if not preswald_toml.exists():
            raise FileNotFoundError(f"preswald.toml not found in {script_dir}")

        with open(preswald_toml) as f:
            config = toml.loads(f.read())
            slug = config["project"]["slug"]
            container_name = f"preswald-app-{slug}"
            container_name = container_name.lower()
            container_name = re.sub(r"[^a-z0-9-]", "", container_name)
            container_name = container_name.strip("-")

        yield log_status("info", "Verifying Google Cloud SDK setup...")
        if not check_gcloud_installation():
            yield log_status(
                "error",
                "Google Cloud SDK not found. Please install from: https://cloud.google.com/sdk/docs/install",
            )
            return

        if not check_gcloud_auth():
            yield log_status(
                "info", "Authentication required. Opening browser for login..."
            )
            try:
                subprocess.run(["gcloud", "auth", "login"], check=True)
            except subprocess.CalledProcessError as e:
                yield log_status("error", f"Failed to authenticate: {e}")
                return

        try:
            project_id = ensure_project_selected()
            yield log_status("success", f"Found GCP project: {project_id}")
        except Exception as e:
            yield log_status("error", f"Failed to get GCP project: {e!s}")
            return

        region = "us-west1"
        gcr_image = f"gcr.io/{project_id}/{container_name}"

        # Delete Cloud Run service
        yield log_status("info", f"Checking Cloud Run service: {container_name}")
        try:
            service_exists = (
                subprocess.run(
                    [
                        "gcloud",
                        "run",
                        "services",
                        "describe",
                        container_name,
                        "--platform",
                        "managed",
                        "--region",
                        region,
                        "--format=json",
                    ],
                    capture_output=True,
                    text=True,
                ).returncode
                == 0
            )

            if service_exists:
                yield log_status(
                    "info", f"Deleting Cloud Run service: {container_name}"
                )
                delete_result = subprocess.run(
                    [
                        "gcloud",
                        "run",
                        "services",
                        "delete",
                        container_name,
                        "--platform",
                        "managed",
                        "--region",
                        region,
                        "--quiet",
                    ],
                    capture_output=True,
                    text=True,
                )

                if delete_result.returncode == 0:
                    yield log_status(
                        "success", f"Deleted Cloud Run service: {container_name}"
                    )
                else:
                    yield log_status(
                        "error", f"Failed to delete service: {delete_result.stderr}"
                    )
            else:
                yield log_status(
                    "info", f"No Cloud Run service found: {container_name}"
                )

        except Exception as e:
            yield log_status(
                "error", f"Error checking/deleting Cloud Run service: {e!s}"
            )

        # Clean up container images
        yield log_status("info", "Checking for container images...")
        try:
            images_exist = (
                subprocess.run(
                    [
                        "gcloud",
                        "container",
                        "images",
                        "describe",
                        gcr_image,
                        "--format=json",
                    ],
                    capture_output=True,
                    text=True,
                ).returncode
                == 0
            )

            if images_exist:
                yield log_status("info", f"Deleting container image: {gcr_image}")
                delete_result = subprocess.run(
                    [
                        "gcloud",
                        "container",
                        "images",
                        "delete",
                        gcr_image,
                        "--force-delete-tags",
                        "--quiet",
                    ],
                    capture_output=True,
                    text=True,
                )

                if delete_result.returncode == 0:
                    yield log_status("success", f"Deleted container image: {gcr_image}")
                else:
                    yield log_status(
                        "error", f"Failed to delete image: {delete_result.stderr}"
                    )
            else:
                yield log_status("info", "No container images found")

        except Exception as e:
            yield log_status("error", f"Error cleaning up container images: {e!s}")

        # Clean up local Docker images
        yield log_status("info", "Cleaning up local Docker images...")
        try:
            subprocess.run(
                ["docker", "rmi", container_name],
                capture_output=True,
                text=True,
                check=False,
            )
            subprocess.run(
                ["docker", "rmi", gcr_image],
                capture_output=True,
                text=True,
                check=False,
            )
            yield log_status("success", "Cleaned up local Docker images")
        except Exception as e:
            yield log_status(
                "info", f"Note: Could not clean local Docker images: {e!s}"
            )

        yield log_status("success", "GCP cleanup completed successfully!")

    except FileNotFoundError as e:
        yield log_status("error", f"Configuration error: {e!s}")
    except Exception as e:
        yield log_status("error", f"Unexpected error during cleanup: {e!s}")
