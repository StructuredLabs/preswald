import pandas as pd
import numpy as np
from preswald import (
    connect,
    get_df,
    query,
    table,
    text,
    slider,
    selectbox,
    plotly
)
import plotly.express as px

def style_plot(fig, title=None):
    # Apply a unified style to all plots (white background, margins, etc.)
    fig.update_traces(marker_line_width=1, marker_line_color="black")
    fig.update_layout(
        title=title if title else fig.layout.title.text,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50),
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    return fig
# Establish connection to Preswald data sources
connect()
# Load the dataset named "heart_attack_prediction_india" from CSV
df = get_df("heart_attack_prediction_india")

text("# Cardiovascular Analysis")

if df is not None:
    table(pd.DataFrame({"Columns": df.columns.tolist()}))
else:
    text("**Error**: Unable to load dataset.")

text("## 1. Aggregation by State_Name")
text("Aggregating average Heart_Attack_Risk and Systolic_BP across states.")
# Aggregation via SQL
sql = """
SELECT
    State_Name,
    AVG(Heart_Attack_Risk) AS avg_risk,
    AVG(Systolic_BP) AS avg_systolic
FROM heart_attack_prediction_india
GROUP BY State_Name
ORDER BY avg_risk DESC
"""
agg_data = query(sql, "heart_attack_prediction_india")
df_agg = pd.DataFrame(agg_data)

table(df_agg, title="Average Risk & Systolic BP by State")

if not df_agg.empty:
    fig_agg = px.bar(
        df_agg,
        x="State_Name",
        y="avg_risk",
        title="Average Heart Attack Risk by State",
        labels={"avg_risk": "Avg Risk"}
    )
    style_plot(fig_agg)
    plotly(fig_agg)
#  Correlation Heatmap
text("## 2. Correlation Heatmap")
text("Examining correlations among key numeric features.")
corr_cols = ["Age", "Systolic_BP", "Diastolic_BP", "Heart_Attack_Risk"]
df_corr = df[corr_cols].apply(pd.to_numeric, errors="coerce").dropna()
corr_matrix = df_corr.corr()

if not df_corr.empty:
    fig_cm = px.imshow(
        corr_matrix,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix"
    )
    fig_cm.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    plotly(fig_cm)
else:
    text("No numeric data found for correlation.")
# Additional Visualizations
text("## 3. Additional Visualizations")

# Pie chart showing heart attack history distribution
if "Heart_Attack_History" in df.columns:
    text("### Heart Attack History Distribution (Pie Chart)")
    fig_pie = px.pie(
        df,
        names="Heart_Attack_History",
        title="Heart Attack History Distribution"
    )
    fig_pie.update_layout(
        title=dict(text="Heart Attack History Distribution", font=dict(size=20, family="Arial Black")),
        font=dict(size=16, family="Arial Black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50)
    )
    plotly(fig_pie)

# Box plot to compare systolic BP by gender
if all(col in df.columns for col in ["Systolic_BP", "Gender"]):
    text("### Systolic BP by Gender (Box Plot)")
    df_box = df.copy()
    df_box["Systolic_BP"] = pd.to_numeric(df_box["Systolic_BP"], errors="coerce")
    df_box.dropna(subset=["Systolic_BP", "Gender"], inplace=True)
    fig_box = px.box(
        df_box,
        x="Gender",
        y="Systolic_BP",
        title="Systolic BP by Gender"
    )
    fig_box.update_layout(
        title=dict(text="Systolic BP by Gender", font=dict(size=20, family="Arial Black")),
        font=dict(size=16, family="Arial Black")
    )
    plotly(fig_box)

# Histogram of Age distribution
if "Age" in df.columns:
    text("### Age Distribution (Histogram)")
    df_hist = df.copy()
    df_hist["Age"] = pd.to_numeric(df_hist["Age"], errors="coerce")
    df_hist.dropna(subset=["Age"], inplace=True)
    fig_hist = px.histogram(df_hist, x="Age", nbins=20, title="Age Distribution")
    fig_hist.update_traces(marker_line_width=1, marker_line_color="black")
    fig_hist.update_layout(
        title="Age Distribution",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(size=16, family="Arial Black")
    )
    fig_hist.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig_hist.update_yaxes(showline=True, linewidth=1, linecolor="black")
    plotly(fig_hist)

# Interactive filter + bubble chart
text("## 4. Age Range Filter + Bubble Chart with Dropdown for Y-axis")
text("Use the sliders to define an Age range and select **any column** from the dataset for the Y-axis.")

all_columns = list(df.columns)
y_axis_choice = selectbox("Select Y-Axis Column", options=all_columns, default="Systolic_BP")

min_age = slider("Minimum Age", min_val=0, max_val=120, default=30)
max_age = slider("Maximum Age", min_val=0, max_val=120, default=60)

df_bubble = df.copy()
df_bubble["Age"] = pd.to_numeric(df_bubble["Age"], errors="coerce")
df_bubble[y_axis_choice] = pd.to_numeric(df_bubble[y_axis_choice], errors="coerce")
df_bubble["Cholesterol_Level"] = pd.to_numeric(df_bubble["Cholesterol_Level"], errors="coerce")

df_bubble.dropna(subset=["Age", y_axis_choice, "Cholesterol_Level"], inplace=True)
df_bubble = df_bubble[(df_bubble["Age"] >= min_age) & (df_bubble["Age"] <= max_age)]

text(f"Showing rows where Age is between {min_age} and {max_age}, plotting Age on X and {y_axis_choice} on Y.")

if not df_bubble.empty:
    table(df_bubble.head(10), title="Sample of Filtered Patients")
    # Bubble chart with Age on X, user-chosen column on Y, bubble size by Cholesterol_Level
    fig_bubble = px.scatter(
        df_bubble,
        x="Age",
        y=y_axis_choice,
        size="Cholesterol_Level",
        color="Gender" if "Gender" in df_bubble.columns else None,
        hover_data=["State_Name"] if "State_Name" in df_bubble.columns else [],
        title=f"Bubble Chart: Age vs. {y_axis_choice} (Bubble Size = Cholesterol_Level)"
    )
    style_plot(fig_bubble)
    plotly(fig_bubble)
else:
    text("No matching data for the chosen filters or columns.")

text("### End of Exploration")
