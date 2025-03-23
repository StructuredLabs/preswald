import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Command, find_packages, setup


class BuildFrontendCommand(Command):
    description = "build frontend assets"
    user_options = []  # noqa: RUF012

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self._build_frontend()
        except Exception as e:
            print(f"Error building frontend: {e!s}", file=sys.stderr)
            raise

    def _build_frontend(self):
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print(f"Frontend directory not found at {frontend_dir}", file=sys.stderr)
            return

        print("Building frontend assets...")
        try:
            # Obtain npm path
            npm_path = shutil.which("npm")
            if not npm_path:
                raise Exception("npm is not installed or not found in PATH")
            # Run npm install with error handling
            result = subprocess.run(
                [npm_path, "install"],
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
                [npm_path, "run", "build"],
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
    # Dependencies that work in browser and server environments
    "pandas>=1.5",
    "toml==0.10.2",
    "plotly==5.24.1",
    "Markdown>=3.4.0",
    # Server-only dependencies
    "fastapi>=0.68.0,<1.0.0; platform_system != 'Emscripten'",
    "uvicorn>=0.15.0,<1.0.0; platform_system != 'Emscripten'",
    "websockets>=10.0,<11.0; platform_system != 'Emscripten'",
    # Native code dependencies
    "duckdb>=1.1.2; platform_system != 'Emscripten'",
    "scipy>=1.15.2; platform_system != 'Emscripten'",
    # Other dependencies
    "httpx>=0.23.0,<1.0.0",
    "python-multipart>=0.0.5,<0.1.0",
    "Jinja2>=3.1.3",
    "click>=8.1.7",
    "networkx>=3.0",
    "Requests>=2.31.0",  # NOTE: maybe need to make this server only as well?
    "setuptools>=69.5.1",
    "tomli>=2.0.1",  # TODO: standardize alongside toml/tomllib
]

# Define additional dependencies for development
DEV_DEPENDENCIES = [
    "pytest>=8.3",
    "build",
    "twine",
    "ruff>=0.1.11",
    "pre-commit>=3.5.0",
]

setup(
    # Basic package metadata
    name="preswald",
    version="0.1.44",
    author="Structured Labs",
    author_email="founders@structuredlabs.com",
    description="A lightweight data workflow SDK.",
    long_description=open("README.md", encoding="utf-8").read(),
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
        "preswald": [
            "static/*",
            "static/assets/*",
            "templates/*",
            "tutorial/*",
            "tutorial/data/*",
            "tutorial/images/*",
        ],
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
