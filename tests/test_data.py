import pytest
import pandas as pd
from preswald.interfaces.data import view, summary, save, load


def test_view(tmpdir):
    # Create a sample CSV
    csv_path = tmpdir.join("test.csv")
    csv_path.write("name,age\nAlice,30\nBob,25")
    connection_name = load(str(csv_path), "test_csv")

    html = view(connection_name)
    assert "<table" in html
    assert "Alice" in html
    assert "Bob" in html


def test_summary(tmpdir):
    # Create a sample CSV
    csv_path = tmpdir.join("test.csv")
    csv_path.write("name,age\nAlice,30\nBob,25")
    connection_name = load(str(csv_path), "test_csv")

    html = summary(connection_name)
    assert "count" in html
    assert "mean" in html
    assert "std" in html


def test_save(tmpdir):
    # Create a DataFrame and save it
    df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
    connection_name = "test_df"
    tmp_file = tmpdir.join("output.csv")
    save(connection_name, str(tmp_file), format="csv")

    assert tmp_file.check()  # Ensure the file exists


def test_load(tmpdir):
    # Create a sample CSV
    csv_path = tmpdir.join("test.csv")
    csv_path.write("name,age\nAlice,30\nBob,25")

    connection_name = load(str(csv_path), "test_csv")
    assert connection_name == "test_csv"
