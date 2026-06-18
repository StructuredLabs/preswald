from datetime import datetime
import pandas as pd
import plotly.express as px

from preswald import (
    button,
    connect,
    get_df,
    plotly,
    selectbox,
    table,
    text,
)

px.defaults.template = "plotly_white"
COLORS = px.colors.qualitative.Bold

connect()

try:
    # Load the dataset configured in preswald.toml (e.g., "Indian_Traffic_Violations")
    df = get_df("Indian_Traffic_Violations_csv")
    original_df = df.copy()
except Exception as e:
    text(f"# ⚠️ Error loading dataset: {e!s}")
    df = pd.DataFrame({
        "Violation_Type": ["Error"],
        "Date": ["Error"],
        "State": ["Error"],
        "Vehicle_Type": ["Error"],
    })
    original_df = df.copy()

# Dashboard Title & Overview
text("# 🚦 Indian Traffic Violations Analysis Dashboard")
text("This dashboard provides insights into the traffic violations data across India.")

# Optional: Filter by State if available in the dataset
if "State" in df.columns:
    states = sorted(df["State"].dropna().unique().tolist())
    all_states = "All States"
    state_options = [all_states] + states
    selected_state = selectbox("Filter by State", options=state_options, default=all_states)
    if button("Apply Filters"):
        filtered_df = original_df.copy()
        if selected_state != all_states:
            filtered_df = filtered_df[filtered_df["State"] == selected_state]
        df = filtered_df
        text(f"**Filtered dataset: {len(df):,} records**")
    else:
        text(f"**Showing all {len(df):,} records**")
else:
    text(f"**Dataset contains {len(df):,} records.**")

# Basic Dataset Overview
total_records = len(df)
if "Violation_Type" in df.columns:
    unique_violations = df["Violation_Type"].nunique()
else:
    unique_violations = "N/A"
text(f"**Total Violations:** {total_records:,}  |  **Unique Violation Types:** {unique_violations}")

# Select Dashboard View
current_tab = selectbox(
    "Dashboard View",
    options=[
        "📊 Violation Type Analysis",
        "🕒 Temporal Trends",
        "🚗 Vehicle Type Analysis"
    ],
    default="📊 Violation Type Analysis",
)

# View 1: Violation Type Analysis
if current_tab == "📊 Violation Type Analysis":
    text("## 📊 Violation Type Analysis")
    if "Violation_Type" in df.columns:
        violation_counts = df["Violation_Type"].value_counts().reset_index()
        violation_counts.columns = ["Violation_Type", "Count"]
        fig_bar = px.bar(
            violation_counts,
            x="Violation_Type",
            y="Count",
            title="Frequency of Traffic Violations",
            labels={"Violation": "Violation Type", "Count": "Number of Violations"}
        )
        plotly(fig_bar)
        table(violation_counts, title="Violation Frequency Table")
    else:
        text("**Note:** No 'Violation' column found in the dataset.")

# View 2: Temporal Trends
elif current_tab == "🕒 Temporal Trends":
    text("## 🕒 Temporal Trends")
    # Attempt to identify a date column (e.g., "Date")
    date_col = None
    for col in df.columns:
        if "date" in col.lower():
            date_col = col
            break
# prswld-59ba54dd-a823-4e67-a918-ae8d06586137
    if date_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df_time = df.dropna(subset=[date_col]).copy()
            # Group by month for better aggregation
            df_time["Month"] = df_time[date_col].dt.to_period("M").dt.to_timestamp()
            time_counts = df_time.groupby("Month").size().reset_index(name="Count")
            # Limit to the last 50 months
            time_counts = time_counts.sort_values("Month").tail(50)
            fig_line = px.line(
                time_counts,
                x="Month",
                y="Count",
                title="Traffic Violations Over Time (Monthly Aggregation)",
                labels={"Month": "Month", "Count": "Number of Violations"}
            )
            plotly(fig_line)
            table(time_counts, title="Monthly Violations Count (Last 50)")
        except Exception as e:
            text(f"**Error processing date column:** {e!s}")
    else:
        text("**Note:** No date column found in the dataset.")
# View 3: Vehicle Type Analysis
elif current_tab == "🚗 Vehicle Type Analysis":
    text("## 🚗 Vehicle Type Analysis")
    if "Vehicle_Type" in df.columns:
        vehicle_counts = df["Vehicle_Type"].value_counts().reset_index()
        vehicle_counts.columns = ["Vehicle Type", "Count"]
        fig_pie = px.pie(
            vehicle_counts,
            names="Vehicle Type",
            values="Count",
            title="Distribution of Vehicle Types Involved in Violations",
            hole=0.4,
            color_discrete_sequence=COLORS,
        )
        plotly(fig_pie)
        table(vehicle_counts, title="Vehicle Type Frequency")
    else:
        text("**Note:** No 'Vehicle_Type' column found in the dataset.")

# Footer / About
text("---")
text("### About this Dashboard")
text("This dashboard provides insights into traffic violations data across India, analyzing violation types, temporal trends, and vehicle types involved. Adjust filters to explore the data further.")