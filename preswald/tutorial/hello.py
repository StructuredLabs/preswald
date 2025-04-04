import matplotlib.pyplot as plt
import plotly.express as px

from preswald import (
    Workflow,
    WorkflowAnalyzer,
    alert,
    button,
    chat,
    checkbox,
    connect,
    get_df,
    image,
    matplotlib,
    playground,
    plotly,
    progress,
    selectbox,
    separator,
    sidebar,
    slider,
    spinner,
    table,
    text,
    text_input,
    topbar,
    workflow_dag,
)


# Create a workflow instance
workflow = Workflow()


@workflow.atom()
def render_topbar():
    topbar()


# --- WELCOME MESSAGE ---
@workflow.atom()
def welcome_message():
    text("# Welcome to Preswald!")
    text(
        """
This tutorial app showcases **all the components** available in the Preswald library, with explanations and usage examples. For more details, check out the [GitHub repository](https://github.com/StructuredLabs/preswald) and the [documentation](https://docs.preswald.com).
"""
    )


# --- TEXT COMPONENT ---
@workflow.atom()
def text_component_demo():
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
@workflow.atom()
def load_data():
    text("## 2. Viewing Data with `table()`")
    text("Let's load a sample dataset and display it using the `table()` component.")

    connect()
    df = get_df("sample_csv")
    table(df, limit=10)  # Display first 10 rows

    text(
        """
The `table()` component displays data in a tabular format.
**Example:**
```python
from preswald import table
table(df, limit=10)
```
- **limit**: Use this parameter to control how many rows to display.
"""
    )
    return df


