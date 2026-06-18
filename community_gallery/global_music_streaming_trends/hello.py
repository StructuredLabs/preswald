from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# 🎵 Global Music Streaming Insights")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('Global_Music_Streaming_Listener_Preferences_csv')

#Display Full Dataset
#text("## 📊 Sample Music Streaming Dataset")
#table(df.head(10))

# **Display the Aggregated Data**
text("## 🌍 User Distribution by Country (Filtered by Streaming Time)")
threshold = slider("Adjust Minimum Streaming Minutes Per Day", min_val=0, max_val=600, default=300)

#  **Filter Users Based on Streaming Time**
filtered_df = df[df["Minutes Streamed Per Day"] > threshold]

# ✅ **Group by Country & Count Users Who Meet the Threshold**
country_grouped = filtered_df.groupby("Country").size().reset_index(name="Number of Users")

table(country_grouped)


# ✅ **Listening Habits Over Time of Day**
text("## ☀️🌙 Listening Trends Throughout the Day")

# ✅ **Ensure Proper Ordering of Categories**
time_order = ["Morning", "Afternoon", "Night"]
df["Listening Time (Morning/Afternoon/Night)"] = pd.Categorical(
    df["Listening Time (Morning/Afternoon/Night)"], categories=time_order, ordered=True
)

# ✅ **Count listeners per time category**
time_counts = df["Listening Time (Morning/Afternoon/Night)"].value_counts().reindex(time_order).reset_index()
time_counts.columns = ["Listening Time", "Number of Listeners"]

# ✅ **Use Distinct Colors for Different Times of Day**
color_map = {
    "Morning": "#FFD700",   # Gold for morning ☀️
    "Afternoon": "#FF8C00", # Dark orange for afternoon 🌇
    "Night": "#4169E1"      # Royal blue for night 🌙
}

fig_time = px.bar(
    time_counts,
    x="Listening Time",
    y="Number of Listeners",
    labels={"Listening Time": "Time of Day", "Number of Listeners": "Listener Count"},
    color="Listening Time",
    color_discrete_map=color_map
)

# ✅ **Apply Styling for Better UI**
fig_time.update_layout(
    xaxis_title="Time of Day",
    yaxis_title="Number of Listeners",
    bargap=0.3,  # Adds spacing between bars
    showlegend=False,  # Hides unnecessary legend
    template="plotly_white"  # Clean background
)

# ✅ **Display the Improved Chart**
plotly(fig_time)

# ✅ **1️⃣ Popular Streaming Platforms**
text("## 📊 Most Popular Music Streaming Platforms")

# Aggregate data: Count number of users per platform
platform_counts = df["Streaming Platform"].value_counts().reset_index()
platform_counts.columns = ["Streaming Platform", "Count"]

# Create a vertical bar chart
fig_platform = px.bar(
    platform_counts, 
    x="Count", 
    y="Streaming Platform", 
    labels={"Streaming Platform": "Platform", "Count": "Number of Listeners"},
    color="Streaming Platform"
)

# Show the plot
plotly(fig_platform)

# ✅ **2️⃣ Streaming Time by Age Group**
# ✅ **Create Age Groups**
bins = [13, 18, 25, 32, 40, 50, 60]
labels = ["Teens (13-18)", "Young Adults (19-25)", "Early Adults (26-32)", 
          "Mid Adults (33-40)", "Older Adults (41-50)", "Mature Listeners (51-60)"]

df["Age Group"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)

# ✅ **Aggregate Streaming Time by Age Group**
age_streaming = df.groupby("Age Group")["Minutes Streamed Per Day"].sum().reset_index()

text("## 🎵 Share of Total Streaming Time by Age Group")
# ✅ **Pie Chart: Share of Total Streaming Time**
fig_pie = px.pie(
    age_streaming, 
    names="Age Group", 
    values="Minutes Streamed Per Day",
    labels={"Minutes Streamed Per Day": "Total Minutes Streamed"}
)

plotly(fig_pie)  # ✅ Show Pie Chart

# ✅ **4️⃣ Most Popular Genres by Age Group**
genre_by_age = df.groupby(["Age Group", "Top Genre"]).size().reset_index(name="Count")

# ✅ **Stacked Bar Chart for Popular Genres by Age Group**
text("## 🎵 Popular Music Genres by Age Group")
fig_genres = px.bar(
    genre_by_age, 
    x="Age Group",  
    y="Count",  
    color="Top Genre",  
    labels={"Count": "Listener Count", "Age Group": "Age Category"},
    barmode="stack"
)

plotly(fig_genres)  # ✅ Show Stacked Bar Chart