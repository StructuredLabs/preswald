import ast
import contextlib
import io
import logging

import plotly.graph_objects as go
from plotly.io import to_html

from preswald.engine.service import PreswaldService


logger = logging.getLogger(__name__)


def render_fig(fig):
    """
    Convert a Plotly figure to an HTML snippet and print it.
    This helper can be used in notebook cells to display interactive charts.
    """
    if isinstance(fig, go.Figure):
        # Generate HTML snippet (without full HTML wrapper) and include Plotly.js via CDN.
        html = to_html(fig, full_html=False, include_plotlyjs="cdn")
        print(html)
        return html
    else:
        print(fig)
        return str(fig)


def render_df(df):
    """
    Convert a Pandas DataFrame into an HTML table and print it so that the notebook
    output captures and renders it.
    """
    try:
        import pandas as pd

        if isinstance(df, pd.DataFrame):
            # Optionally, add classes for styling.
            html = df.to_html(classes="preswald-table", index=False)
            return html
        else:
            print(df)
            return str(df)
    except Exception as e:
        print("Error rendering DataFrame:", e)
        return ""


def render_text(text_content):
    """
    Convert plain text to HTML and return it for inline rendering.
    """
    html = f"<div class='notebook-text' style='padding: 0.5em; font-family: monospace;'>{text_content}</div>"
    return html


class NotebookSession:
    def __init__(self, script_path: str, client_id: str):
        self.script_path = script_path
        self.client_id = client_id
        self.global_namespace = {}  # Shared state across cells
        self.service = PreswaldService.get_instance()
        # Inject the helper into the namespace so it can be used directly in cells.
        self.global_namespace["render_fig"] = render_fig
        self.global_namespace["render_df"] = render_df
        self.global_namespace["render_text"] = render_text
        self.cells = []

    def start(self):
        logger.info(f"Starting NotebookSession for client {self.client_id}")
        # Optionally, preload the namespace (e.g. execute the script)
        self.global_namespace = {}
        self.global_namespace["render_fig"] = render_fig
        self.global_namespace["render_df"] = render_df
        self.global_namespace["render_text"] = render_text

    def update_cells(self, new_cells):
        """Update the notebook cell definitions and broadcast them."""
        self.cells = new_cells

    async def run_cell(self, cell_id: str, code: str) -> dict:
        logger.info(f"Executing cell {cell_id} for client {self.client_id}")
        output = ""
        error = None
        try:
            # Parse the code into an AST.
            parsed = ast.parse(code, mode="exec")
            if parsed.body:
                last_node = parsed.body[-1]
                # Check if the last node is an expression.
                if isinstance(last_node, ast.Expr):
                    # If it's not an explicit print call, transform it.
                    if not (
                        isinstance(last_node.value, ast.Call)
                        and isinstance(last_node.value.func, ast.Name)
                        and last_node.value.func.id == "print"
                    ):
                        # Create an assignment: _result = <last expression>
                        assign = ast.Assign(
                            targets=[ast.Name(id="_result", ctx=ast.Store())],
                            value=last_node.value,
                        )
                        # Create a new print statement: print(_result)
                        print_stmt = ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id="print", ctx=ast.Load()),
                                args=[ast.Name(id="_result", ctx=ast.Load())],
                                keywords=[],
                            )
                        )
                        # Replace the last node with the assignment and add the print statement.
                        parsed.body[-1] = assign
                        parsed.body.append(print_stmt)
                        # Fix missing location info for all nodes.
                        parsed = ast.fix_missing_locations(parsed)
                        code_to_run = compile(parsed, "<string>", "exec")
                    else:
                        code_to_run = compile(code, "<string>", "exec")
                else:
                    code_to_run = compile(code, "<string>", "exec")
            else:
                code_to_run = compile(code, "<string>", "exec")

            # Execute the code and capture printed output.
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                exec(code_to_run, self.global_namespace)
            output = output_buffer.getvalue()
            logger.info(f"Cell {cell_id} executed successfully, output: {output}")
        except Exception as e:
            error = str(e)
            logger.error(f"Error in cell {cell_id}: {error}")
        return {"cell_id": cell_id, "output": output, "error": error}
