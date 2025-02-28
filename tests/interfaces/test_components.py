import pytest
import pandas as pd
from pytest_mock import MockerFixture
from unittest.mock import Mock, patch
import numpy as np

from preswald.interfaces.components import (
    Checkbox,
    Plotly,
    Slider,
    Table,
    Text,
    WorkflowDAG,
)
from preswald.errors import ValidationError
from preswald.interfaces.workflow import Workflow


@pytest.fixture
def mock_service(mocker: MockerFixture) -> Mock:
    service = mocker.patch('preswald.interfaces.components.PreswaldService')
    mock_instance = Mock()
    service.get_instance.return_value = mock_instance
    mock_instance.get_component_state.return_value = None
    return mock_instance

def test_component_size_validation() -> None:
    """Test that component size must be between 0 and 1"""
    with pytest.raises(ValidationError) as error:
        Text(label="header", size=1.5, markdown="test")
    assert str(error.value) == "text component 'header' has invalid size 1.5. Size must be between 0 and 1"

    with pytest.raises(ValidationError) as error:
        Text(label="footer", size=0, markdown="test")
    assert str(error.value) == "text component 'footer' has invalid size 0. Size must be between 0 and 1"

    with pytest.raises(ValidationError) as error:
        Text(label="sidebar", size=-0.5, markdown="test")
    assert str(error.value) == "text component 'sidebar' has invalid size -0.5. Size must be between 0 and 1"

    # Valid sizes should work
    Text(label="test", size=0.5, markdown="test")
    Text(label="test", size=1.0, markdown="test")
    Text(label="test", size=0.1, markdown="test") 

@pytest.mark.parametrize("service_value, default, expected", [
    (None, False, False),  # No value from service, use default False
    (None, True, True),    # No value from service, use default True
    (True, False, True),   # Service returns True, ignore default False
    (False, True, False),  # Service returns False, ignore default True
])
def test_checkbox_component(
    mock_service: Mock,
    service_value: bool | None,
    default: bool,
    expected: bool
) -> None:
    mock_service.get_component_state.return_value = service_value
    checkbox = Checkbox(label="test", size=1.0, default=default)
    
    # Verify the service was called with the correct ID
    mock_service.get_component_state.assert_called_once_with(checkbox.id)
    assert checkbox.id.startswith("checkbox-")
    assert checkbox.value == expected
    assert checkbox.default == default

class TestSliderComponent:
    def test_slider_component_fails_validation(self) -> None:
        """Fail if min is greater than max"""
        with pytest.raises(ValidationError) as error:
            Slider(
                label="temperature",
                size=1.0,
                min=10,
                max=0,
                step=1,
            )
        assert str(error.value) == "slider component 'temperature' has invalid range: min value (10) must be less than max value (0)"

    def test_slider_component_with_invalid_step(self) -> None:
        """Fail if step is less than or equal to 0"""
        with pytest.raises(ValidationError) as error:
            Slider(
                label="volume",
                size=1.0,
                min=0,
                max=10,
                step=0,
            )
        assert str(error.value) == "slider component 'volume' has invalid step: value (0) must be greater than 0"

    @pytest.mark.parametrize("service_value, default, expected", [
        (None, 0, 0),  # No value from service, use default 0
        (None, 5, 5),    # No value from service, use default 5
        (10, 0, 10),   # Service returns 10, ignore default 0
        (5, 10, 5),  # Service returns 5, ignore default 10
    ])
    def test_slider_component(
        self,
        mock_service: Mock,
        service_value: int | None,
        default: int,
        expected: int
    ) -> None:
        # Configure mock service to return specific value
        mock_service.get_component_state.return_value = service_value

        slider = Slider(
            label="test",
            min=0,
            max=10,
            step=1,
            default=default,
            size=1.0,
        )

        # Verify the service was called with the correct ID
        mock_service.get_component_state.assert_called_once_with(slider.id)
        assert slider.id.startswith("slider-")
        assert slider.value == expected
        assert slider.default == default
        assert slider.min == 0
        assert slider.max == 10


class TestTableComponent:
    def test_table_component_with_dataframe(self) -> None:
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["x", "y", "z"]
        })
        table = Table(label="test", size=1.0, raw_data=df)
        assert len(table.data) == 3
        assert table.data[0] == {"a": 1, "b": "x"}

    def test_table_component_with_dict_list(self) -> None:
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        table = Table(label="test", size=1.0, raw_data=data)
        assert len(table.data) == 2
        assert table.data[0] == {"name": "John", "age": 30}

    def test_table_component_with_primitive_list(self) -> None:
        data = ["a", "b", "c"]
        table = Table(label="test", size=1.0, raw_data=data)
        assert len(table.data) == 3
        assert table.data[0] == {"value": "a"}

    def test_table_component_with_single_object(self) -> None:
        data = {"total": 100}
        table = Table(label="test", size=1.0, raw_data=data)  # type: ignore
        assert len(table.data) == 1
        assert table.data[0] == {"total": 100}

