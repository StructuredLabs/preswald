![Banner](assets/banner.png)

<p align="center">
    <em>🐵 Your lightweight companion for building simple, interactive, and dynamic data apps in Python.</em>
</p>
<p align="center">
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0 License">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue.svg" alt="Python Version">
    </a>
    <a href="https://structured-users.slack.com/join/shared_invite/zt-265ong01f-UHP6BP3FzvOmMQDIKty_JQ#/shared-invite/email">
        <img src="https://img.shields.io/badge/Slack-Join%20Community-orange" alt="Slack Community">
    </a>
    <a href="https://pypi.org/project/preswald/">
        <img src="https://img.shields.io/pypi/v/preswald" alt="PyPI Version">
    </a>
</p>

<p align="center">
<a href="https://preswald.com" target="_blank">
<img src="https://img.shields.io/badge/Landing%20Page-Visit-blue?style=for-the-badge" alt="Website">
</a>
<a href="https://docs.preswald.com" target="_blank">
<img src="https://img.shields.io/badge/Documentation-Read-green?style=for-the-badge" alt="Documentation">
</a>
<a href="https://demo.preswald.com" target="_blank">
<img src="https://img.shields.io/badge/Demo-Try-orange?style=for-the-badge" alt="Demo">
</a>
<a href="https://cal.com/structured" target="_blank">
<img src="https://img.shields.io/badge/Book%20a%20Demo-Schedule-red?style=for-the-badge" alt="Book a Demo">
</a>
</p>

## **What is Preswald?**

Preswald is a full-stack platform for building, deploying, and managing interactive data applications. It combines ingestion, storage, transformation, and visualization into one lightweight and powerful SDK. Whether you're prototyping internal tools or deploying production-grade apps, Preswald reduces complexity and cost without compromising flexibility.

- Code-First Simplicity. Minimal Python and SQL for powerful apps
- End-to-End Coverage. Handle ingestion, ETL, and visualization in one platform
- Efficient by Design. Avoid the sprawling complexity of the modern data stack while keeping what works.
- Connect to CSV, JSON, Parquet, or SQL databases in seconds.
- Fully Customizable Themes. Your app, your brand—just tweak images and names in `preswald.toml`.
- Go live on your machine with a single command.

<br>

<br>

# **🚀 Getting Started**

## **Installation**

First, install Preswald using pip. https://pypi.org/project/preswald/

```bash
pip install preswald
```

![Demo GIF](assets/demo1.gif)

## **👩‍💻 Quick Start**

### **1. Initialize a New Project**

Start your journey with Preswald by initializing a new project:

```bash
preswald init my_project
cd my_project
```

This will create a folder called `my_project` with all the basics you need:

- `hello.py`: Your first Preswald app.
- `preswald.toml`: Customize your app’s settings and style.
- `secrets.toml`: Keep your API keys and sensitive information safe.
- `.gitignore`: Preconfigured to keep `secrets.toml` out of your Git repository.

### **2. Write Your First App**

Time to make something magical! Open up `hello.py` and write:

```python
from preswald import text, view
import pandas as pd

# Render Markdown content
text("# Welcome to Preswald")

# Connect to a CSV file
df = pd.read_csv("data.csv")

# Display the data as a table
view(df)
```

![Demo GIF](assets/demo2.gif)

### **3. Run Your App**

Now the fun part—see it in action! Run your app locally with:

```bash
preswald run hello.py
```

This command launches a development server, and Preswald will let you know where your app is hosted. Typically, it’s here:

```
🌐 App running at: http://localhost:8501
```

Open your browser, and voilà—your first Preswald app is live!

### **4. Deploy Your App to the Cloud**

Once you've built and tested your app locally, deploying it to the cloud is just as simple. Preswald integrates with **Google Cloud Run**, allowing you to host your app in a scalable, serverless environment with just one command.

To deploy your app, set up Google Cloud credentials and a project. Then, run:

```bash
preswald deploy hello.py --project <your-gcp-project>
```

Once deployed, you’ll see a URL where your app is live, for example:

```
🌐 App deployed at: https://your-app-name-abc123.run.app
```

## **💡 Examples**

### **Example 1: Hello World**

```python
from preswald import text

text("# Hello, World!")
```

### **Example 2: Interactive Dashboard**

```python
from preswald import text, slider, view
import pandas as pd


text("# Interactive Dashboard")
slider_value = slider("Rows to Display", min_val=10, max_val=100, step=10, default=50)
data_conn = pd.read_csv("data.csv")
view(data_conn, limit=slider_value)
```

## **🔧 Configuration**

Preswald uses `preswald.toml` for project settings and theming. It’s straightforward, and it makes your app look polished.

### **Sample `preswald.toml`:**

```
[project]
title = "Preswald Project"
version = "0.1.0"
port = 8501

[branding]
name = "Preswald Project"
logo = "images/logo.png"
favicon = "images/favicon.ico"
primaryColor = "#4CAF50"

[logging]
level = "INFO" # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

<br>

## **📚 Documentation**

We’re here to help! Check out our full documentation at [Preswald Docs](https://docs.preswald.com/).

<br>

## **🤝 Contributing**

Preswald thrives on community contributions! Here’s how you can help:

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/StructuredLabs/preswald.git
   ```
3. For local development, with the frontend, run the following commands

   ```
   pip install -e ".[dev]"
   pre-commit install
   python setup.py build_frontend
   python -m build
   pip install dist/preswald-0.xx.xx.tar.gz
   ```

4. Run a test app
   ```
   preswald run examples/earthquakes.py
   ```

### Code Quality

Preswald maintains high code quality standards through automated tools:

- All code is formatted with Black for consistent style
- Imports are organized with isort
- Code is linted with Ruff to catch potential issues

If you're using Preswald in your project, you might want to adopt similar standards. You can use our configuration files as a starting point:

- `.pre-commit-config.yaml` for pre-commit configuration
- `pyproject.toml` for tool settings

These configurations ensure your code remains consistent with our standards when contributing back to the project.

For details, check out [CONTRIBUTING.md](CONTRIBUTING.md).

<br>

## **🎉 Join the Community**

- **GitHub Issues**: Found a bug? Let us know [here](https://github.com/StructuredLabs/preswald/issues).
- **Community Forum**: Reach out [here](https://structured-users.slack.com/join/shared_invite/zt-265ong01f-UHP6BP3FzvOmMQDIKty_JQ#/shared-invite/email)
- **Discussions**: Share your ideas and ask questions in our [discussion forum](https://github.com/StructuredLabs/preswald/discussions).
- **Contributors**: Meet the awesome people who make Preswald better [here](https://github.com/StructuredLabs/preswald/graphs/contributors).

<br>

## **📢 Stay Connected**

<p>
    <a href="https://www.linkedin.com/company/structuredlabs/" target="_blank">
        <img src="https://img.shields.io/badge/Follow%20Us-LinkedIn-blue?style=for-the-badge&logo=linkedin" alt="Follow us on LinkedIn">
    </a>
    <a href="https://x.com/StructuredLabs" target="_blank">
        <img src="https://img.shields.io/badge/Follow%20Us-Twitter-1DA1F2?style=for-the-badge&logo=twitter" alt="Follow us on Twitter">
    </a>
</p>

## **📄 License**

Preswald is licensed under the [Apache 2.0 License](LICENSE).
