import os
import numpy as np
from datetime import datetime
from pathlib import Path

FILE_PATH = Path("../data/job_descriptions.csv")


def filter(year: int = 2023, n_elems: int = 16000):
    import pandas as pd

    data = pd.read_csv(FILE_PATH)
    data["Job Posting Date"] = pd.to_datetime(
        data["Job Posting Date"], format="%Y-%M-%d"
    )

    desired_columns = [
        "Salary Range",
        "Country",
        "Work Type",
        "Company Size",
        "Job Posting Date",
        "Job Title",
        "Company",
    ]
    filtered_df = data[desired_columns]
    filtered_df = filtered_df[(filtered_df["Job Posting Date"].dt.year == year)]

    def get_max(s: str):
        elements = s.split("-")
        return int(elements[1][1:-1])

    def get_min(s: str):
        elements = s.split("-")
        return int(elements[0][1:-1])

    filtered_df["Max Salary"] = filtered_df["Salary Range"].apply(get_max)
    filtered_df["Min Salary"] = filtered_df["Salary Range"].apply(get_min)
    filtered_df.drop("Salary Range", inplace=True, axis=1)
    filtered_df.drop("Job Posting Date", inplace=True, axis=1)
    filtered_df = filtered_df.head(n_elems)

    parent_dir = os.path.join(FILE_PATH.parent.absolute(), "job_csv.csv")
    filtered_df.to_csv(parent_dir)
    return f"File saved at {parent_dir}"


if __name__ == "__main__":
    output_dir = os.path.join(FILE_PATH.parent.absolute(), "job_csv.csv")
    if not os.path.exists(output_dir):
        print(filter())
