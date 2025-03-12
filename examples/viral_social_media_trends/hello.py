from preswald import connect, get_df, table, text, selectbox, slider, plotly
import plotly.express as px

connect()

# Load dataset
df = get_df("viral_trends")

# Title and introduction
text("# Viral Social Media Trends Analysis")
text("Explore engagement trends across different social media platforms!")

platform = selectbox("Select Platform", options=df["Platform"].unique(), default="TikTok")

# Filter data by selected platform
filtered_df = df[df["Platform"] == platform]

# Slider for minimum likes threshold
min_likes = slider("Minimum Likes", min_val=0, max_val=int(df["Likes"].max()), default=50000)

# Filter data further
high_engagement_df = filtered_df[filtered_df["Likes"] > min_likes]

# Enhanced scatter plot visualization
fig = px.scatter(
    high_engagement_df,
    x="Views",
    y="Likes",
    color="Hashtag", 
    size="Shares", 
    hover_data=["Post_ID", "Comments", "Engagement_Level"],
    title=f"Engagement Trend for {platform}",
)

fig.update_traces(marker=dict(
    size=9,  
    opacity=0.8,
    line=dict(width=1.5, color="black") 
))

fig.update_layout(
    template="plotly_white",
    xaxis=dict(title="Total Views", tickformat="~s"),
    yaxis=dict(title="Total Likes", tickformat="~s"),
    legend_title="Hashtag",
)

# Display the plot
plotly(fig)

# Display table of filtered data
table(filtered_df, title=f"Trending Posts on {platform}")