# --- PLOTTING DATA ---
@workflow.atom(dependencies=["load_data"])
def plot_data(load_data):
    df = load_data
    text("## 3. Visualizing Data with `plotly()`")
    text(
        """
Now, let's create an interactive scatter plot using Plotly and embed it using the `plotly()` component.
"""
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
    fig.update_traces(
        textposition="top center", marker={"size": 12, "color": "lightblue"}
    )
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
@workflow.atom(dependencies=["load_data"])
def slider_demo(load_data):
    df = load_data
    text("## 4. Adding Interactivity with `slider()`")
    text("Let's add a slider to let users control how many rows of data to display.")

    # Create a slider for selecting the number of rows to display
    num_rows = slider(
        label="Select number of rows to display",
        min_val=0,
        max_val=len(df),
        step=1,
        default=5,
    )

    # Display the selected number of rows
    table(df.head(num_rows))

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
@workflow.atom(dependencies=["load_data"])
def selectbox_demo(load_data):
    df = load_data
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
@workflow.atom()
def separator_demo():
    text("## 6. Organizing Content with `separator()`")
    text(
        "The `separator()` function adds a simple visual break between sections for better readability."
    )

    # Display some content
    text("### Section 1")
    separator()
    text("### Section 2")

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
This improves the readability of your app by clearly distinguishing between different sections.
"""
    )


# --- IMAGE COMPONENT ---
@workflow.atom()
def image_demo():
    text("## 7. Displaying Images with `image()`")
    text("Let's display an image using the `image()` component.")
    image("https://www.preswald.com/images/Logo.svg")


# --- WORKFLOW DAG COMPONENT ---
@workflow.atom()
def workflow_dag_demo():
    text("## 8. Visualizing Workflow Dependencies with `workflow_dag()`")
    text(
        """
The `workflow_dag()` function renders a Directed Acyclic Graph (DAG) to visualize task dependencies in your workflow.
"""
    )

    # Create a demo workflow for visualization
    demo_workflow = Workflow()

    @demo_workflow.atom()
    def demo_load_data():
        connect()
        return get_df("sample_csv")

    @demo_workflow.atom(dependencies=["demo_load_data"])
    def demo_clean_data(demo_load_data):
        return demo_load_data.dropna()

    @demo_workflow.atom(dependencies=["demo_clean_data"])
    def demo_analyze_data(demo_clean_data):
        return demo_clean_data.describe()

    # Execute the demo workflow
    demo_workflow.execute()

    # Render the workflow DAG
    workflow_dag(demo_workflow, title="Sample Workflow Dependency Graph")

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
@workflow.atom(dependencies=["workflow_dag_demo"])
def workflow_analyzer_demo():
    text("## 9. Optimizing Workflows with `WorkflowAnalyzer()`")
    text(
        "The `WorkflowAnalyzer()` provides tools to analyze and optimize workflows, helping you identify bottlenecks and parallel execution opportunities."
    )

    # Initialize the WorkflowAnalyzer with the main tutorial workflow
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
@workflow.atom()
def retry_policy_demo():
    text("## 10. Making Workflows More Reliable with `RetryPolicy`")
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


@workflow.atom()
def alert_demo():
    text("## 11. Displaying Alerts with `alert()`")
    text(
        "The `alert()` function displays a message to the user, which can be used to provide information, warnings, or errors."
    )
    alert("hi", 1.0)


@workflow.atom()
def checkbox_demo():
    text("## 12. Adding Interactivity with `checkbox()`")
    text(
        "The `checkbox()` function allows users to select or deselect an option using a checkbox."
    )

    # Simple checkbox example
    is_selected = checkbox(label="Select me!")

    # Show the checkbox state
    if is_selected:
        text("✅ Checkbox is selected!")
    else:
        text("⬜ Checkbox is not selected")

    text(
        """
The `checkbox()` component creates an interactive checkbox input.
**Example:**
```python
from preswald import checkbox

# Basic usage
is_checked = checkbox(
    label="Enable feature",
    default=False
)

# Use the checkbox value in your app
if is_checked:
    # Do something when checked
    print("Feature enabled!")
```

The checkbox returns a boolean value that you can use to control your app's behavior.
"""
    )


@workflow.atom()
def progress_demo():
    text("## 13. Tracking Progress with `progress()`")
    text(
        "The `progress()` function displays a progress bar to indicate the completion status of a task."
    )
    progress(label="Progress", value=80)


@workflow.atom()
def sidebar_demo():
    text("## 14. Showing sidebar to your app with sidebar()")
    sidebar(defaultopen=True)


@workflow.atom()
def playground_demo():
    text("## 15. Interacting with SQL queries using `playground()` component")
    text(
        "The `playground` function provides a dynamic interface for querying connected data sources and visualizing results directly."
    )

    df = playground(label="Playground Example", query="SELECT * FROM sample_csv")
    text(f"Total Items: {df.shape[0]}")


@workflow.atom()
def chat_demo():
    text("## 16. Chat with your data using `chat()`")
    text(
        "The `chat()` function allows you to chat with your data using a chat interface."
    )
    chat("sample_csv")


@workflow.atom()
def matplotlib_demo():
    text("## 17. Visualizing data using `matplotlib()`")
    text("The `matplotlib()` function allows you to visualize data using matplotlib.")
    fig = plt.figure()
    plt.plot([1, 2, 3, 4, 5])
    matplotlib(fig)


@workflow.atom()
def button_demo():
    text("## 18. Adding Interactivity with `button()`")
    text(
        "The `button()` function creates a simple interactive button. Here's an example:"
    )

    # Simple button example
    clicked = button(label="Click me!")

    # Show the button state
    if clicked:
        text("Button was clicked!")
    else:
        text("Click the button!")


@workflow.atom()
def spinner_demo():
    text("## 19. Adding a spinner with `spinner()`")
    text(
        "The `spinner()` function creates a loading indicator. Here are some examples:"
    )

    # Default spinner
    spinner(label="Loading data...")

    # Card variant with a different message
    spinner(label="Processing request...", variant="card")


@workflow.atom()
def text_input_demo():
    text("## 20. Adding a text input with `text_input()`")
    text(
        "The `text_input()` function creates a text input field that returns its current value."
    )

    # Get user's name
    name = text_input(
        label="What's your name?",
        placeholder="Enter your name here",
        default="",
    )

    # Show a greeting if they've entered a name
    if name:
        text(f"👋 Hello, {name}!")


# --- FINAL MESSAGE ---
@workflow.atom()
def final_message():
    text("## 🎉 You've explored all the components of Preswald!")
    text("Now go ahead and build your own interactive data apps!")


# Execute the workflow
results = workflow.execute()
