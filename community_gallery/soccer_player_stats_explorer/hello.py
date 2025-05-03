# Final Submission Code by Shahir

from preswald import connect, slider, text, text_input, selectbox, checkbox, plotly, alert, separator, button
import pandas as pd
import plotly.express as px

connect()

# Header and description of the app
text("# ⚽ 2022-2023 Soccer Player Stats Explorer")
text("Explore and visualize soccer player data with interactive filters and detailed charts.")

# Load data
df = pd.read_csv("data/football_player_stats.csv", sep=";", encoding="latin1")

# Filter by player names
player_search = text_input(label="Filter by Player names", placeholder="Enter player's name")

# Checkbox to show additional filters
show_filters = checkbox(label="Show Additional Filters", default=False)
if show_filters:
    player_group = selectbox(
        label="Player Group", 
        options=["All", "Goalkeeper", "Defender", "Midfielder", "Attacker", "CB", "RB", "RWB"],
        default="All",
        size=0.33
    )
    min_age_input = text_input(
        label="Minimum Age", 
        placeholder=str(df["Age"].min()),
        size=0.33
    )
    max_age_input = text_input(
        label="Maximum Age", 
        placeholder=str(df["Age"].max()),
        size=0.33
    )
    # Convert the age inputs to floats else use defaults if input is empty or invalid
    try:
        min_age = float(min_age_input) if min_age_input.strip() != "" else float(df["Age"].min())
    except:
        min_age = float(df["Age"].min())
    try:
        max_age = float(max_age_input) if max_age_input.strip() != "" else float(df["Age"].max())
    except:
        max_age = float(df["Age"].max())
    
    # Additional filters for nationality, club, and league.
    nationalities = sorted(list(df["Nation"].dropna().astype(str).unique()))
    nationality_filter = selectbox(
        label="Nationality", 
        options=["All"] + nationalities, 
        default="All",
        size=0.33
    )
    clubs = sorted(list(df["Squad"].dropna().astype(str).unique()))
    club_filter = selectbox(
        label="Club", 
        options=["All"] + clubs, 
        default="All",
        size=0.33
    )
    leagues = sorted(list(df["Comp"].dropna().astype(str).unique()))
    league_filter = selectbox(
        label="League", 
        options=["All"] + leagues, 
        default="All",
        size=0.33
    )
else:
    # If additional filters are hidden, use default values.
    player_group = "All"
    min_age = float(df["Age"].min())
    max_age = float(df["Age"].max())
    nationality_filter = "All"
    club_filter = "All"
    league_filter = "All"

separator()

# Make a copy of the dataframe and filter based on user inputs
filtered_df = df.copy()
if player_search:
    filtered_df = filtered_df[filtered_df["Player"].str.contains(player_search, case=False, na=False)]
filtered_df = filtered_df[(filtered_df["Age"] >= min_age) & (filtered_df["Age"] <= max_age)]
if nationality_filter != "All":
    filtered_df = filtered_df[filtered_df["Nation"] == nationality_filter]
if club_filter != "All":
    filtered_df = filtered_df[filtered_df["Squad"] == club_filter]
if league_filter != "All":
    filtered_df = filtered_df[filtered_df["Comp"] == league_filter]

# Filter by player group if it's not "All"
if player_group != "All":
    if player_group == "Goalkeeper":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("GK", case=False, na=False)]
    elif player_group == "Defender":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("DF", case=False, na=False)]
    elif player_group == "Midfielder":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("MF", case=False, na=False)]
    elif player_group == "Attacker":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("FW|ST", case=False, na=False)]

# record which graph the user wants to see
viz_choice = selectbox(
    label="Select Visualization Type", 
    options=["Scatter Plot", "Correlation Heatmap", "Bar Chart", "Histogram"],
    default="Scatter Plot"
)

# Render the user's choice of graph
if viz_choice == "Scatter Plot":
    text("### Scatter Plot")

    # custom x and y axis
    scatter_x = selectbox(label="X-axis", options=df.columns.tolist(), default="Age", size=0.5)
    scatter_y = selectbox(label="Y-axis", options=df.columns.tolist(), default="Goals", size=0.5)

    text(f"Scatter Plot: {scatter_x} vs. {scatter_y}")
    fig_scatter = px.scatter(
        filtered_df,
        x=scatter_x,
        y=scatter_y,
        hover_data=["Player", "Squad", "Nation", "Pos"],
        title=f"Scatter Plot: {scatter_x} vs. {scatter_y}",
        labels={scatter_x: scatter_x, scatter_y: scatter_y}
    )
    plotly(fig_scatter)

elif viz_choice == "Correlation Heatmap":
    text("### Correlation Heatmap")
    text("This heatmap shows correlations between selected key metrics.")
    useful_cols = ["Age", "Goals", "Assists", "MP"]
    corr_matrix = filtered_df[useful_cols].corr()
    fig_heatmap = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap (Limited Data)")
    plotly(fig_heatmap)

elif viz_choice == "Bar Chart":
    text("### Bar Chart")
    text("This bar chart displays the average of a selected stat grouped by club, league, or nationality.")

    # group by club, league, or nationality. Then select a stat to average.
    group_by_option = selectbox(label="Group by (for Bar Chart)", options=["Club", "League", "Nationality"], default="Club", size=0.33)
    stat_for_avg = selectbox(label="Stat for Average", options=list(df.select_dtypes(include='number').columns), default="Goals", size=0.33)

    if group_by_option == "Club":
        group_col = "Squad"
    elif group_by_option == "League":
        group_col = "Comp"
    else:
        group_col = "Nation"
    df_grouped = filtered_df.groupby(group_col)[stat_for_avg].mean().reset_index()
    fig_bar = px.bar(
        df_grouped, 
        x=group_col, 
        y=stat_for_avg, 
        title=f"Average {stat_for_avg} by {group_by_option}",
        labels={group_col: group_by_option, stat_for_avg: stat_for_avg}
    )
    plotly(fig_bar)

elif viz_choice == "Histogram":
    text("### Histogram")
    text("This histogram shows the distribution of a selected numeric stat.")

    # select a stat and number of bins
    hist_stat = selectbox(label="Histogram Stat", options=list(df.select_dtypes(include='number').columns), default="Age", size=0.33)
    bins = slider(label="Number of Bins", min_val=5, max_val=50, step=1.0, default=20, size=0.33)
    fig_hist = px.histogram(
        filtered_df, 
        x=hist_stat, 
        nbins=int(bins), 
        title=f"Distribution of {hist_stat}",
        labels={hist_stat: hist_stat}
    )
    plotly(fig_hist)
