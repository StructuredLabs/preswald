from preswald import connect, get_df, query, table, text, slider, plotly, selectbox
import plotly.express as px

connect()  # Initialize connection to preswald.toml data sources
df = get_df("my_dataset")  # Load data

fiction_df = df[df["Genre"] == "Fiction"]

text("# My Data Analysis on Fiction Books")
table(fiction_df, title="Fiction Data", limit=10)


text("## Find Books with User Rating and Year")
# Compute min and max values for "User Rating" from the dataframe
min_rating = fiction_df["User Rating"].min()
max_rating = fiction_df["User Rating"].max()

# Slider for "User Rating" with min and max values
Rating = slider(
    "User Rating",
    min_val=min_rating,
    max_val=max_rating,
    default=(min_rating + max_rating) / 2,
    step=0.1,
)

# Extract unique years from the DataFrame, sort them and convert them to strings
years = sorted(df["Year"].dropna().unique())
years = list(map(str, years))
year_options = ["All Years"] + years

# Selectbox for "Years"
Year = selectbox(
    label="Choose Year from",
    options=year_options,
)

# Build the SQL query based on the selected "Year" and "User Rating"
if Year == "All Years":
    sql = f'SELECT * FROM my_dataset WHERE "User Rating" >= {Rating} ORDER BY "User Rating" ASC'
else:
    sql = f'SELECT * FROM my_dataset WHERE "User Rating" >= {Rating} AND Year > {Year} ORDER BY "User Rating" ASC'

filtered_df = query(sql, "my_dataset")
table(filtered_df, title="Filtered Data Fiction")


fig = px.scatter(
    filtered_df,
    x="User Rating",
    y="Reviews",
    color="Year",
    hover_name="Name",
    hover_data=["Price"],
    title="User Rating vs. Reviews",
)
plotly(fig)
