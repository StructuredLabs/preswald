from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Welcome to the Ultimate Music Streaming Analysis 🎵")
text("## Exploring Listener Preferences with Interactive Visuals 🚀")

connect()  
df = get_df('sample_csv')


sql = "SELECT * FROM sample_csv WHERE Age > 50"
filtered_df = query(sql, 'sample_csv')

    # Dataset Summary
text("### Quick Summary of the Dataset")
text(f"**Total Records:** {df.shape[0]}")
text(f"**Countries Represented:** {df['Country'].nunique()}")
text(f"**Average Age of Users:** {df['Age'].mean():.2f}")

    # Dynamic Table with Slider
threshold = slider("Discover Weekly Engagement Threshold", min_val=0, max_val=100, default=50)
table(df[df["Discover Weekly Engagement (%)"] > threshold], title="Users Engaging with Discover Weekly")

    # Scatter Plot: Minutes Streamed vs. Repeat Song Rate
fig1 = px.scatter(df, x='Minutes Streamed Per Day', y='Repeat Song Rate (%)', 
                    text='User_ID', title='🎼 Streaming Minutes vs. Repeat Song Rate',
                    labels={'Minutes Streamed Per Day': 'Minutes Streamed', 'Repeat Song Rate (%)': 'Repeat Rate'},
                    color='Repeat Song Rate (%)', size='Minutes Streamed Per Day',
                    hover_name='User_ID', template='plotly_dark')
fig1.update_traces(textposition='top center', marker=dict(size=10, opacity=0.8))
plotly(fig1)

    # Top Streaming Platforms
top_platforms = df['Streaming Platform'].value_counts().reset_index()
top_platforms.columns = ['Streaming Platform', 'User Count']
fig2 = px.bar(top_platforms, x='Streaming Platform', y='User Count',
                title='🔥 Most Popular Streaming Platforms',
                text_auto=True, color='User Count',
                color_continuous_scale='Viridis')
fig2.update_layout(xaxis_tickangle=-45, template='plotly_white')
plotly(fig2)

    # Line Chart: Streaming Trends (If date column exists)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    trend_df = df.groupby('date')['Minutes Streamed Per Day'].sum().reset_index()
    fig3 = px.line(trend_df, x='date', y='Minutes Streamed Per Day', 
                    title='📈 Daily Streaming Trends',
                    labels={'Minutes Streamed Per Day': 'Total Streaming Minutes'}, template='plotly_white')
    plotly(fig3)

    # Table with Filtered Data
table(filtered_df, title="Filtered Data (Users Above 50)")

text("## Conclusion")
text("With these insights, we can see the most popular streaming platforms, user engagement trends, and listener preferences in a visually appealing way. 🚀")
