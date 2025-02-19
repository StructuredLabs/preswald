import hashlib
import json
import logging
from abc import ABC
from dataclasses import dataclass, asdict, field
from typing import Any, Literal, ClassVar, Union, Sequence, Mapping, TypeVar

import numpy as np
import pandas as pd

from preswald.engine.service import PreswaldService
from preswald.errors import ValidationError


# Configure logging
logger = logging.getLogger(__name__)

ComponentType = Literal[
    "checkbox",
    "slider",
    "button",
    "selectbox",
    "text_input",
    "progress",
    "spinner",
    "alert",
    "image",
    "text",
    "plot",
    "table",
    "dag",
    "separator"
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
class BaseComponent(ABC):
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
            "flex": self.flex,
        }

@dataclass
class CheckboxComponent(BaseComponent):
    default: bool = False
    value: bool = field(init=False)
    type: ClassVar[Literal["checkbox"]] = "checkbox"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        self.value = current_value if current_value is not None else self.default
        super().__post_init__()

@dataclass 
class SliderComponent(BaseComponent):
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
class ButtonComponent(BaseComponent):
    type: ClassVar[Literal["button"]] = "button"

@dataclass
class SelectboxComponent(BaseComponent):
    options: list[Any] = []
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
class TextInputComponent(BaseComponent):
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
class ProgressComponent(BaseComponent):
    default: float = 0.0
    value: float = field(init=False)
    type: ClassVar[Literal["progress"]] = "progress"

    def __post_init__(self) -> None:
        service = PreswaldService.get_instance()
        current_value = service.get_component_state(self.id)
        self.value = current_value if current_value is not None else self.default
        super().__post_init__()

@dataclass
class SpinnerComponent(BaseComponent):
    type: ClassVar[Literal["spinner"]] = "spinner"

@dataclass
class AlertComponent(BaseComponent):
    message: str
    level: Literal["info", "warning", "error", "success"] = "info"
    type: ClassVar[Literal["alert"]] = "alert"

@dataclass
class ImageComponent(BaseComponent):
    src: str
    alt: str = ""
    type: ClassVar[Literal["image"]] = "image"
    
@dataclass
class TextComponent(BaseComponent):
    markdown: str
    value: str = field(init=False)
    type: ClassVar[Literal["text"]] = "text"

    def __post_init__(self) -> None:
        self.value = self.markdown
        super().__post_init__()
    
@dataclass
class SeparatorComponent(BaseComponent):
    type: ClassVar[Literal["separator"]] = "separator"

@dataclass
class TableComponent(BaseComponent):
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
