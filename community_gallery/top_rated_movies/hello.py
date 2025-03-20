from preswald import text, connect, get_df, table, slider, query, plotly
import plotly.express as px

# Title
text("# 🎬 Top Rated Movies Dashboard")

# Connect to the CSV file
connect()
df = get_df("top_rated_movies")

# Show available columns
text("## 🔍 Data Preview")
table(df.head())

# Filter Data by using a slider
threshold = slider("Threshold", min_val=0, max_val=1624, default=50)
table(df[df["popularity"] > threshold], title="View Popularity according To Threshold")

# SQL Modification and Query
text("### An SQL Query Used to Manipulate\n```sql\nUPDATE top_rated_movies SET overview = 'HELLO WORLD' WHERE original_title = 'Barb Wire'\n```")  
manipulate = query("UPDATE top_rated_movies SET overview = 'HELLO WORLD' WHERE original_title = 'Barb Wire'","top_rated_movies")

text("## Lets View The Changes")
changed = query("SELECT * FROM top_rated_movies WHERE original_title='Barb Wire'","top_rated_movies")
table(changed, title="View Changes")

# Data Visualization
text("## 📊 Data Visualization")
fig = px.scatter(df, x="original_title", y="popularity", color="popularity", title="Popularity of Movies")
plotly(fig)