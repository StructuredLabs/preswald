from preswald import connect, get_df, text, plotly, table, query, selectbox, slider
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# --------------------------------------
# Connect to dataset and introduction
# --------------------------------------
text("# 🌎 Global Happiness Tracking")
text("This dashboard tracks the global happiness index from 2015 to 2019.")
text("The data is sourced from the World Happiness Report.")

connect()
df = get_df("all_years")

# --------------------------------------
# World Map of Happiness Scores by Country (with slider)
# --------------------------------------
text("## 🗺️ World Happiness Map")

# Add year slider (2015 to 2019)
selected_year = slider("Select Year for World Map",
                       min_val=2015, max_val=2019, default=2015, step=1)

# Filter dataset by selected year
year_df = df[df["Year"] == selected_year]

# Plot world choropleth map for that year
map_fig = px.choropleth(
    year_df,
    locations="Country",
    locationmode="country names",
    color="Score",
    color_continuous_scale="Viridis",
    title=f"🗺️ Average Happiness Score by Country in {selected_year}",
    labels={"Score": "Happiness Score"},
)

map_fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True,
             projection_type="natural earth"),
    margin=dict(l=60, r=40, t=60, b=60)
)

plotly(map_fig)


# --------------------------------------
# Line Chart: Global Average Happiness Over Time
# --------------------------------------
text("## 📈 Global Average Happiness Over Time")

avg_scores = query("""
    SELECT Year, AVG(Score) AS avg_score
    FROM all_years
    GROUP BY Year
    ORDER BY Year
""", "all_years")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=avg_scores["Year"].astype(str),
    y=avg_scores["avg_score"],
    mode="lines+markers",
    name="",
    line=dict(width=3)
))

fig.add_trace(go.Scatter(
    x=[str(avg_scores["Year"].min()), str(avg_scores["Year"].max())],
    y=[5.3, 5.5],
    mode="markers",
    marker=dict(color='rgba(0,0,0,0)'),
    showlegend=False,
    hoverinfo='skip'
))

fig.update_layout(
    title="📈 Global Average Happiness Score by Year",
    xaxis_title="Year",
    yaxis_title="Happiness Score",
    margin=dict(l=60, r=40, t=60, b=60)
)

plotly(fig)

# --------------------------------------
# Bar Chart: Average Happiness by Region
# --------------------------------------
text("## 🏆 Average Happiness by Region")

region_avg = query("""
    SELECT Region, AVG(Score) AS avg_score
    FROM all_years
    GROUP BY Region
    ORDER BY avg_score DESC
""", "all_years")

colors = px.colors.qualitative.Plotly
region_colors = {region: colors[i % len(colors)]
                 for i, region in enumerate(region_avg["Region"])}

bar_fig = go.Figure()

for idx, row in region_avg.iterrows():
    bar_fig.add_trace(go.Bar(
        x=[row["Region"]],
        y=[row["avg_score"]],
        marker_color=region_colors[row["Region"]],
        name="",
        showlegend=False
    ))

bar_fig.update_layout(
    title="🏆 Average Happiness Score by Region",
    xaxis_title="Region",
    yaxis_title="Happiness Score",
    xaxis_tickangle=-45,
    margin=dict(l=60, r=40, t=60, b=100)
)

plotly(bar_fig)

# --------------------------------------
# Country Comparison: Selectbox (Top 5 Countries Only)
# --------------------------------------
text("## 🌐 Country vs Country: Happiness Score Comparison")

# Shortlist of countries
country_options = ["India", "United States",
                   "China", "United Kingdom", "Denmark"]

# Selectboxes for comparison
country1 = selectbox("Select Country 1",
                     options=country_options, default="United States")
country2 = selectbox("Select Country 2",
                     options=country_options, default="India")

# SQL Query for selected countries
comparison_df = query(f"""
    SELECT Country, Year, AVG(Score) AS avg_score
    FROM all_years
    WHERE Country IN ('{country1}', '{country2}')
    GROUP BY Country, Year
    ORDER BY Year
""", "all_years")

# Plot the comparison chart
compare_fig = go.Figure()

