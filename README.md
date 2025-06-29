<p align="center">
  <img src="assets/PreswaldBanner.png" alt="Banner">
</p>


<p align="center">
    <em>Create interactive data apps with a full data stack that runs in the browser (no local dependencies!),runs offline, and is shareable in a single file.
    </em>
</p>
<p align="center">
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0 License">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue.svg" alt="Python Version">
    </a>
    <a href="https://join.slack.com/t/structuredlabs-users/shared_invite/zt-33zwhyv3l-6Xu4bHL6b6~bI3z9fvlUig">
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
<a href="https://preswald.com/dashboard" target="_blank">
<img src="https://img.shields.io/badge/Studio-Get Started-orange?style=for-the-badge" alt="Studio">
</a>
<a href="https://cal.com/amruthagujjar" target="_blank">
<img src="https://img.shields.io/badge/Book%20a%20Demo-Schedule-red?style=for-the-badge" alt="Book a Demo">
</a>
</p>

## **What is Preswald?**

Preswald is a static-site generator for building interactive data apps in Python. It packages compute, data access, and UI into self-contained data apps that run locally in the browser. Built on a WASM runtime with Pyodide and DuckDB, Preswald enables portable, file-based apps that are fast, reactive, and shareable.

You can think of Preswald as a lightweight alternative to heavier web app platforms. It provides built-in UI components and reactive state tracking, so you can use it to build dashboards, reports, prototypes, workflows, and notebooks that are reactive, portable, and secure by default.

Preswald is especially useful when:

- You want to bundle logic, UI, and data into a shareable file
- You need to ship a tool to a stakeholder who shouldn't need to install anything
- You're working with sensitive data and want full local control
- You want to give AI systems structured, modifiable tools

## **Key Features**

- Code-based. Write apps in Python, not in notebooks or JS frameworks
- File-first. One command creates a fully-packaged `.html` app
- Built for computation. Use Pyodide + DuckDB directly in-browser
- Composable UI. Use prebuilt components like tables, charts, forms
- Reactive engine. Only re-run what's needed, powered by a DAG of dependencies
- Local execution. No server. Runs offline, even with large data
- AI-ready. Apps are fully inspectable and modifiable by agents

## Export as a Static App

```bash
preswald export --format html
 ```         
This command builds your app into a static site inside the dist/ directory. The folder contains all the files needed to run your app locally or share it.

⚠️ Note: The --format option is required.
Available formats: html, markdown, pdf.
* Works offline in any modern browser
* Bundles your Python code (via Pyodide), data, and DuckDB queries
* Preserves app UI, logic, and reactive state
* Shareable as a file folder or embeddable in hosting platforms

Example
```bash
preswald export --format markdown
```
## **Installation**

https://pypi.org/project/preswald/

```bash
pip install preswald

or 

uv pip install preswald
```

![Demo GIF](assets/demo1.gif)

## **Quick Start**

```bash
pip install preswald
preswald init my_app
cd my_app
preswald run
```

This will create a folder called `my_app`:

```
my_app/
├── hello.py           # Your app logic
├── preswald.toml      # App metadata and config
├── secrets.toml       # Secrets (e.g. API keys)
├── data/sample.csv    # Input data files
├── images/logo.png    # Custom branding
```

Edit `hello.py` to build your app.

```python
from preswald import text, table, get_df

text("# Hello Preswald")
df = get_df("sample.csv")
table(df)
...
```

Now run your app locally with:

```bash
preswald run
```

This command launches a development server, and Preswald will let you know where your app is hosted. Typically, it’s here:

```
🌐 App running at: http://localhost:8501
```

Open your browser, and voilà—your first Preswald app is live!


## **Configuration**

Preswald uses a simple `preswald.toml` file for configuration. This defines the app's metadata, runtime settings, UI branding, and data sources. Here's a sample:

```
[project]
title = "Preswald Project"
version = "0.1.0"
port = 8501
slug = "preswald-project"
entrypoint = "hello.py"

[branding]
name = "Preswald Project"
logo = "images/logo.png"
favicon = "images/favicon.ico"
primaryColor = "#F89613"

[logging]
level = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## **Use Cases**

- Analyst dashboards. Build data summaries and visualizations. Share as static sites. [Example 1]() [Example 2]() [Example 3]()  
- Interactive reports. Deliver notebooks and reports that update live based on user input. [Example 1]() [Example 2]() [Example 3]()  
- Data inspection tools. Explore files, logs, or snapshots with quick, purpose-built UIs.[Example 1]() [Example 2]() [Example 3]()  
- Offline kits. Package apps for fieldwork or secure / airgap settings. [Example 1]() [Example 2]() [Example 3]()  
- Experiment panels. Compare runs, track metrics, and present results in standalone interactive apps. [Example 1]() [Example 2]() [Example 3]()  

<br>

## **📚 Documentation**

We’re here to help! Check out our full documentation at [Preswald Docs](https://docs.preswald.com/).

<br>

## **🤝 Contributing**

Check out [CONTRIBUTING.md](CONTRIBUTING.md).

<br>

## **🎉 Join the Community**

- **GitHub Issues**: Found a bug? Let us know [here](https://github.com/StructuredLabs/preswald/issues).
- **Community Forum**: Reach out [here](https://join.slack.com/t/structuredlabs-users/shared_invite/zt-33zwhyv3l-6Xu4bHL6b6~bI3z9fvlUig)
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

## ✨ Contributors

Thanks to everyone who has contributed to Preswald 💜

[![](https://contrib.rocks/image?repo=StructuredLabs/preswald)](https://github.com/StructuredLabs/preswald/graphs/contributors)

