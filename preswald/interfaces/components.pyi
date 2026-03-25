"""Type stubs for preswald.interfaces.components — the public component API."""

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from preswald.interfaces.component_return import ComponentReturn

def alert(
    message: str,
    level: str = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def big_number(
    value: int | float | str,
    label: str | None = ...,
    delta: str | None = ...,
    delta_color: str | None = ...,
    icon: str | None = ...,
    description: str | None = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def button(
    label: str,
    variant: str = ...,
    disabled: bool = ...,
    loading: bool = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def checkbox(
    label: str,
    default: bool = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def generic(
    content: object,
    mimetype: str,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def image(
    src: str,
    alt: str = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def json_viewer(
    data: Any,
    title: str | None = ...,
    expanded: bool = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def matplotlib(
    fig: plt.Figure | None = ...,
    label: str = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def plotly(
    fig: Any,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def progress(
    label: str,
    value: float = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def selectbox(
    label: str,
    options: list[str],
    default: str | None = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def separator(
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def sidebar(
    defaultopen: bool = ...,
    component_id: str | None = ...,
    logo: str | None = ...,
    name: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def slider(
    label: str,
    min_val: float = ...,
    max_val: float = ...,
    step: float = ...,
    default: float | None = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def spinner(
    label: str = ...,
    variant: str = ...,
    show_label: bool = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def table(
    data: pd.DataFrame,
    title: str | None = ...,
    limit: int | None = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def text(
    markdown_str: str,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def text_input(
    label: str,
    placeholder: str = ...,
    default: str = ...,
    size: float = ...,
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def topbar(
    component_id: str | None = ...,
    **kwargs: Any,
) -> ComponentReturn: ...

def convert_to_serializable(obj: object) -> object: ...
