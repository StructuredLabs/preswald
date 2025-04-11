"""Build utilities for preswald."""

import shutil
import subprocess
import sys
from pathlib import Path


def _run_npm_command(cmd: str, cwd: Path) -> int:
    """Run an npm command in the specified directory."""
    npm_path = shutil.which("npm")
    if not npm_path:
        print("Error: npm not found. Please install npm first.", file=sys.stderr)
        return 1

    result = subprocess.run([npm_path, *cmd.split()], cwd=cwd, check=False)
    return result.returncode


def main():
    """CLI entry point for build commands."""
    if len(sys.argv) < 2:
        print("Usage: python -m preswald.build [frontend|watch|all]")
        return 1

    command = sys.argv[1]
    frontend_dir = Path(__file__).parent.parent / "frontend"

    if not frontend_dir.exists():
        print(f"Frontend directory not found at {frontend_dir}", file=sys.stderr)
        return 1

    if command == "frontend":
        # Install dependencies first
        if _run_npm_command("install", frontend_dir) != 0:
            return 1
        # Then build
        return _run_npm_command("run build", frontend_dir)

    elif command == "watch":
        # Install dependencies first
        if _run_npm_command("install", frontend_dir) != 0:
            return 1
        # Then start watch mode
        return _run_npm_command("run watch", frontend_dir)

    elif command == "all":
        # Build frontend
        if _run_npm_command("install", frontend_dir) != 0:
            return 1
        if _run_npm_command("run build", frontend_dir) != 0:
            return 1

        # Run tests
        if subprocess.run([sys.executable, "-m", "pytest"]).returncode != 0:
            return 1

        print("All build steps completed successfully!")
        return 0

    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
