from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

connect()  # Initialize Preswald

df = get_df('ev_csv')

text("## Top Electric Vehicle Manufacturers in the Washington, USA")

sql = f"""
SELECT Make, COUNT(*) AS Owned_by
FROM ev_csv
GROUP BY Make
HAVING Owned_by > 0
ORDER BY Owned_by DESC
"""

all_makes_df = query(sql, "ev_csv")

fig = px.bar(all_makes_df, x="Make", y="Owned_by", text_auto='.2s',
             title="All Electric Vehicle Manufacturers (Grouped)",
             color="Owned_by")

fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
plotly(fig)

# Selection
limit_slider = slider("Select Top N Manufacturers in Washington, USA", min_val=1, max_val=20, default=10)

sql += f"LIMIT {limit_slider}"
selected_makes_df = query(sql, "ev_csv")

table(selected_makes_df, f"Top {limit_slider} Electric Car Manufacturers in Washington, USA")

# pie chart
fig_pie = px.pie(selected_makes_df, 
                 names="Make", 
                 values="Owned_by",
                 title=f"Market Share of Top {limit_slider} EV Manufacturers",
                 hole=0.3)
plotly(fig_pie)

# Adoption

text("#### EV Adoption Over the years in Washington, USA")

sql_yearly = """
SELECT "Model Year", COUNT(*) AS Total_EVs
FROM ev_csv
GROUP BY "Model Year"
ORDER BY "Model Year"
"""

yearly_trends_df = query(sql_yearly, "ev_csv")

fig_trend = px.line(yearly_trends_df, x="Model Year", y="Total_EVs",
                    title="EV Adoption Over Time",
                    markers=True)
plotly(fig_trend)


