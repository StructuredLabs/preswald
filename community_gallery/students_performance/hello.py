
from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Connect to the dataset
connect()
df = get_df('sample_csv')

# Display the full dataset
text("# Student Attendance and Final_Score Performance Analysis")
table(df, title="Full Student Dataset")

# Filter the dataset for relevant columns
df_filtered = df[['Attendance (%)', 'Final_Score']]

# Add a slider for Attendance threshold
attendance_threshold = slider(
    "Select Minimum Attendance (%)",  # Slider label
    min_val=0,                        # Minimum value
    max_val=100,                      # Maximum value
    default=50                        # Default value
)

# Filter the dataset based on the slider value
filtered_df = df_filtered[df_filtered['Attendance (%)'] >= attendance_threshold]


# Heatmap of Attendance vs. Final_Score
heatmap_fig = px.density_heatmap(
    filtered_df,
    x='Attendance (%)',
    y='Final_Score',
    title=f'Attendance vs. Final Score (Heatmap, Attendance >= {attendance_threshold}%)',
    labels={'Attendance (%)': 'Attendance (%)', 'Final_Score': 'Final_Score'},
    color_continuous_scale='Viridis'  # Use a color scale for better visualization
)

heatmap_fig.update_layout(
    template='plotly_white',
    height=500,
    width=800,
    title_x=0.5
)
plotly(heatmap_fig)
