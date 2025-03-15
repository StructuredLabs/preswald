import plotly.express as px

from preswald import connect, get_df, plotly, query, slider, table, text


# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("pixar_films")

sql = "SELECT film, release_date, box_office_worldwide, rotten_tomatoes_score FROM pixar_films WHERE CAST(release_date AS Date) >= '2005-01-01'"
filtered_df = query(sql, "pixar_films")

text(
    "## Pixar rilms released on or after 2005 with their box office revenue and associated rotten tomatoes score"
)
threshold = slider("Threshold", min_val=70, max_val=100, default=50)
table(
    filtered_df[filtered_df["rotten_tomatoes_score"] > threshold],
    title="Dynamic Data View",
)

text(
    "## A plot of box office revenue and rotten tomato scores for Pixar rilms released on or after 2005"
)
fig = px.scatter(df, x="rotten_tomatoes_score", y="box_office_worldwide")
plotly(fig)
