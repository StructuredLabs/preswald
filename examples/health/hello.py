import duckdb
import plotly.express as px

from preswald import plotly, text, view


# ----------------------------------------------------------------------------
# 1. Connect to your MotherDuck database
# ----------------------------------------------------------------------------
#    Make sure the environment variable MOTHERDUCK_TOKEN is set
#    or update the connection string to include your token.
con = duckdb.connect("md:my_db")

# 2. Query the DQS_Cholesterol_in_adults_age_20 table
df = con.execute("SELECT * FROM DQS_Cholesterol_in_adults_age_20").df()

# ----------------------------------------------------------------------------
# 2. Simple text description for Preswald
# ----------------------------------------------------------------------------
text("# Cholesterol Data Exploration")
text("Here are some sample charts based on our dummy health dataset schema.")

# ----------------------------------------------------------------------------
# 3. Several Plotly charts
# ----------------------------------------------------------------------------

# -- Chart A: Line chart of ESTIMATE over TIME_PERIOD
text("## Chart A: Trend of Cholesterol Estimates Over Time")
# We'll filter out rows where ESTIMATE is missing
df_line = df.dropna(subset=["ESTIMATE"]).copy()

fig_a = px.line(
    df_line,
    x="TIME_PERIOD",
    y="ESTIMATE",
    color="ESTIMATE_TYPE",  # separate lines for "age adjusted" vs "crude"
    markers=True,
    title="Cholesterol Estimate by Time Period",
)
plotly(fig_a)

# -- Chart B: Bar chart comparing ESTIMATE for different ESTIMATE_TYPE
text("## Chart B: Comparison of Age Adjusted vs. Crude Estimates")
fig_b = px.bar(
    df_line,
    x="TIME_PERIOD",
    y="ESTIMATE",
    color="ESTIMATE_TYPE",
    barmode="group",
    title="Age Adjusted vs. Crude Estimates",
)
plotly(fig_b)

# -- Chart C: Scatter plot of ESTIMATE vs. SUBGROUP, colored by GROUP
text("## Chart C: Scatter Plot of Estimate vs. Subgroup")
# We'll again filter out missing estimates
fig_c = px.scatter(
    df_line,
    x="SUBGROUP_ID",
    y="ESTIMATE",
    color="GROUP",  # e.g. "Total" vs. "Race and Hispanic origin"
    size="ESTIMATE",
    hover_data=["TIME_PERIOD", "ESTIMATE_TYPE"],
    title="Cholesterol Estimate by Subgroup",
)
plotly(fig_c)

# ----------------------------------------------------------------------------
# 4. Render the final display in Preswald
# ----------------------------------------------------------------------------
view(df)
