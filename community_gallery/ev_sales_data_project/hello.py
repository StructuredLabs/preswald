from preswald import connect, get_df, table, text, slider, selectbox, plotly
import plotly.express as px

# Step 1: Load the dataset
connect()
df = get_df("ev_data_csv")  # Load data

# Step 2: Filter and display limited rows for clarity
filtered_df = df[df["value"] > 500].head(15)  # Limit to top 15 rows for easier viewing

# Step 3: Build an interactive UI
text("# 🌍 EV Sales Analysis")
text("### Overview of EV Sales Across Regions and Years")

# Dropdown to filter by region
region_options = df["region"].unique().tolist()
selected_region = selectbox("Select Region", options=region_options, default="Europe")

# Keep the slider range clean and useful
threshold = slider(
    "Minimum Sales Value", 
    min_val=0, 
    max_val=int(df["value"].max()), 
    default=500
)

# Filter data dynamically based on user input
dynamic_df = df[
    (df["region"] == selected_region) &
    (df["value"] > threshold)
]

# Display the table with limited rows
table(dynamic_df[["year", "region", "powertrain", "value"]].head(10), title=f"Filtered EV Sales Data for {selected_region}")

# Step 4: Create a simple but clean visualization
fig = px.scatter(
    dynamic_df, 
    x="year", 
    y="value", 
    color="powertrain", 
    hover_name="powertrain", 
    title=f"EV Sales Trend ({selected_region})",
    labels={"value": "Number of EVs Sold", "year": "Year"},
)

# Keep the chart visually clean and readable:
fig.update_traces(marker=dict(opacity=0.7))
fig.update_layout(
    template="plotly_white",
    title_font=dict(size=18),
    legend_title="Powertrain Type"
)

plotly(fig)

# Key Insights Section
text("### Key Insights:\n"
     "- EV sales have increased steadily over the years.\n"
     "- Europe and China dominate the global EV market.\n"
     "- Battery Electric Vehicles (BEVs) are the fastest-growing category.\n")