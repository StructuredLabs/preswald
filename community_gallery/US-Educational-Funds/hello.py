from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app.")


connect()
# Load districts, statesm neap datasets 
df_districts = get_df("districts")
df_states = get_df("states")
df_naep = get_df("naep")


datasets = {"districts": df_districts, "states": df_states, "naep": df_naep}
for name, df in datasets.items():
    if df is None or df.empty:
        text(f"{name} dataset failed to load or is empty. Please check `preswald.toml` paths.")
    else:
        text(f"{name} dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")

# Rename the column Names for Merging
if df_districts is not None and not df_districts.empty:
    df_districts.rename(columns={"YRDATA": "YEAR"}, inplace=True)

if df_districts is not None and not df_districts.empty:
    df_districts.rename(columns={"ENROLL": "ENROLL_DISTRICTS"}, inplace=True)

if df_states is not None and not df_states.empty:
    df_states.rename(columns={"ENROLL": "ENROLL_STATES"}, inplace=True)  # No changes needed

# Ensure YEAR, ENROLL_DISTRICTS and ENROLL_STATES Columns Exists Before Converting
for name, df in datasets.items():
    if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
        if "YEAR" in df.columns:
            df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")
            
        if "ENROLL_DISTRICTS" in df.columns:
            df["ENROLL_DISTRICTS"] = pd.to_numeric(df["ENROLL_DISTRICTS"], errors="coerce")

        if "ENROLL_STATES" in df.columns:
            df["ENROLL_STATES"] = pd.to_numeric(df["ENROLL_STATES"], errors="coerce")


# Merge District and State-Level Data
df_combined = None
if df_districts is not None and not df_districts.empty and df_states is not None and not df_states.empty:
    if "STATE" in df_districts.columns and "STATE" in df_states.columns:
        df_combined = pd.merge(df_districts, df_states, on=["STATE", "YEAR"], how="outer")
    else:
        text("Cannot merge district and state data. Missing `STATE` column.")

# Merge with Standardized Test Scores Data
if df_combined is not None and df_naep is not None and not df_naep.empty:
    if "STATE" in df_naep.columns and "YEAR" in df_naep.columns:
        df_combined = pd.merge(df_combined, df_naep, on=["STATE", "YEAR"], how="outer")
    else:
        text("NAEP dataset missing required columns.")

# Handle Missing Values
if df_combined is not None and not df_combined.empty:
    # df_combined.fillna(1, inplace=True)
    df_combined["ENROLL_DISTRICTS"].fillna(1, inplace=True)
    df_combined["ENROLL_STATES"].fillna(1, inplace=True)

    # Calculate Per-Student Spending & Performance Metrics
    if "ENROLL_DISTRICTS" in df_combined.columns and "ENROLL_STATES" in df_combined.columns:
        df_combined["Per Student Expenditure (District)"] = df_combined["TOTAL_EXPENDITURE"] / df_combined["ENROLL_DISTRICTS"]
        df_combined["Revenue Per Student (District)"] = df_combined["TOTAL_REVENUE"] / df_combined["ENROLL_DISTRICTS"]
        df_combined["Per Student Expenditure (State)"] = df_combined["TOTAL_EXPENDITURE"] / df_combined["ENROLL_STATES"]
        df_combined["Revenue Per Student (State)"] = df_combined["TOTAL_REVENUE"] / df_combined["ENROLL_STATES"]
        
        df_combined["Weighted Per Student Expenditure"] = (
            (df_combined["Per Student Expenditure (District)"] * df_combined["ENROLL_DISTRICTS"]) + 
            (df_combined["Per Student Expenditure (State)"] * df_combined["ENROLL_STATES"]) 
        ) / (df_combined["ENROLL_DISTRICTS"] + df_combined["ENROLL_STATES"])

    # Visualization - Revenue vs. Expenditure Trend
    if "TOTAL_REVENUE" in df_combined.columns and "TOTAL_EXPENDITURE" in df_combined.columns:
        text("## Revenue vs. Expenditure Trend")
        fig2 = px.line(df_combined, x='TOTAL_REVENUE', y='TOTAL_EXPENDITURE', 
                          color='STATE', 
                          title="State-Wise Revenue vs. Expenditure",
                          labels={'TOTAL_REVENUE': 'Total Revenue ($B)', 'TOTAL_EXPENDITURE': 'Total Expenditure ($B)'})
        plotly(fig2)
    
    # Student Performance vs. Spending (State-Level)
    if "Per Student Expenditure (State)" in df_combined.columns and "AVG_SCORE" in df_combined.columns:
        text("## Student Performance vs. Spending (State-Level)")
        fig3 = px.scatter(df_combined, x='Per Student Expenditure (State)', y='AVG_SCORE', 
                          color='STATE',
                          title="Impact of Per-Student Spending on Test Scores (State-Level)",
                          labels={'Per Student Expenditure (State)': 'Per Student Spending ($)', 'AVG_SCORE': 'Average Test Score'})
        plotly(fig3)
    
    # Student Performance vs. Spending (District-Level)
    if "Per Student Expenditure (District)" in df_combined.columns and "AVG_SCORE" in df_combined.columns:
        text("## Student Performance vs. Spending (District-Level)")
        fig4 = px.scatter(df_combined, x='Per Student Expenditure (District)', y='AVG_SCORE', 
                          color='STATE',
                          title="Impact of Per-Student Spending on Test Scores (District-Level)",
                          labels={'Per Student Expenditure (District)': 'Per Student Spending ($)', 'AVG_SCORE': 'Average Test Score'})
        plotly(fig4)
else:
    text("Data merging failed. No analysis or visualization can be generated.")