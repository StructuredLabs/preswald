from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px
from preswald import query

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df("music_csv")
# Create table 1
sql = """
WITH ArtistCounts AS (
    SELECT 
        Country,
        Most_Played_Artist,
        COUNT(*) AS Artist_Count
    FROM music_csv
    WHERE Minutes_Streamed_Per_Day > 30
    GROUP BY Country, Most_Played_Artist
),
RankedArtists AS (
    SELECT 
        Country,
        Most_Played_Artist,
        Artist_Count,
        RANK() OVER (PARTITION BY Country ORDER BY Artist_Count DESC) AS Rank
    FROM ArtistCounts
)
SELECT Country, Most_Played_Artist
FROM RankedArtists
WHERE Rank <= 5
ORDER BY Country, Rank
"""
filtered_df = query(sql, "music_csv")
text("# Music Analysis Trends")
text("Top 5 Artists Per Country")
# Create table of top 5 artists by country
text("Listeners had to listen for at least 30 minutes")
table(filtered_df, title="Filtered Data")

#figure 1
threshold = slider("Threshold", min_val=12, max_val=60, default=30)
# Create a bar plot of top genres by age
text("## Top Genre Variation By Age")
text("Top Genre changes as younger ages get excluded")
fig1 = px.histogram(df[df["Age"] > threshold], x="Top_Genre", text_auto=True)
plotly(fig1)

#figure 2
sql2 = "SELECT Subscription_Type, Minutes_Streamed_Per_Day, Repeat_Song_Rate FROM music_csv"
data2 = query(sql2, "music_csv")
text("## Repeat Song Ratio vs Minutes Streamed Per Day")
text("No correlation on minutes streamed per day, repeat song rate, or subscription type")
# Create a scatter plot of repeat song rate vs minutes streamed per day color coded by subscription type
fig2 = px.scatter(data2, x="Minutes_Streamed_Per_Day", y="Repeat_Song_Rate", color="Subscription_Type")
fig2.update_layout( title="Repeat Song Ratio vs Minutes Streamed Per Day", legend_title="Subscription Type") 
plotly(fig2)