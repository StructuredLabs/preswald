# Import the Required Components & Libraries Needed
import plotly.express as px

from preswald import connect, get_df, plotly, query, slider, table, text


# Initialize the Connection
connect()
# Load the CSV(You can Change the Data Source in preswald.toml)
df = get_df("sample_csv")

# Manipulate the DataSet Based On Custom SQL Query
sql = "SELECT * FROM sample_csv WHERE Comments < 6376 LIMIT 10;"
# Set the Updated Data Set
filtered_df = query(sql, "sample_csv")

# Set A Title To Your App
text("# Social Media Trends Viewer")
# Display the Filtered Table
table(filtered_df, title="Custom Filtered Data")

# Add a Custom Visualization
text("# Engagement-Based Analysis")
# Create a scatter plot Based On Custom Analysis Requirements & Styling
fig = px.scatter(
    filtered_df,
    x="Content_Type",
    y="Region",
    text="Engagement_Level",
    title="Content-Type vs. Region",
    labels={"content-type": "Content-Type", "region": "Region"},
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=12, color="green"))
# Style the plot
fig.update_layout(template="plotly_white")
# Display the plot
plotly(fig)

# Add a User Control Dynamic Data View
text("# Shares-Trend Analysis")
# Add a User Instruction
text("#Please select the custom slider value below to view the data.")
# Set the values
threshold = slider("shares", min_val=3000, max_val=98000, default=3357)
# Display the Data
table(filtered_df[filtered_df["Shares"] > threshold], title="Dynamic Data View")

# Add a simple visualization
text("# Region-Based Analysis")
# Create a scatter plot
fig = px.scatter(filtered_df, x="Hashtag", y="Platform", color="Region")
# Display the plot
plotly(fig)
