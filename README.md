<p align="center">
  <img src="assets/PreswaldBanner.png" alt="Banner">
</p>


<p align="center">
    <em>Turn Python scripts into interactive data apps and deploy them anywhere in one command.</em>
</p>
<p align="center">
    <a href="LICENSE">
        <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0 License">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/python-3.7%2B-blue.svg" alt="Python Version">
    </a>
    <a href="https://join.slack.com/t/structuredlabs-users/shared_invite/zt-31vvfitfm-_vG1HR9hYysR_56u_PfI8Q">
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
<a href="https://app.preswald.com" target="_blank">
<img src="https://img.shields.io/badge/Cloud-Get Started-orange?style=for-the-badge" alt="Studio">
</a>
<a href="https://cal.com/amruthagujjar" target="_blank">
<img src="https://img.shields.io/badge/Book%20a%20Demo-Schedule-red?style=for-the-badge" alt="Book a Demo">
</a>
</p>

## **What is Preswald?**

Preswald is an open-source framework for building **data apps, dashboards, and internal tools** with just Python. It gives you **pre-built UI components** like tables, charts, and forms, so you don’t have to write frontend code. Users can interact with your app, changing inputs, running queries, and updating visualizations, without you needing to manage the UI manually.

Preswald tracks state and dependencies, so computations update only when needed instead of re-running everything from scratch. It uses a **workflow DAG** to manage execution order, making apps more predictable and performant. Preswald lets you **turn Python scripts into shareable, production-ready applications** easily. 

## **Key Features**

- Add UI components to python scripts – Drop in buttons, text inputs, tables, and charts that users can interact with.
- Stateful execution – Automatically tracks dependencies and updates results when inputs change.
- Structured computation – Uses a DAG-based execution model to prevent out-of-order runs.
- Deploy with one command – Run preswald deploy and instantly share your app online.
- Query and display data – Fetch live data from databases, or local files and display it in a UI.
- Build interactive reports – Create dashboards where users can change filters and see results update.
- Run locally or in the cloud – Start your app on your laptop or host it in Preswald Cloud for easy access.
- Share with a link – No need to send scripts or install dependencies—just share a URL.
- High-performance GPU charts – Render real-time, interactive charts using fastplotlib, with offscreen GPU acceleration and WebSocket-based streaming to the browser.

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
from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

# Create a scatter plot
fig = px.scatter(df, x='quantity', y='value', text='item',
                 title='Quantity vs. Value',
                 labels={'quantity': 'Quantity', 'value': 'Value'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
table(df)
```
### **3. Run Your App**

Now the fun part—see it in action! Run your app locally with:

```bash
preswald run
```

This command launches a development server, and Preswald will let you know where your app is hosted. Typically, it’s here:

```
🌐 App running at: http://localhost:8501
```

Open your browser, and voilà—your first Preswald app is live!

### **4. Deploy Your App to the Cloud**

Preswald provides its own cloud platform for hosting and sharing your applications. You can authenticate with GitHub, create an organization, and generate an API key at [app.preswald.com](https://app.preswald.com). Once set up, deploying is as simple as running:  

```bash
preswald deploy --target structured
```

The first time you deploy, you'll be prompted to enter your **GitHub username** and **Preswald API key**. After that, your app will be built, deployed, and accessible online.  

```
🌐 App deployed at: https://your-app-name-abc123.preswald.app
```

Now your app is live, shareable, and scalable—without any extra setup.


## **🔧 Configuration**

Preswald uses `preswald.toml` for project settings and theming. It’s straightforward, and it makes your app look polished.

### **Sample `preswald.toml`:**

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

[data.sample_csv]
type = "csv"
path = "data/sample.csv"

[logging]
level = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

<br>

## **📚 Documentation**

We’re here to help! Check out our full documentation at [Preswald Docs](https://docs.preswald.com/).

<br>

## **🤝 Contributing**

Check out [CONTRIBUTING.md](CONTRIBUTING.md).

<br>

## **🎉 Join the Community**

- **GitHub Issues**: Found a bug? Let us know [here](https://github.com/StructuredLabs/preswald/issues).
- **Community Forum**: Reach out [here](https://join.slack.com/t/structuredlabs-users/shared_invite/zt-31vvfitfm-_vG1HR9hYysR_56u_PfI8Q)
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

