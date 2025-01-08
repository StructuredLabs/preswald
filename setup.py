from setuptools import setup, find_packages, Command
import subprocess
import os
import shutil
import sys
from pathlib import Path


class BuildFrontendCommand(Command):
    description = "build frontend assets"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self._build_frontend()
        except Exception as e:
            print(f"Error building frontend: {str(e)}", file=sys.stderr)
            raise

    def _build_frontend(self):
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print(f"Frontend directory not found at {frontend_dir}", file=sys.stderr)
            return

        print("Building frontend assets...")
        try:
            # Run npm install with error handling
            result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(f"npm install failed: {result.stderr}", file=sys.stderr)
                raise Exception("npm install failed")

            # Run npm build with error handling
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(f"npm build failed: {result.stderr}", file=sys.stderr)
                raise Exception("npm build failed")

            # Copy the built assets
            self._copy_assets(frontend_dir)

        except subprocess.CalledProcessError as e:
            print(f"Failed to build frontend: {str(e)}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Unexpected error building frontend: {str(e)}", file=sys.stderr)
            raise

    def _copy_assets(self, frontend_dir):
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            raise Exception(f"Build directory not found at {dist_dir}")

        package_static_dir = Path(__file__).parent / "preswald" / "static"
        package_static_dir.mkdir(parents=True, exist_ok=True)

        # Copy dist contents
        print(f"Copying built assets to {package_static_dir}")
        for item in dist_dir.iterdir():
            dest = package_static_dir / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # Copy public assets
        public_dir = frontend_dir / "public"
        if public_dir.exists():
            print("Copying public assets...")
            for item in public_dir.iterdir():
                dest = package_static_dir / item.name
                if not dest.exists():
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)


# Define core dependencies needed for the package to run
CORE_DEPENDENCIES = [
    "fastapi>=0.68.0,<1.0.0",
    "uvicorn>=0.15.0,<1.0.0",
    "websockets>=10.0,<11.0",
    "python-multipart>=0.0.5,<0.1.0",
    "httpx>=0.23.0,<1.0.0",
    "Markdown>=3.4.0",
    "pandas>=1.5",
    "toml==0.10.2",
    "SQLAlchemy==2.0.36",
    "plotly==5.24.1",
    "Jinja2==3.1.4",
    "click==8.1.7",
    "networkx>=3.0",
    "Requests==2.32.3",
    "setuptools==75.1.0",
]

# Define additional dependencies for development
DEV_DEPENDENCIES = [
    "pytest>=8.3",
    "build",
]

setup(
    # Basic package metadata
    name="preswald",
    version="0.1.25",
    author="Structured",
    author_email="founders@structuredlabs.com",
    description="A lightweight data workflow SDK.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/StructuredLabs/preswald",
    license="Apache License 2.0",
    # Package configuration
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    # Package data and dependencies
    include_package_data=True,
    package_data={
        "preswald": ["static/*", "static/assets/*"],
    },
    python_requires=">=3.7",
    # Dependencies
    install_requires=CORE_DEPENDENCIES,
    extras_require={
        "dev": DEV_DEPENDENCIES,
    },
    # Command line interface registration
    entry_points={
        "console_scripts": [
            "preswald=preswald.cli:cli",
        ],
    },
    # Custom commands
    cmdclass={
        "build_frontend": BuildFrontendCommand,
    },
)
