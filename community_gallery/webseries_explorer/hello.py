import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table, selectbox, slider

text("## 📺 **Web Series Explorer** 🎬✨  \n"
     "### *Explore top web series with Series Explorer! Filter by genre, year, and rating, track trends, and uncover fun insights with interactive charts and data-driven visuals.* 🚀")

connect()
df = get_df('webseries_csv').dropna()

df["Released_year"] = pd.to_numeric(df["Released_year"], errors="coerce").fillna(0).astype(int)
df["Ratings"] = df["Ratings"].astype(float)

df["first_letter"] = df["Title"].str[0].str.upper()
unique_letters = sorted(df["first_letter"].dropna().unique())
unique_letters.insert(0, "All")

unique_genres = set()
df["Genre"].str.split(";").apply(unique_genres.update)
unique_genres = sorted(unique_genres)
unique_genres.insert(0, "All")

filter_mode = selectbox("Filter By", options=["Genre", "Series Name"], default="Genre")

if filter_mode == "Genre":
    text("You can type to search for a genre.")
    selected_genre = selectbox("Choose a Genre", options=unique_genres, default="All")  
    selected_letter = None
else:
    text("You can type to search for a letter.")
    selected_letter = selectbox("Choose a Starting Letter", options=unique_letters, default="All")  
    selected_genre = None

selected_rating = slider("Select Maximum Rating", min_val=1, max_val=10, default=10) 
min_year, max_year = int(df["Released_year"].min()), int(df["Released_year"].max())
selected_year = slider("Select Maximum Year", min_val=min_year, max_val=max_year, default=max_year)

def filter_series(filter_mode, selected_genre, selected_letter, selected_rating, selected_year):
    filtered = df[(df['Ratings'] <= selected_rating) & (df['Released_year'] <= selected_year)]
    
    if filter_mode == "Genre" and selected_genre != "All":
        filtered = filtered[filtered['Genre'].str.contains(selected_genre, na=False, case=False)]
    elif filter_mode == "Series Name" and selected_letter != "All":
        filtered = filtered[filtered['first_letter'] == selected_letter]
    
    return filtered if not filtered.empty else pd.DataFrame(columns=['Title', 'Genre', 'Released_year', 'Ratings', 'Votes', 'Duration (in Min)'])

filtered_df = filter_series(filter_mode, selected_genre, selected_letter, selected_rating, selected_year)[['Title', 'Genre', 'Released_year', 'Ratings', 'Votes', 'Duration (in Min)']]

display_df = filtered_df.rename(columns={
    "Title": "Series Name",
    "Genre": "Genres",
    "Released_year": "Release Year",
    "Ratings": "Rating",
    "Votes": "Number of Votes",
    "Duration (in Min)": "Duration (Minutes)"
})

text(f"Number of series: {len(display_df)}")
table(display_df)

series_per_year = df.groupby("Released_year").size().reset_index(name="count")
average_rating_per_year = df.groupby("Released_year")["Ratings"].mean().reset_index()

text("Number of Web Series Released Per Year")
fig1 = px.line(series_per_year, x="Released_year", y="count", markers=True)
plotly(fig1)

text("Average Web Series Rating Per Year")
fig2 = px.line(average_rating_per_year, x="Released_year", y="Ratings", markers=True)
plotly(fig2)

text("Duration vs Average Rating")
unique_duration_df = df.groupby("Duration (in Min)", as_index=False)["Ratings"].mean()
fig3 = px.scatter(unique_duration_df, x="Duration (in Min)", y="Ratings")
plotly(fig3)

text("📺 **Fun Web Series Facts!** 📺")
selected_fact = selectbox(
    "Pick a web series fact to reveal!", 
    options=[
        "⭐ Highest-Rated Series", 
        "💀 Lowest-Rated Series", 
        "🎥 Longest Series", 
        "⏳ Shortest Series", 
        "👥 Most Voted Series", 
        "🕵️‍♂️ Least Voted Series", 
        "📜 Earliest Released Series", 
        "🚀 Latest Released Series"
    ]
)

if selected_fact == "⭐ Highest-Rated Series":
    text(f"📺 **{df.loc[df['Ratings'].idxmax(), 'Title']}** - 📊 Rating: **{df['Ratings'].max()}**")

elif selected_fact == "💀 Lowest-Rated Series":
    text(f"📺 **{df.loc[df['Ratings'].idxmin(), 'Title']}** - 📊 Rating: **{df['Ratings'].min()}**")

elif selected_fact == "🎥 Longest Series":
    text(f"📺 **{df.loc[df['Duration (in Min)'].idxmax(), 'Title']}** - ⏳ Runtime: **{df['Duration (in Min)'].max()} minutes**")

elif selected_fact == "⏳ Shortest Series":
    text(f"📺 **{df.loc[df['Duration (in Min)'].idxmin(), 'Title']}** - ⏳ Runtime: **{df['Duration (in Min)'].min()} minutes**")

elif selected_fact == "👥 Most Voted Series":
    text(f"📺 **{df.loc[df['Votes'].idxmax(), 'Title']}** - 👥 Votes: **{df['Votes'].max()}**")

elif selected_fact == "🕵️‍♂️ Least Voted Series":
    text(f"📺 **{df.loc[df['Votes'].idxmin(), 'Title']}** - 👥 Votes: **{df['Votes'].min()}**")

elif selected_fact == "📜 Earliest Released Series":
    text(f"📺 **{df.loc[df['Released_year'].idxmin(), 'Title']}** - 📅 Year: **{df['Released_year'].min()}**")

elif selected_fact == "🚀 Latest Released Series":
    text(f"📺 **{df.loc[df['Released_year'].idxmax(), 'Title']}** - 📅 Year: **{df['Released_year'].max()}**")
