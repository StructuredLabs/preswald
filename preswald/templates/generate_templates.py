import json
from pathlib import Path


def generate_template_files(template_dir: Path):
    """Generate template files for a given template directory."""
    # Create hello.py.template
    hello_py = template_dir / "hello.py.template"
    hello_py.write_text("""import preswald

def main():
    preswald.text("Hello, World!")
    preswald.text("This is a template for your Preswald app.")
    preswald.text("Edit this file to create your app.")

if __name__ == "__main__":
    main()
""")

    # Create preswald.toml.template
    preswald_toml = template_dir / "preswald.toml.template"
    preswald_toml.write_text("""[project]
name = "Preswald Project"
slug = "preswald-project"
entrypoint = "hello.py"
port = 8501

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
""")

    # Create sample.csv.template
    sample_csv = template_dir / "sample.csv.template"
    sample_csv.write_text("""name,value
A,1
B,2
C,3
""")


def main():
    # Read templates.json
    templates_path = Path(__file__).parent / "templates.json"
    with open(templates_path) as f:
        templates = json.load(f)["templates"]

    # Create directories and files for each template
    for template in templates:
        template_id = template["id"]
        template_dir = Path(__file__).parent / template_id

        # Create directory if it doesn't exist
        template_dir.mkdir(exist_ok=True)

        # Generate template files
        generate_template_files(template_dir)
        print(f"Generated template files for {template_id}")


if __name__ == "__main__":
    main()
