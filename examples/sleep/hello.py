import pandas as pd
import plotly.express as px
import numpy as np
from preswald import connect, get_df, plotly, text, slider, table

connect()
df = get_df("sleep_data")
df.columns = df.columns.str.replace(" ", "_")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Project Heading and Description
text("# Sleep, Mood & Productivity Dashboard")
text("Explore the connection between your sleep, mood, stress, and productivity.")

# 1. Sleep Duration Impact on Mood Score
text("## 1. Sleep Duration Impact on Mood Score")
df["Sleep_Hours_Bin"] = df["Total_Sleep_Hours"].round(0)
mood_trend = df.groupby("Sleep_Hours_Bin", as_index=False).agg({"Mood_Score": "mean"})
fig1 = px.scatter(
    df,
    x="Total_Sleep_Hours",
    y="Mood_Score",
    title="Impact of Sleep Duration on Mood Score",
    labels={"Total_Sleep_Hours": "Total Sleep Hours", "Mood_Score": "Mood Score"},
    opacity=0.6
)
fig1.add_scatter(
    x=mood_trend["Sleep_Hours_Bin"],
    y=mood_trend["Mood_Score"],
    mode="lines+markers",
    name="Average Mood",
    line=dict(width=3)
)
fig1.update_layout(template="plotly_white", title="Impact of Sleep Duration on Mood Score")
fig1.update_xaxes(title_text="Total Sleep Hours")
fig1.update_yaxes(title_text="Mood Score")
plotly(fig1)

# 2. Stress Level vs Total Sleep Hours
text("## 2. Stress Level vs Total Sleep Hours")
df["Sleep_Hours_Bin"] = df["Total_Sleep_Hours"].round(0)
stress_trend = df.groupby("Sleep_Hours_Bin", as_index=False).agg({"Stress_Level": "mean"})
fig2 = px.line(
    stress_trend,
    x="Sleep_Hours_Bin",
    y="Stress_Level",
    title="Average Stress Level by Total Sleep Hours",
    labels={"Sleep_Hours_Bin": "Total Sleep Hours (Binned)", "Stress_Level": "Average Stress Level"},
    markers=True
)
fig2.update_traces(line={"width": 3}, marker={"size": 8})
fig2.update_layout(template="plotly_white", title="Average Stress Level by Total Sleep Hours")
fig2.update_xaxes(title_text="Total Sleep Hours (Binned)")
fig2.update_yaxes(title_text="Average Stress Level")
plotly(fig2)

# 3. Total Sleep Hours vs Productivity Score (with slider control)
text("## 3. Total Sleep Hours vs Productivity Score")
threshold = slider("Productivity Score Threshold", min_val=0, max_val=9, default=5)
df_q3 = df[["Total_Sleep_Hours", "Productivity_Score"]].dropna()
df_q3_filtered = df_q3[df_q3["Productivity_Score"] > threshold]
table(df_q3_filtered, title="Data Points with Productivity Score above Threshold")
fig3 = px.scatter(
    df_q3_filtered,
    x="Total_Sleep_Hours",
    y="Productivity_Score",
    title="Relationship between Total Sleep Hours and Productivity Score",
    labels={"Total_Sleep_Hours": "Total Sleep Hours", "Productivity_Score": "Productivity Score"},
    opacity=0.7
)
if df_q3_filtered.shape[0] > 1:
    slope3, intercept3 = np.polyfit(df_q3_filtered["Total_Sleep_Hours"], df_q3_filtered["Productivity_Score"], 1)
    line_x3 = np.linspace(df_q3_filtered["Total_Sleep_Hours"].min(), df_q3_filtered["Total_Sleep_Hours"].max(), 100)
    line_y3 = slope3 * line_x3 + intercept3
    fig3.add_scatter(x=line_x3, y=line_y3, mode="lines", name="Fit Line", line=dict(width=3))
fig3.update_layout(template="plotly_white", title="Relationship between Total Sleep Hours and Productivity Score")
fig3.update_xaxes(title_text="Total Sleep Hours")
fig3.update_yaxes(title_text="Productivity Score")
plotly(fig3)

# 4. Sleep Quality Distribution by Age Group
text("## 4. Sleep Quality Distribution by Age Group")
if "Age_Group" not in df.columns:
    df["Age_Group"] = pd.cut(df["Age"], bins=[0, 25, 35, 45, 55, 100], labels=["0-25", "26-35", "36-45", "46-55", "56+"])
fig4 = px.violin(
    df,
    x="Age_Group",
    y="Sleep_Quality",
    box=True,
    points="all",
    title="Sleep Quality Distribution by Age Group",
    labels={"Age_Group": "Age Group", "Sleep_Quality": "Sleep Quality"}
)
fig4.update_layout(template="plotly_white", title="Sleep Quality Distribution by Age Group")
fig4.update_xaxes(title_text="Age Group")
fig4.update_yaxes(title_text="Sleep Quality")
plotly(fig4)
