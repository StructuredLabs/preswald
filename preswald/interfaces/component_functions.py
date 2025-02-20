"""
Create components using the functional interface
"""

from typing import Literal, Any

import pandas as pd
import plotly.graph_objs as go  # type: ignore

from preswald.interfaces.components import (
    Alert,
    Button,
    Checkbox,
    Image,
    Plotly,
    Progress,
    Selectbox,
    Separator,
    Slider,
    Spinner,
    Table,
    Text,
    TextInput,
    WorkflowDAG,
)
from preswald.interfaces.workflow import Workflow

ComponentDict = dict[str, Any]

def alert(
    message: str,
    level: Literal["info", "warning", "error", "success"] = "info",
    size: float = 1.0
) -> ComponentDict:
    """
    Alert component for displaying messages to the user.
    
    Args:
        message: The message to display in the alert
        level: Alert level ("info", "warning", "error", "success")
        size: Relative size of the component (0-1)
    """
    component = Alert(
        label=message[:20] + "..." if len(message) > 20 else message,  # Use truncated message as label
        message=message,
        level=level,
        size=size
    )
    return component.to_dict()

def button(
    label: str,
    size: float = 1.0
) -> ComponentDict:
    """
    Button component for user interaction.

    Args:
        label: The label of the button
        size: Relative size of the component (0-1)
    """
    component = Button(
        label=label,
        size=size
    )
    return component.to_dict()


def checkbox(
    label: str,
    default: bool = False,
    size: float = 1.0
) -> ComponentDict:
    """
    Checkbox component for user interaction.

    Args:
        label: The label of the checkbox
        default: The default value of the checkbox
        size: Relative size of the component (0-1)
    """
    component = Checkbox(
        default=default,
        label=label,
        size=size
    )
    return component.to_dict()


def image(
    src: str,
    alt: str = "Image",
    size: float = 1.0
) -> ComponentDict:
    """
    Image component for displaying images.

    Args:
        src: The source of the image
        alt: The alternative text for the image
        size: Relative size of the component (0-1)
    """
    component = Image(
        src=src,
        alt=alt,
        label=alt,
        size=size
    )
    return component.to_dict()


def plotly(
    figure: go.Figure,
    size: float = 1.0
) -> ComponentDict:
    """
    Render a Plotly figure.

    Args:
        figure: The Plotly figure to display
        size: Relative size of the component (0-1)
    """
    title = getattr(figure.layout.title, 'text', '') or ''
    component = Plotly(
        figure=figure,
        label=title[:20] + "..." if len(title) > 20 else title,
        size=size
    )
    return component.to_dict()


def progress(
    label: str,
    value: float,
    size: float = 1.0
) -> ComponentDict:
    """
    Progress component for displaying progress.
    """
    component = Progress(
        label=label,
        default=value,
        size=size
    )
    return component.to_dict()


def selectbox(
    label: str,
    options: list[Any],
    default: Any = None,
    size: float = 1.0
) -> ComponentDict:
    """
    Selectbox component for user interaction.

    Args:
        label: The label of the selectbox
        options: The options of the selectbox
        default: The default value of the selectbox
        size: Relative size of the component (0-1)
    """
    component = Selectbox(
        label=label,
        options=options,
        default=default,
        size=size
    )
    return component.to_dict()

def separator(
    size: float = 1.0
) -> ComponentDict:
    """
    Separator component that forces a new row.

    Args:
        size: Relative size of the component (0-1)
    """
    component = Separator(
        label="",
        size=size
    )
    return component.to_dict()

def slider(
    label: str,
    min_val: float,
    max_val: float,
    step: float = 1.0,
    default: float | None = None,
    size: float = 1.0
) -> ComponentDict:
    """
    Slider component for user interaction.

    Args:
        label: The label of the slider
        min_val: The minimum value of the slider
        max_val: The maximum value of the slider
        step: The step value of the slider
        default: The default value of the slider
        size: Relative size of the component (0-1)
    """
    component = Slider(
        label=label,
        min=min_val,
        max=max_val,
        step=step,
        default=default,
        size=size
    )
    return component.to_dict()

def spinner(
    label: str,
    size: float = 1.0
) -> ComponentDict:
    """
    Spinner component for displaying a loading state.

    Args:
        label: The label of the spinner
        size: Relative size of the component (0-1)
    """
    component = Spinner(
        label=label,
        size=size
    )
    return component.to_dict()

def table(
    data: pd.DataFrame | list[Any],
    title: str | None = None,
    limit: int | None = None,
    size: float = 1.0
) -> ComponentDict:
    """
    Table component that renders data using TableViewerWidget

    Args:
        data: The data to display in the table
        title: The title of the table
        limit: The maximum number of rows to display
        size: Relative size of the component (0-1)
    """
    component = Table(
        raw_data=data,
        title=title,
        # limit=limit,
        label=title or "",
        size=size
    )
    return component.to_dict()

def text(
    markdown_str: str,
    size: float = 1.0
) -> ComponentDict:
    """
    Text/Markdown component for displaying text.

    Args:
        markdown_str: The markdown string to display
        size: Relative size of the component (0-1)
    """
    component = Text(
        markdown=markdown_str,
        label=markdown_str[:20] + "..." if len(markdown_str) > 20 else markdown_str,
        size=size
    )
    return component.to_dict()

def text_input(
    label: str,
    placeholder: str,
    size: float = 1.0
) -> ComponentDict:
    """
    Text input component for user interaction.

    Args:
        label: The label of the text input
        placeholder: The placeholder text of the text input
        size: Relative size of the component (0-1)
    """
    component = TextInput(
        label=label,
        placeholder=placeholder,
        size=size
    )
    return component.to_dict()

def workflow_dag(
    workflow: Workflow,
    title: str = "Workflow Dependency Graph",
    size: float = 1.0
) -> ComponentDict:
    """
    Render the workflow's DAG visualization.

    Args:
        workflow: The workflow to visualize
        title: The title of the visualization
        size: Relative size of the component (0-1)
    """
    component = WorkflowDAG(
        workflow=workflow,
        title=title,
        label=title[:20] + "..." if len(title) > 20 else title,
        size=size
    )
    return component.to_dict()
