import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text

# Title
text("# Travel Details Analytics Dashboard 🌍")

# Load and connect data
connect()

# ---


def clean_cost(cost):
    """
    Cleans an individual cost string.

    Args:
        cost (str): The cost string to clean.

    Returns:
        float: The cleaned cost as a float, or None if the cost cannot be cleaned.
    """
    if isinstance(cost, str):
        cost = cost.replace("$", "").replace(" ", "")  # Remove '$' and spaces
        if "USD" in cost:
            cost = cost.replace("USD", "")  # Remove 'USD'
        try:
            return float(cost)
        except ValueError:
            return None
    elif isinstance(cost, (int, float)):
        return float(cost)
    else:
        return None


# Columns to interact with
ACCOMMODATION_COST_COLUMN = "Accommodation cost"
TRAVELER_NATIONALITY_COLUMN = "Traveler nationality"
CLEANED_COST_COLUMN = "Cleaned Cost"

# Read the data and filter based on magnitude
data = get_df("travel_details_data")
print(data)

# Convert Accommodation cost column to numeric, handling any non-numeric values
data[ACCOMMODATION_COST_COLUMN] = pd.to_numeric(
    data[ACCOMMODATION_COST_COLUMN], errors="coerce"
)
data[CLEANED_COST_COLUMN] = data[ACCOMMODATION_COST_COLUMN].apply(clean_cost)
data = data.dropna(subset=[CLEANED_COST_COLUMN])  # Drop rows with missing costs

lowest_price = data[CLEANED_COST_COLUMN].min()
highest_price = data[CLEANED_COST_COLUMN].max()

# Slider for filtering accommodation cost
min_accommodation_cost = slider(
    "Minimum Accommodation Cost",
    min_val=lowest_price,
    max_val=highest_price,
    default=375.00,
)

filtered_data = data[data[ACCOMMODATION_COST_COLUMN] >= min_accommodation_cost]

# Summary statistics
text(
    f"### Total Trips with Accommodation Cost ≥ {min_accommodation_cost}: {len(filtered_data)}"
)

# View the filtered data
table(filtered_data)

# ACCOMMODATION_COST distribution
fig_hist = px.histogram(
    filtered_data,
    x=CLEANED_COST_COLUMN,
    nbins=20,
    title="Distribution of Accommodation Cost",
)
fig_hist.update_layout(  # ✅ Added axis titles for Issue #656
    xaxis_title="Accommodation Cost (USD)",
    yaxis_title="Number of Trips"
)
plotly(fig_hist)

# Nationality vs. Accommodation cost scatter plot
fig_scatter = px.scatter(
    filtered_data,
    x=TRAVELER_NATIONALITY_COLUMN,
    y=CLEANED_COST_COLUMN,
    title="Nationality vs Accommodation Cost",
    labels={
        "Nationality": "Nationality",
        "Accommodation Cost": "Accommodation Cost (USD)",
    },
)
plotly(fig_scatter)
