import json
import logging
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Literal, ClassVar, Union, Sequence, Mapping, TypeVar

import numpy as np
import pandas as pd
import plotly.graph_objs as go  # type: ignore

from preswald.engine.service import PreswaldService
from preswald.errors import ValidationError
from preswald.interfaces.workflow import Workflow, WorkflowAnalyzer


# Configure logging
logger = logging.getLogger(__name__)

ComponentType = Literal[
    "alert",
    "button", 
    "checkbox",
    "dag",
    "image",
    "plot",
    "progress",
    "selectbox",
    "separator",
    "slider",
    "spinner", 
    "table",
    "text",
    "text_input"
]

T = TypeVar("T")
TableData = Union[pd.DataFrame, Sequence[Mapping[str, Any]], Sequence[T]]

def convert_to_serializable(obj):
    """Convert numpy arrays and other non-serializable objects to Python native types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64, np.floating)):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.generic):
        if np.isnan(obj):
            return None
        return obj.item()
    return obj

@dataclass
class BaseComponent:
    label: str
    size: float
    type: ClassVar[ComponentType]
    _flex: float = field(init=False, default=1.0)

    def __post_init__(self) -> None:
        self.validate()
        logger.debug(f"Created component: {self.to_dict()}")
        PreswaldService.get_instance().append_component(self)

    @property
    def id(self) -> str:
        """Generate a unique ID for the component"""
        return f"{self.type}-{hashlib.md5(self.label.encode()).hexdigest()[:8]}"

    @property
    def flex(self) -> float:
        """Get the flex value for layout"""
        return self._flex

    def set_flex_from_total(self, total_size: float) -> None:
        """Calculate and set flex value based on total row size"""
        self._flex = self.size / total_size if total_size > 0 else 1.0

    def _validation_error(self, message: str) -> ValidationError:
        """Create a validation error with standardized component context."""
        return ValidationError(
            f"{self.type} component '{self.label}' {message}"
        )

    def validate(self) -> None:
        """Validate component state. Raises ValidationError if invalid."""
        if not 0 < self.size <= 1:
            raise self._validation_error(
                f"has invalid size {self.size}. Size must be between 0 and 1"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            **asdict(self),
            "id": self.id,
            "type": self.type,
            "flex": self.flex,
        }

@dataclass
class Alert(BaseComponent):
    """Alert component for displaying messages to the user."""
    message: str
    level: Literal["info", "warning", "error", "success"] = "info"
    type: ClassVar[Literal["alert"]] = "alert"


@dataclass
class Button(BaseComponent):
    """Button component for user interaction."""
    type: ClassVar[Literal["button"]] = "button"


@dataclass
class Checkbox(BaseComponent):
    """Checkbox component for user interaction."""
    default: bool = False
    value: bool = field(init=False)
    type: ClassVar[Literal["checkbox"]] = "checkbox"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        self.value = current_value if current_value is not None else self.default
        super().__post_init__()


@dataclass
class Image(BaseComponent):
    """Image component for displaying images."""
    src: str
    alt: str = "Image"
    type: ClassVar[Literal["image"]] = "image"


@dataclass
class Plotly(BaseComponent):
    """Component for rendering Plotly figures."""
    figure: go.Figure
    data: dict[str, Any] = field(init=False)
    type: ClassVar[Literal["plot"]] = "plot"

    def __post_init__(self) -> None:
        self.data = self._process_figure()
        super().__post_init__()

    def _process_figure(self) -> dict[str, Any]:
        """Process plotly figure into serializable format."""
        try:
            # Optimize the figure for web rendering
            self._optimize_figure()

            # Convert to dict and clean up
            fig_dict = self.figure.to_dict()
            serializable_fig_dict = convert_to_serializable(fig_dict)

            return {
                "data": serializable_fig_dict.get("data", []),
                "layout": serializable_fig_dict.get("layout", {}),
                "config": {
                    "responsive": True,
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "displaylogo": False,
                    "scrollZoom": True,
                    "showTips": False,
                },
            }

        except Exception as e:
            logger.error(f"[PLOT] Error creating plot: {e!s}", exc_info=True)
            return {"error": f"Failed to create plot: {e!s}"}

    def _optimize_figure(self) -> None:
        """Optimize figure for web rendering."""
        # Reduce precision of numeric values
        for trace in self.figure.data:
            for attr in ["x", "y", "z", "lat", "lon"]:
                if hasattr(trace, attr):
                    values = getattr(trace, attr)
                    if isinstance(values, (list, np.ndarray)):
                        if np.issubdtype(np.array(values).dtype, np.floating):
                            setattr(trace, attr, np.round(values, decimals=4))

            # Optimize marker sizes
            if hasattr(trace, "marker") and hasattr(trace.marker, "size"):
                if isinstance(trace.marker.size, (list, np.ndarray)):
                    sizes = np.array(trace.marker.size)
                    if len(sizes) > 0:
                        max_size = 20
                        with np.errstate(divide="ignore", invalid="ignore"):
                            scaled_sizes = (sizes / max_size) * max_size
                            scaled_sizes = np.nan_to_num(
                                scaled_sizes, nan=0.0, posinf=0.0, neginf=0.0
                            )
                        trace.marker.size = np.clip(scaled_sizes, 1, max_size).tolist()

        # Optimize layout
        if hasattr(self.figure, "layout"):
            self.figure.update_layout(
                margin={"l": 50, "r": 50, "t": 50, "b": 50},
                autosize=True,
                font={"size": 12},
                title={"font": {"size": 14}},
            )


@dataclass
class Progress(BaseComponent):
    """Progress component for displaying progress."""
    default: float = 0.0
    value: float = field(init=False)
    type: ClassVar[Literal["progress"]] = "progress"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        self.value = current_value if current_value is not None else self.default
        super().__post_init__()


@dataclass
class Selectbox(BaseComponent):
    """
    Selectbox component for user interaction.
    
    TODO: Add type for the options
    """
    options: list[Any] = field(default_factory=list)
    default: Any = None
    value: Any = field(init=False)
    type: ClassVar[Literal["selectbox"]] = "selectbox"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        
        if current_value is None:
            current_value = self.default if self.default is not None else (self.options[0] if self.options else None)

        self.value = current_value
        super().__post_init__()


@dataclass
class Separator(BaseComponent):
    """Separator component that forces a new row."""
    type: ClassVar[Literal["separator"]] = "separator"


@dataclass
class Slider(BaseComponent):
    """Slider component for user interaction."""
    step: float = 1.0
    min: float = 0.0
    max: float = 100.0
    default: float | None = None
    value: float = field(init=False)
    type: ClassVar[Literal["slider"]] = "slider"

    def validate(self) -> None:
        super().validate()
        if self.min >= self.max:
            raise self._validation_error(
                f"has invalid range: min value ({self.min}) must be less than max value ({self.max})"
            )
        
        if self.step <= 0:
            raise self._validation_error(
                f"has invalid step: value ({self.step}) must be greater than 0"
            )

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)

        if current_value is None:
            current_value = self.default if self.default is not None else self.min

        self.value = current_value
        super().__post_init__()

@dataclass
class Spinner(BaseComponent):
    """Spinner component for displaying a loading state."""
    type: ClassVar[Literal["spinner"]] = "spinner"


@dataclass
class Table(BaseComponent):
    """Table component that renders data using TableViewerWidget"""
    raw_data: TableData
    data: list[dict[str, Any]] = field(init=False)
    title: str | None = None
    type: ClassVar[Literal["table"]] = "table"

    def __post_init__(self) -> None:
        self.data = self._process_data()
        super().__post_init__()

    def _process_data(self) -> list[dict[str, Any]]:
        # Handle DataFrame
        if isinstance(self.raw_data, pd.DataFrame):
            return self.raw_data.reset_index(drop=True).to_dict("records")

        # Convert to list if not already
        data_list = list(self.raw_data) if isinstance(self.raw_data, Sequence) else [self.raw_data]
        
        # Process each item
        processed: list[dict[str, Any]] = []
        for item in data_list:
            if isinstance(item, Mapping):
                processed_item = self._process_dict(item)
            else:
                processed_item = {"value": self._process_value(item)}
            processed.append(processed_item)

        return processed

    def _process_dict(self, d: Mapping[str, Any]) -> dict[str, Any]:
        return {
            str(k): self._process_value(v)
            for k, v in d.items()
        }

    def _process_value(self, value: Any) -> Any:
        """
        Convert a value to a serializable format
        
        TODO: Add support for more types
        """
        if pd.isna(value):
            return None
        elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
            return str(value)
        elif isinstance(value, (np.integer, np.floating)):
            return value.item()
        elif isinstance(value, (list, np.ndarray)):
            return convert_to_serializable(value)
        else:
            try:
                json.dumps(value)
                return value
            except:
                return str(value)


@dataclass
class Text(BaseComponent):
    """Text/Markdown component for displaying text."""
    markdown: str
    value: str = field(init=False)
    type: ClassVar[Literal["text"]] = "text"

    def __post_init__(self) -> None:
        self.value = self.markdown
        super().__post_init__()


@dataclass
class TextInput(BaseComponent):
    """Text input component for user interaction."""
    placeholder: str
    default: str = ""
    value: str = field(init=False)
    type: ClassVar[Literal["text_input"]] = "text_input"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        self.value = current_value if current_value is not None else self.default
        super().__post_init__()

@dataclass
class WorkflowDAG(BaseComponent):
    """Component for visualizing workflow dependency graphs."""
    workflow: Workflow
    title: str = "Workflow Dependency Graph"
    data: dict[str, Any] = field(init=False)
    type: ClassVar[Literal["dag"]] = "dag"

    def __post_init__(self) -> None:
        self.data = self._process_workflow()
        super().__post_init__()

    def _process_workflow(self) -> dict[str, Any]:
        """Process workflow into visualization data structure."""
        try:
            analyzer = WorkflowAnalyzer(self.workflow)
            analyzer.build_graph()

            # Get node data
            nodes_data = [
                {
                    "name": node,
                    "status": data["status"],
                    "execution_time": data["execution_time"],
                    "attempts": data["attempts"],
                    "error": data["error"],
                    "dependencies": data["dependencies"],
                    "force_recompute": data["force_recompute"],
                }
                for node, data in analyzer.graph.nodes(data=True)
            ]

            return {
                "data": [
                    {
                        "type": "scatter",
                        "customdata": nodes_data,
                        "node": {"positions": []},  # Will be calculated by react-flow
                    }
                ],
                "layout": {
                    "title": {"text": self.title},
                    "showlegend": True,
                },
            }

        except Exception as e:
            logger.error(
                f"[WORKFLOW_DAG] Error creating DAG visualization: {e!s}",
                exc_info=True
            )
            return {
                "error": f"Failed to create DAG visualization: {e!s}"
            }
