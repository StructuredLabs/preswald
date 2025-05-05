from preswald import connect, get_df, query, text, text_input, table, slider, selectbox, plotly
import plotly.express as px
import pandas as pd

import numpy as np

# Connect to Preswald
connect()

# Load the dataset
df = get_df("indian_startup_funding")

#data processing and basic wrangliing (CLEAN!)
df = df.dropna(subset=["Date dd/mm/yyyy", "Amount in USD"])

def clean_amount_column(value):
    """Clean the amount column by removing commas and converting to float."""
    if pd.isna(value):
        return None
    try:
        # Remove commas and convert to float
        return float(str(value).replace(",", ""))
    except:
        return None  # if conversion fails (e.g., "Undisclosed"), return NONE or n/a
    
df["Year"] = pd.to_datetime(df["Date dd/mm/yyyy"], format="%d/%m/%Y", errors="coerce").dt.year
df["Month"] = pd.to_datetime(df["Date dd/mm/yyyy"], format="%d/%m/%Y", errors="coerce").dt.month
df["Amount in USD"] = df["Amount in USD"].apply(clean_amount_column)
df = df.dropna(subset=["Year", "Amount in USD"])



#extracting variables that we will use to filter
unique_verticals = sorted(df["Industry Vertical"].dropna().unique().tolist())
cities = sorted(df["City  Location"].dropna().unique().tolist())
investment_types = sorted(df["InvestmentnType"].dropna().unique().tolist())

text("# Indian Startup Funding Analysis 💰💰💰")

text("The Indian startup scene has exploded in recent years! This tool lets you dig into funding data, PitchBook-style, to see which startups got the big bucks and filter them by funding amount.")
text("Shows startups with funding above your selected range, including their city, investors, and cash haul—perfect for spotting the heavy hitters!")



'''
I tried to implement this with SQL however, my sql query was not giving me any data results, it seemed to be an 
issue with some keywords that were not being recognized by the SQL engine. So i implemented this with pandas instead.

here was my SQL query code..
filter_query = f"""
SELECT "Startup Name", "City  Location", "Investors Name", "Amount in USD"
FROM indian_startup_funding
WHERE "Amount in USD" <= {funding_range}
ORDER BY "Amount in USD" DESC
LIMIT 10
"""

filtered_df = query(filter_query)
if filtered_df.empty:
    text("No startups found within the selected funding range.")
else:
    filtered_df = filtered_df[["Startup Name", "City  Location", "Investors Name", "Amount in USD"]]
    filtered_df = filtered_df.sort_values("Amount in USD", ascending=False)
    table(filtered_df)
    
'''

text("## 🔍 Filter Startups by Funding Amount and their city")

min_funding = int(df["Amount in USD"].min())
max_funding = int(df["Amount in USD"].max())
# Compute realistic funding limits using percentiles
min_funding = int(df["Amount in USD"].min())
p96_funding = int(np.percentile(df["Amount in USD"].dropna(), 96))  # 96th percentile (removes outliers in the slider range) (our max)
p95_funding = int(np.percentile(df["Amount in USD"].dropna(), 95))  # 95th percentile (our limit after which we can jusy show all results) 
p50_funding = int(np.percentile(df["Amount in USD"].dropna(), 50))  # Median funding (approx 11016000 dollars)

#Since most of the startups are on the lower funcding size, only a few have billions of dollars in funding, casues slider to be 
#too skewed to the right. Need to compensate for this by setting the max funding to the 95th percentile.
#step size is 100k

funding_range = slider("Select Funding Range (USD)", min_val=min_funding, max_val=p96_funding, default=p50_funding, step = 1000000)
selected_city = selectbox(options = cities, label="Select City", default="Bangalore")

#and if we are at 95th then, just set the query range to max.
if funding_range >= p95_funding:
    funding_range = max_funding  # Only if fully at 95th, allow max value

text(f"Selected Funding Range: {funding_range}")

#firsy use sql query to get all records that match city
#btwthis is so cool, how do they make a csv into sql database? sqllite perhaps? could see the code and check on git.

city_query = f"""
SELECT "Startup Name", "City  Location", "Investors Name", "Amount in USD" FROM indian_startup_funding
WHERE "City  Location" = '{selected_city}'
"""

filtered_df = query(city_query, "indian_startup_funding")   
#seems like this sql query is on a fresh version of the dataset. not sure why, but it is not the same as the one loaded above.
filtered_df["Amount in USD"] = filtered_df["Amount in USD"].apply(clean_amount_column)
filtered_df = filtered_df.dropna(subset=["Amount in USD"])
#so need to clean again.


filtered_df = filtered_df[filtered_df["Amount in USD"] <= funding_range][["Startup Name", "City  Location", "Investors Name", "Amount in USD"]]
filtered_df = filtered_df.sort_values("Amount in USD", ascending=False)
table(filtered_df)


text("## 📈 Top Funded Startups")

text("1) Total Investments Over Time")
text("This line chart tracks total startup funding over the years in millions—see how the cash flow’s been trending!")

investments_per_year = df.groupby("Year")["Amount in USD"].sum().reset_index()
investments_per_year["Amount in USD (Millions)"] = investments_per_year["Amount in USD"] / 1000000

fig1 = px.line(
    investments_per_year, 
    x="Year", 
    y="Amount in USD (Millions)", 
    markers=True
)
fig1.update_layout(
    xaxis_title="Year",
    yaxis_title="Total Funding (USD Millions)",
    template="plotly_white"
)
plotly(fig1)




top_cities = df.groupby("City  Location")["Amount in USD"].sum().reset_index().nlargest(10, "Amount in USD")
top_cities["Amount in USD (Millions)"] = top_cities["Amount in USD"] / 1000000
top_cities = top_cities.sort_values("Amount in USD", ascending=True)

text("2) Top Cities for Startup Funding")
text("Check out the top 10 cities raking in startup cash—horizontal bars show who’s leading the funding race!")


fig2 = px.bar(
    top_cities, 
    x="Amount in USD (Millions)", 
    y="City  Location", 
    orientation='h'
)
fig2.update_layout(
    xaxis_title="Total Funding (USD Millions)",
    yaxis_title="City",
    template="plotly_white"
)
plotly(fig2)




top_investors = df.groupby("Investors Name")["Amount in USD"].sum().reset_index().nlargest(10, "Amount in USD")
top_investors["Amount in USD (Millions)"] = top_investors["Amount in USD"] / 1000000
top_investors = top_investors.sort_values("Amount in USD", ascending=True)


text("3) Top Investors by Funding Amount")
text("Here's who's doling out the most cash—top 10 investors ranked by total funding in millions!")

fig3 = px.bar(
    top_investors, 
    x="Amount in USD (Millions)", 
    y="Investors Name", 
    orientation='h'
)
fig3.update_layout(
    xaxis_title="Total Funding (USD Millions)",
    yaxis_title="Investor",
    template="plotly_white"
)
plotly(fig3)



industry_funding = df.groupby("Industry Vertical")["Amount in USD"].sum().reset_index().nlargest(10, "Amount in USD")
industry_funding["Amount in USD (Millions)"] = industry_funding["Amount in USD"] / 1000000

text("4) Funding by Industry")
text("This pie chart breaks down funding by industry—see which sectors are eating the biggest slices of the pie!")


fig4 = px.pie(
    industry_funding, 
    values="Amount in USD (Millions)", 
    names="Industry Vertical", 
    title="🏭 Funding Distribution by Industry",
    hole=0.4
)
fig4.update_layout(template="plotly_white")
plotly(fig4)