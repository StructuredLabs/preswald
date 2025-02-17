import plotly.express as px

from preswald import (
    Workflow,
    WorkflowAnalyzer,
    connect,
    get_df,
    plotly,
    selectbox,
    separator,
    slider,
    text,
    view,
    workflow_dag,
)


# --- WELCOME MESSAGE ---
text("# 🐵 Welcome to Preswald!")
text(
    "This tutorial app showcases **all the components** available in the Preswald library, with explanations and usage examples. For more details, check out the [GitHub repository](https://github.com/StructuredLabs/preswald) and the [documentation](https://docs.preswald.com)."
)

# --- TEXT COMPONENT ---
text("## 1. Displaying Text with `text()`")
text(
    """
The `text()` function allows you to display formatted text using **Markdown**. You can create headers, lists, and even embed code snippets.

**Example:**

```python
from preswald import text
text("# This is a Header")
text("This is **bold** text, and this is *italic* text.")
```
"""
)

# --- LOADING DATA ---
text("## 2. Viewing Data with `view()`")
text("Let's load a sample dataset and display it using the `view()` component.")

# Load the sample CSV
connect()
df = get_df("sample_csv")

# Displaying the data with `view`
view(df, limit=10)  # Display first 10 rows

text(
    """
The `view()` component displays data in a tabular format.

**Example:**

```python
from preswald import view
view(df, limit=10)
```

- **limit**: Use this parameter to control how many rows to display.
"""
)

# --- PLOTTING DATA ---
text("## 3. Visualizing Data with `plotly()`")
text(
    "Now, let's create an interactive scatter plot using Plotly and embed it using the `plotly()` component."
)

# Create a scatter plot using Plotly Express
fig = px.scatter(
    df,
    x="quantity",
    y="value",
    text="item",
    title="Quantity vs. Value",
    labels={"quantity": "Quantity", "value": "Value"},
)

# Add labels and style the plot
fig.update_traces(textposition="top center", marker={"size": 12, "color": "lightblue"})
fig.update_layout(template="plotly_white")

# Display the plot using plotly()
plotly(fig)

text(
    """
The `plotly()` function embeds interactive Plotly charts into your app.

**Example:**

```python
from preswald import plotly
import plotly.express as px

fig = px.scatter(x=[1, 2, 3], y=[4, 5, 6])
plotly(fig)
```
"""
)

# --- SLIDER COMPONENT ---
text("## 4. Adding Interactivity with `slider()`")
text("Let's add a slider to let users control how many rows of data to display.")

# Create a slider for selecting the number of rows to display
num_rows = slider(
    label="Select number of rows to display",
    min_val=1,
    max_val=len(df),
    step=1,
    default=5,
)

# Display the selected number of rows
view(df.head(num_rows))

text(
    """
The `slider()` component allows users to select a numerical value.

**Example:**

```python
from preswald import slider

value = slider(
    label="Select a value",
    min_val=1,
    max_val=100,
    step=5,
    default=20
)
```

Use the selected value dynamically in your app!
"""
)

# --- SELECTBOX COMPONENT ---
text("## 5. Adding Interactivity with `selectbox()`")
text(
    "Use the dropdown menu below to select a column from the dataset and visualize its distribution."
)

# Create a selectbox for choosing a column to visualize
column_choice = selectbox(
    label="Choose a column to visualize",
    options=df.select_dtypes(include=["number"]).columns.tolist(),
)

# Create and display a histogram based on the selected column
fig = px.histogram(df, x=column_choice, title=f"Distribution of {column_choice}")

# Display the plot
plotly(fig)

text(
    """
The `selectbox()` component allows users to select from a list of options.

**Example:**

```python
from preswald import selectbox

choice = selectbox(
    label="Choose Dataset",
    options=["Dataset A", "Dataset B", "Dataset C"]
)

print(f"User selected: {choice}")
```
In this example, selecting a column updates the histogram dynamically! """
)

# --- SEPARATOR COMPONENT ---
text("## 6. Organizing Content with `separator()`")
text(
    "The `separator()` function adds a simple visual break between sections for better readability."
)

# Display some content
text("### Section 1: Original Data")
view(df.head(5))

# Add a separator to visually break content
separator()

# Display more content after the separator
text("### Section 2: Data Summary")
view(df.describe())

text(
    """
The `separator()` component helps organize your app content by adding visual breaks.

**Example:**

```python
from preswald import separator

text("Section 1 Content")
separator()
text("Section 2 Content")
```

This improves the readability of your app by clearly distinguishing between different sections. """
)


# --- WORKFLOW DAG COMPONENT ---
text("## 7. Visualizing Workflow Dependencies with `workflow_dag()`")
text(
    "The `workflow_dag()` function renders a Directed Acyclic Graph (DAG) to visualize task dependencies in your workflow."
)

