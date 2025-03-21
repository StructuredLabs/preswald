import os

import pandas as pd


def process_data():
    # Assuming the 'data' folder is in the same directory as this script
    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  # Get the current script directory

    # Correct the file paths
    emissions_df = pd.read_csv(
        os.path.join(base_dir, "data", "facility_data.csv")
    )  # Sheet 1: Emission Data
    point_source_df = pd.read_csv(
        os.path.join(base_dir, "data", "source_attributions.csv")
    )  # Sheet 2: Point Source Data
    plume_df = pd.read_csv(
        os.path.join(base_dir, "data", "plume_detections.csv")
    )  # Sheet 3: Plume Data

    print(emissions_df)

    # Check if the data is loaded properly
    if emissions_df is None or point_source_df is None or plume_df is None:
        raise ValueError("One or more datasets could not be loaded.")

    # Merge the datasets on 'GHGRP ID'
    # Merge emissions data with point source data
    merged_df = emissions_df.merge(point_source_df, on="GHGRP ID", how="left")

    # Merge the result with the plume data
    combined_df = merged_df.merge(plume_df, on="GHGRP ID", how="left")

    # Save the merged dataframe to a CSV file in the 'data' directory
    combined_df.to_csv(os.path.join(base_dir, "data", "combined_data.csv"), index=False)

    return combined_df


process_data()
