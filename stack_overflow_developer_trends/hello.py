from preswald import connect, get_df, selectbox, table, text, plotly, separator, checkbox
import plotly.express as px
import pandas as pd
import string

try:
    connect()
    df = get_df("stack_overflow_survey")

except Exception as e:
    text("Error: Unable to load dataset. Please ensure the data file is in the 'data/' directory.")
    text("Follow the instructions in the README to download the dataset and run the app.")
    raise e

text("# Stack Overflow Developer Survey 2024 Explorer")

text("### Check one or more boxes below to filter the countries shown in the dropdown")

# Create alphabet checkboxes labeled by country range (excluding 'NA')
# The number of countries is too long to load completely into the
# select box since the selectbox has no search or scroll features
selected_letters = []
for letter in string.ascii_uppercase:
    matching_countries = sorted([c for c in df["Country"].dropna().unique() if c.upper().startswith(letter)])
    # Skip groups with no valid country names or containing 'NA'
    matching_countries = [c for c in matching_countries if c != 'NA']
    if matching_countries:
        checkbox_label = f"{matching_countries[0]} - {matching_countries[-1]}"
        if checkbox(checkbox_label, size=0.15):
            selected_letters.append(letter)

separator()

# Filter countries based on selected country ranges
if selected_letters:
    filtered_countries = sorted(
        [c for c in df["Country"].dropna().unique() if c != 'NA' and c[0].upper() in selected_letters]
    )

    # Load country selectbox based on chosen country filter
    country = selectbox("Select Country", filtered_countries, default=filtered_countries[0])

    separator()

    # Data filtering and cleaning
    filtered_df = df[df["Country"] == country].copy()
    filtered_df = filtered_df.dropna(subset=["YearsCodePro", "ConvertedCompYearly"])

    filtered_df["YearsCodePro"] = filtered_df["YearsCodePro"].replace({
        "Less than 1 year": 0.5,
        "More than 50 years": 51
    })
    filtered_df["YearsCodePro"] = pd.to_numeric(filtered_df["YearsCodePro"], errors="coerce")
    filtered_df["ConvertedCompYearly"] = pd.to_numeric(filtered_df["ConvertedCompYearly"], errors="coerce")
    filtered_df = filtered_df.dropna(subset=["YearsCodePro", "ConvertedCompYearly"])
    filtered_df = filtered_df[filtered_df["ConvertedCompYearly"] > 0]

    # Scatter plot with trendline
    fig = px.scatter(
        filtered_df,
        x="YearsCodePro",
        y="ConvertedCompYearly",
        labels={
            "YearsCodePro": "Years of Professional Experience",
            "ConvertedCompYearly": "Annual Compensation (USD)"
        },
        title=f"Developer Compensation vs. Experience ({country})",
        log_y=True,
        opacity=0.6,
        trendline="ols",
        template="plotly_white"
    )

    plotly(fig)
    separator()

    # Display limited table (first 20 rows)
    table(filtered_df.head(20), title=f"Developer Responses from {country}")
else:
    text("Please select at least one letter group to filter countries.")