# Create a workflow instance
workflow = Workflow()

# Define an atom for loading data


@workflow.atom()
def load_data():
    connect()
    return get_df("sample_csv")


# Define an atom for cleaning data, dependent on load_data


@workflow.atom(dependencies=["load_data"])
def clean_data(load_data):
    return load_data.dropna()


# Define an atom for analyzing data, dependent on clean_data


@workflow.atom(dependencies=["clean_data"])
def analyze_data(clean_data):
    return clean_data.describe()


# Execute the workflow
results = workflow.execute()

# Render the workflow DAG
workflow_dag(workflow, title="Sample Workflow Dependency Graph")

text(
    """
The `workflow_dag()` component helps visualize dependencies and relationships within workflows.

**Example:**

```python
from preswald import workflow_dag, Workflow

workflow = Workflow()

@workflow.atom()
def load_data():
    connect()
    return get_df("sample_csv")

@workflow.atom(dependencies=['load_data'])
def clean_data(load_data):
    return load_data.dropna()

@workflow.atom(dependencies=['clean_data'])
def analyze_data(clean_data):
    return clean_data.describe()

workflow.execute()
workflow_dag(workflow, title="Workflow Dependency Graph")
```

**Key Features:**
- **Visualize Dependencies:** Clearly see how tasks are interconnected.
- **Interactive Exploration:** Zoom, pan, and hover over nodes for details.
- **Customizable Titles:** Make your DAGs more descriptive and easy to understand.
"""
)

# --- WORKFLOW ANALYZER COMPONENT ---
text("## 8. Optimizing Workflows with `WorkflowAnalyzer()`")
text(
    "The `WorkflowAnalyzer()` provides tools to analyze and optimize workflows, helping you identify bottlenecks and parallel execution opportunities."
)

# Initialize the WorkflowAnalyzer
analyzer = WorkflowAnalyzer(workflow)

# Identify and display the critical path
critical_path = analyzer.get_critical_path()
text(f"**Critical Path:** {' → '.join(critical_path)}")

# Visualize the critical path
analyzer.visualize(highlight_path=critical_path, title="Workflow Critical Path")

# Identify and display parallel execution groups
parallel_groups = analyzer.get_parallel_groups()
text("**Parallel Execution Groups:**")
for i, group in enumerate(parallel_groups, 1):
    text(f"- Group {i}: {', '.join(group)}")

text(
    """
The `WorkflowAnalyzer()` helps identify bottlenecks and optimize execution by highlighting critical paths and parallelizable tasks.

**Example:**

```python
from preswald import WorkflowAnalyzer

analyzer = WorkflowAnalyzer(workflow)

# Visualize the workflow
analyzer.visualize(title="Workflow Dependency Graph")

# Display critical path
critical_path = analyzer.get_critical_path()
print("Critical Path:", ' → '.join(critical_path))

# Visualize the critical path
analyzer.visualize(highlight_path=critical_path,
                   title="Workflow Critical Path")

# Display parallel execution groups
parallel_groups = analyzer.get_parallel_groups()
for i, group in enumerate(parallel_groups, 1):
    print(f"Group {i}: {', '.join(group)}")
```

**Key Features:**
- **Critical Path Analysis:** Identify workflow bottlenecks to improve execution time.
- **Parallel Execution Groups:** Highlight tasks that can run in parallel for optimized performance.
- **Interactive DAG Visualization:** Explore workflow dependencies visually to better understand complex processes.
"""
)


# --- RETRY POLICY EXPLANATION ---
text("## 9. Making Workflows More Reliable with `RetryPolicy`")
text(
    """
The `RetryPolicy` helps handle failures in your workflow by automatically retrying tasks if they fail. You can control how many times a task is retried, how long to wait between retries, and which errors should trigger a retry.

### How It Works:
1. **Set a Retry Policy for the Whole Workflow:** This will apply to all tasks unless you override it for specific ones.

```python
from preswald import Workflow, RetryPolicy

policy = RetryPolicy(max_attempts=3, delay=1.0)
workflow = Workflow(default_retry_policy=policy)
```

2. **Override for Specific Tasks:** You can set a different retry rule for individual tasks.

```python
@workflow.atom(retry_policy=RetryPolicy(max_attempts=5, delay=0.5))
def fetch_data():
    raise IOError("Simulated failure")
```

### Why Use `RetryPolicy`?
- **More Reliable:** Automatically retries tasks if something goes wrong.
- **Avoid Infinite Loops:** Limits retries and adds delays between attempts.
- **Customizable:** Set different retry rules for different tasks.

"""
)

# --- FINAL MESSAGE ---
text("## 🎉 You've explored all the components of Preswald!")
text("Now go ahead and build your own interactive data apps!")
