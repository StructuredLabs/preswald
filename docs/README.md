# Preswald SDK Documentation

---

## **Preswald SDK**

An open-source lightweight SDK for building data workflows. Designed for small teams, solo developers, and startups, Preswald offers a unified framework for data ingestion, transformation, visualization, and deployment.

---

### **Features**

- **Data Ingestion**: Prebuilt connectors for CSV, APIs, Google Sheets, PostgreSQL, and more.
- **Data Transformation**: SQL and Python-based transformations, reusable models, and prebuilt templates.
- **Data Visualization**: Basic dashboards with KPIs, charts, and tables.
- **Pipeline Orchestration**: Simple scheduling and execution of lightweight data pipelines.
- **Deployment**: One-click deployment to Vercel and other cloud platforms.

---

### **Getting Started**

#### **Installation**

Install the Preswald SDK via pip:

```bash
pip install preswald
```

#### **Initialize a Project**

```bash
preswald init sales_analytics
cd sales_analytics
```

#### **Run Locally**

Start the development server:

```bash
preswald run
```

#### **Execute a Pipeline**

```bash
preswald pipeline run load_sales_data
```

#### **Deploy**

Deploy to Vercel with one command:

```bash
preswald deploy
```

---

### **Example Workflow**

#### **Pipeline Definition**

Define your steps for ingestion, transformation, and visualization:

```python
from preswald_sdk.ingestion.csv import from_csv
from preswald_sdk.transformations.pandas_utils import clean_nulls
from preswald_sdk.visualization.dashboard import create_dashboard
from preswald_sdk.pipeline.pipeline import run_pipeline

def load_and_transform_data():
    data = from_csv("data/sales.csv")
    data = clean_nulls(data, ["email"])
    return data

def build_dashboard(data):
    dashboard = create_dashboard(
        title="Sales Overview",
        widgets=[
            {"type": "chart", "data": data, "x": "product", "y": "revenue"},
            {"type": "kpi", "value": "$120,000", "label": "Total Revenue"}
        ]
    )
    dashboard.render("output/dashboard.html")

if __name__ == "__main__":
    run_pipeline([load_and_transform_data, build_dashboard])
```

#### **Pipeline Execution**

Run the pipeline locally:

```bash
python examples/example_pipeline.py
```

---

### **CLI Commands**

| **Command**                     | **Description**                                               |
| ------------------------------- | ------------------------------------------------------------- |
| `preswald init [project_name]`  | Initialize a new project with folder structure and templates. |
| `preswald run`                  | Start a local development server with live updates.           |
| `preswald pipeline run [name]`  | Execute a data pipeline.                                      |
| `preswald deploy`               | Deploy the app to Vercel or other platforms.                  |
| `preswald debug`                | Open an interactive debugging session.                        |
| `preswald api generate [model]` | Generate a shareable API endpoint for a data model.           |
| `preswald dashboard serve`      | Serve a dashboard locally for preview.                        |

---

### **Technical Highlights**

- **Storage**: DuckDB for local prototyping; PostgreSQL, BigQuery, or Snowflake for production.
- **Integration**: GitHub-based authentication for version control.
- **Extensibility**: Plugin architecture for adding custom connectors and visualizations.
- **Deployment**: Dockerized builds with support for AWS, GCP, and Azure.

---

### **Repository Structure**

```
preswald/
│
├── preswald/               # Core SDK code
│   ├── ingestion/              # Data ingestion utilities
│   ├── transformations/        # Data transformation utilities
│   ├── visualization/          # Dashboard and visualization logic
│   ├── pipeline/               # Pipeline orchestration
│
├── examples/                   # Example workflows and pipelines
├── tests/                      # Unit and integration tests
├── README.md                   # Documentation
├── requirements.txt            # Python dependencies
├── setup.py                    # Packaging configuration
└── LICENSE                     # Open-source license (MIT/Apache 2.0)
```

---

### **Contributing**

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request with a detailed description.

---

### **License**

Preswald SDK is open-source under the [MIT License](LICENSE).

---

### **Support**

For issues or feature requests, please open an [issue on GitHub](https://github.com/StructuredLabs/preswald/issues).