class TestWorkflowDAG:
    @pytest.fixture
    def mock_workflow(self):
        workflow = Mock(spec=Workflow)
        return workflow

    @pytest.fixture
    def mock_analyzer(self):
        with patch('preswald.interfaces.components.WorkflowAnalyzer') as mock:
            analyzer = Mock()
            analyzer.graph.nodes.return_value = [
                ('task1', {
                    'status': 'pending',
                    'execution_time': 0.0,
                    'attempts': 0,
                    'error': None,
                    'dependencies': [],
                    'force_recompute': False
                }),
                ('task2', {
                    'status': 'completed',
                    'execution_time': 1.2,
                    'attempts': 1,
                    'error': None,
                    'dependencies': ['task1'],
                    'force_recompute': False
                })
            ]
            mock.return_value = analyzer
            yield mock

    def test_workflow_dag_creation(self, mock_workflow, mock_analyzer):
        """Test basic creation of WorkflowDAG component"""
        dag = WorkflowDAG(
            label="Test DAG",
            workflow=mock_workflow,
            size=1.0
        )

        # Verify the component was created correctly
        assert dag.type == "dag"
        assert dag.label == "Test DAG"
        assert dag.workflow == mock_workflow
        assert dag.title == "Workflow Dependency Graph"

        # Verify workflow was processed
        assert "data" in dag.data
        assert "layout" in dag.data
        
        # Check data structure
        data = dag.data["data"][0]
        assert data["type"] == "scatter"
        assert len(data["customdata"]) == 2
        assert data["customdata"][0]["name"] == "task1"
        assert data["customdata"][1]["name"] == "task2"

    def test_workflow_dag_with_custom_title(self, mock_workflow, mock_analyzer):
        """Test WorkflowDAG creation with custom title"""
        custom_title = "Custom Workflow Visualization"
        dag = WorkflowDAG(
            label="Test DAG",
            workflow=mock_workflow,
            title=custom_title,
            size=1.0
        )

        assert dag.title == custom_title
        assert dag.data["layout"]["title"]["text"] == custom_title

    def test_workflow_dag_error_handling(self, mock_workflow):
        """Test error handling when workflow processing fails"""
        with patch('preswald.interfaces.components.WorkflowAnalyzer', side_effect=Exception("Test error")):
            dag = WorkflowDAG(
                label="Test DAG",
                workflow=mock_workflow,
                size=1.0
            )

            assert "error" in dag.data
            assert "Failed to create DAG visualization" in dag.data["error"]

    def test_workflow_dag_to_dict(self, mock_workflow, mock_analyzer):
        """Test the to_dict method of WorkflowDAG"""
        dag = WorkflowDAG(
            label="Test DAG",
            workflow=mock_workflow,
            size=1.0
        )

        dag_dict = dag.to_dict()
        assert dag_dict["type"] == "dag"
        assert dag_dict["label"] == "Test DAG"
        assert "data" in dag_dict
        assert "id" in dag_dict

class TestPlotlyComponent:
    @pytest.fixture
    def mock_figure(self):
        figure = Mock()
        figure.data = []
        figure.layout = Mock()
        figure.update_layout = Mock()
        figure.to_dict.return_value = {
            "data": [
                {
                    "type": "scatter",
                    "x": [1, 2, 3],
                    "y": [4, 5, 6],
                    "marker": {"size": [10, 15, 20]},
                }
            ],
            "layout": {"title": "Test Plot"},
        }
        return figure

    def test_plot_creation(self, mock_figure):
        """Test basic creation of Plot component"""
        plot = Plotly(
            label="Test Plot",
            figure=mock_figure,
            size=1.0
        )

        # Verify the component was created correctly
        assert plot.type == "plot"
        assert plot.label == "Test Plot"
        assert plot.figure == mock_figure

        # Verify figure was processed
        assert "data" in plot.data
        assert "layout" in plot.data
        assert "config" in plot.data

        # Check config options
        config = plot.data["config"]
        assert config["responsive"] is True
        assert config["displayModeBar"] is True
        assert "lasso2d" in config["modeBarButtonsToRemove"]
        assert config["scrollZoom"] is True

    def test_plot_optimization(self, mock_figure):
        """Test figure optimization"""
        # Create a figure with data that needs optimization
        mock_figure.data = [Mock()]
        mock_figure.data[0].x = np.array([1.23456789, 2.34567890])
        mock_figure.data[0].marker = Mock()
        mock_figure.data[0].marker.size = np.array([5, 50])  # Should be scaled to 1-20

        plot = Plotly(
            label="Test Plot",
            figure=mock_figure,
            size=1.0
        )

        # Verify layout optimization was called
        mock_figure.update_layout.assert_called_once()
        call_args = mock_figure.update_layout.call_args[1]
        assert "margin" in call_args
        assert "autosize" in call_args
        assert "font" in call_args

    def test_plot_error_handling(self):
        """Test error handling when figure processing fails"""
        mock_figure = Mock()
        mock_figure.to_dict.side_effect = Exception("Test error")

        plot = Plotly(
            label="Test Plot",
            figure=mock_figure,
            size=1.0
        )

        assert "error" in plot.data
        assert "Failed to create plot" in plot.data["error"]

    def test_plot_to_dict(self, mock_figure):
        """Test the to_dict method of Plot"""
        plot = Plotly(
            label="Test Plot",
            figure=mock_figure,
            size=1.0
        )

        plot_dict = plot.to_dict()
        assert plot_dict["type"] == "plot"
        assert plot_dict["label"] == "Test Plot"
        assert "data" in plot_dict
        assert "id" in plot_dict