for country in [country1, country2]:
    country_data = comparison_df[comparison_df["Country"] == country]
    compare_fig.add_trace(go.Scatter(
        x=country_data["Year"].astype(str),
        y=country_data["avg_score"],
        mode="lines+markers",
        name=country,
        line=dict(width=3)
    ))

compare_fig.update_layout(
    title=f"📊 Happiness Score Over Time: {country1} vs {country2}",
    xaxis_title="Year",
    yaxis_title="Average Happiness Score",
    margin=dict(l=60, r=40, t=60, b=60)
)

plotly(compare_fig)

# --------------------------------------
# Most Improved & Declined Countries in Happiness Score (2015 to 2019)
# --------------------------------------
text("## 🔺 Most Improved & Declined Countries (2015 → 2019)")

# Get scores from 2015 and 2019
score_2015 = df[df["Year"] == 2015][["Country", "Score"]].rename(
    columns={"Score": "Score_2015"})
score_2019 = df[df["Year"] == 2019][["Country", "Score"]].rename(
    columns={"Score": "Score_2019"})

# Compute change
score_change = pd.merge(score_2015, score_2019, on="Country")
score_change["Change"] = score_change["Score_2019"] - \
    score_change["Score_2015"]

# -------------------------------
# 🔼 Top 5 Most Improved Countries
# -------------------------------
top_improved = score_change.sort_values(
    "Change", ascending=False).head(5).reset_index(drop=True)

# Reverse green shades so darkest = most improved
green_shades = px.colors.sequential.Greens[-5:][::-1]

fig_improved = go.Figure()

for i, row in top_improved.iterrows():
    fig_improved.add_trace(go.Bar(
        x=[row["Country"]],
        y=[row["Change"]],
        marker_color=green_shades[i],
        text=f"{row['Change']:.2f}",
        textposition='outside',
        showlegend=False
    ))

fig_improved.update_layout(
    title="🔺 Top 5 Most Improved Countries (2015 to 2019)",
    xaxis_title="Country",
    yaxis_title="Score Change",
    margin=dict(l=60, r=40, t=60, b=60)
)

plotly(fig_improved)

# -------------------------------
# 🔻 Top 5 Most Declined Countries
# -------------------------------
top_declined = score_change.sort_values(
    "Change", ascending=True).head(5).reset_index(drop=True)

# Reverse red shades so darkest = most declined
red_shades = px.colors.sequential.Reds[-5:][::-1]

fig_declined = go.Figure()

for i, row in top_declined.iterrows():
    fig_declined.add_trace(go.Bar(
        x=[row["Country"]],
        y=[row["Change"]],
        marker_color=red_shades[i],
        text=f"{row['Change']:.2f}",
        textposition='outside',
        showlegend=False
    ))

fig_declined.update_layout(
    title="🔻 Top 5 Most Declined Countries (2015 to 2019)",
    xaxis_title="Country",
    yaxis_title="Score Change",
    margin=dict(l=60, r=40, t=60, b=60)
)

plotly(fig_declined)

# --------------------------------------
# 💸 GDP vs Happiness Score (Manual Year Slider - Independent)
# --------------------------------------
text("## 📊 Correlation Between GDP and Happiness Score")
text("## 💸 GDP vs Happiness Score (Selected Year)")

# Separate slider just for this section
bubble_year = slider("Select Year for Bubble Plot",
                     min_val=2015, max_val=2019, default=2015, step=1)

# Filter for selected year
bubble_year_df = df[df["Year"] == bubble_year]

fig = px.scatter(
    bubble_year_df,
    x="GDP_Capita",
    y="Score",
    size="Life_Expectancy",
    color="Region",
    hover_name="Country",
    title=f"💸 GDP per Capita vs Happiness Score ({bubble_year})",
    labels={"GDP_Capita": "GDP per Capita", "Score": "Happiness Score"},
    hover_data={
        "Life_Expectancy": True,  # 👈 force actual value
        "GDP_Capita": ":.2f",
        "Score": ":.2f"
    }
)

fig.update_layout(
    xaxis_title="GDP per Capita",
    yaxis_title="Happiness Score",
    margin=dict(l=60, r=40, t=60, b=60),
    xaxis=dict(showgrid=True, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=False)
)

plotly(fig)
