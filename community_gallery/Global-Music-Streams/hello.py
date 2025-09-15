from preswald import text, plotly, connect, get_df, table, slider
import plotly.express as px

COMMON_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Arial", size=14, color="#333"),
    title_font=dict(size=20, family="Arial", color="#111"),
    xaxis_title_font=dict(size=16, family="Arial"),
    yaxis_title_font=dict(size=16, family="Arial"),
    margin=dict(l=40, r=40, t=60, b=40)
)

text("# User Streaming Behavior Dashboard")
text("This interactive dashboard visualizes user streaming behavior and preferences, including age distribution, streaming habits, and engagement metrics.")

connect()
df = get_df('Global_Music_Streaming_Listener_Preferences')

text("Treemap of Streaming Platforms and Subscription Types")
fig_treemap = px.treemap(df, path=['Country', 'Streaming Platform', 'Subscription Type'],)
plotly(fig_treemap)

text("Sunburst Chart of Streaming Platforms and Subscription Types")
fig_sunburst = px.sunburst(df, path=['Country', 'Streaming Platform', 'Subscription Type'], )
plotly(fig_sunburst)

text("Choropleth Map of Minutes Streamed Per Day by Country")
fig_choropleth = px.choropleth(
    df,
    locations='Country',
    color='Minutes Streamed Per Day',
    hover_name='Country',
    locationmode='country names',
    color_continuous_scale=px.colors.sequential.Plasma,

)
fig_choropleth.update_layout(template="plotly_white")
plotly(fig_choropleth)

text("Minutes Streamed Per Day Distribution")
fig_age = px.histogram(
    df, x="Age", nbins=10,
    labels={"Age": "User Age"}, color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_age.update_layout(**COMMON_LAYOUT)
plotly(fig_age)

text("Average Minutes Streamed Per Day by Country")
avg_minutes = df.groupby("Country")["Minutes Streamed Per Day"].mean().reset_index()
fig_avg_minutes = px.bar(
    avg_minutes, x="Country", y="Minutes Streamed Per Day",
    labels={"Minutes Streamed Per Day": "Avg Minutes per Day"},
    color="Country", color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_avg_minutes.update_layout(**COMMON_LAYOUT)
plotly(fig_avg_minutes)

text("User Count by Streaming Platform")
platform_counts = df["Streaming Platform"].value_counts().reset_index()
platform_counts.columns = ["Streaming Platform", "Count"]
fig_platform = px.bar(
    platform_counts, x="Streaming Platform", y="Count",
    color="Streaming Platform", color_discrete_sequence=px.colors.qualitative.Vivid
)
fig_platform.update_layout(**COMMON_LAYOUT)
plotly(fig_platform)

text("Subscription Type Distribution")
sub_counts = df["Subscription Type"].value_counts().reset_index()
sub_counts.columns = ["Subscription Type", "Count"]
fig_subscription = px.pie(
    sub_counts, values="Count", names="Subscription Type",
    color_discrete_sequence=["#00CC96", "#EF553B"]
)
fig_subscription.update_traces(textposition='inside', textinfo='percent+label')
fig_subscription.update_layout(**COMMON_LAYOUT)
plotly(fig_subscription)

text("Violin Plot of Repeat Song Rate (%) by Top Genre")
fig_violin = px.violin(
    df, x="Top Genre", y="Repeat Song Rate (%)", color="Top Genre",
)
fig_violin.update_layout(**COMMON_LAYOUT)
plotly(fig_violin)

text("Minutes Streamed Per Day vs. Number of Songs Liked")
fig_scatter = px.scatter(
    df, x="Minutes Streamed Per Day", y="Number of Songs Liked",
    color="Subscription Type", hover_data=["User_ID", "Age", "Top Genre"],
    color_discrete_sequence=px.colors.qualitative.Dark2
)
fig_scatter.update_layout(**COMMON_LAYOUT)
plotly(fig_scatter)

text("## Dynamic Data View: Filtered Table based on Age Threshold")
threshold = slider("Threshold", min_val=0, max_val=50, default=50)
filtered_df = df[df["Age"] > threshold]
table(filtered_df, title="Dynamic Data View")
