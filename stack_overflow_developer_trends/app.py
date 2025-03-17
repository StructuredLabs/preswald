from preswald import connect, get_df, selectbox, table, text, plotly, separator, checkbox, slider
import statsmodels.api as sm
import plotly.express as px
import pandas as pd
import string

def normalize_years_of_experience(filtered_df):
    filtered_df["YearsCodePro"] = filtered_df["YearsCodePro"].replace({
            "Less than 1 year": 0,
            "More than 50 years": 51
    })
    filtered_df["YearsCodePro"] = pd.to_numeric(filtered_df["YearsCodePro"], errors="coerce")

    # Apply filtering
    filtered_df = filtered_df.dropna(subset=["YearsCodePro", "ConvertedCompYearly"])
    filtered_df["ConvertedCompYearly"] = pd.to_numeric(filtered_df["ConvertedCompYearly"], errors="coerce")
    filtered_df = filtered_df[filtered_df["ConvertedCompYearly"] > 0]

    return filtered_df

def apply_experience_level_filter(filtered_df):

    numeric_experience_levels = sorted(set(filtered_df["YearsCodePro"].dropna().unique()))
    min_experience = int(min(numeric_experience_levels))
    max_experience = int(max(numeric_experience_levels))

    # Use slider for experience level selection
    selected_experience_min = slider(
        "Select Minimum Experience Level",
        min_val=min_experience,
        max_val=max_experience,
        step=1,
        default=min_experience,
        size=0.5
    )

    selected_experience_max = slider(
        "Select Maximum Experience Level",
        min_val=min_experience,
        max_val=max_experience,
        step=1,
        default=max_experience,
        size=0.5
    )

    # Apply experience level filter
    return filtered_df[(filtered_df["YearsCodePro"] >= selected_experience_min) & (filtered_df["YearsCodePro"] <= selected_experience_max)]

# load the dataset
try:
    connect()
    df = get_df("stack_overflow_survey")
except Exception as e:
    text("Error: Unable to load dataset. Please ensure the data file is in the 'data/' directory.")
    text("Follow the instructions in the README to download the dataset and run the app.")
    df = pd.DataFrame()

text("# Stack Overflow Developer Survey 2024 Explorer")

filtered_countries = sorted(df["Country"].dropna().unique())

# dashboard navigation
current_tab = selectbox(
    "Select Dashboard View",
    options=[
        "📊 Experience vs. Compensation",
        "🌍 Compare Countries"
    ],
    default="📊 Experience vs. Compensation"
)

separator()

if current_tab == "📊 Experience vs. Compensation":
    # Only visualize data if at least one country was selected
    if filtered_countries:
        country = selectbox("Select Country", filtered_countries, default=filtered_countries[0])

        filtered_df = df[df["Country"] == country].copy()
        filtered_df = normalize_years_of_experience(filtered_df)

        filtered_df = apply_experience_level_filter(filtered_df)

        separator()

        # Display summary statistics
        avg_salary = filtered_df["ConvertedCompYearly"].mean()
        median_salary = filtered_df["ConvertedCompYearly"].median()
        total_respondents = len(filtered_df)

        text(f"### Summary Statistics")
        text(f"**Average Salary:** ${avg_salary:,.2f}", size=0.3)
        text(f"**Median Salary:** ${median_salary:,.2f}", size=0.3)
        text(f"**Total Respondents:** {total_respondents}", size=0.3)

        # Perform linear regression to get trendline details
        X = sm.add_constant(filtered_df["YearsCodePro"])  # Add intercept
        y = filtered_df["ConvertedCompYearly"]
        model = sm.OLS(y, X).fit()
        slope, intercept = model.params["YearsCodePro"], model.params["const"]
        r_squared = model.rsquared

        # Display trendline equation and R² value
        text(f"### Trendline: Salary = {slope:.2f} * Experience + {intercept:.2f}", size=0.5)
        text(f"### R² Value: {r_squared:.3f}", size=0.5)

        fig = px.scatter(
            filtered_df,
            x="YearsCodePro",
            y="ConvertedCompYearly",
            color="YearsCodePro",
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

        # Add histogram for salary distribution
        hist_fig = px.histogram(
            filtered_df,
            x="ConvertedCompYearly",
            nbins=30,
            labels={"ConvertedCompYearly": "Annual Compensation (USD)"},
            title="Salary Distribution",
            template="plotly_white"
        )
        plotly(hist_fig)

        separator()

        # Display limited table (first 20 rows)
        table(filtered_df.head(20), title=f"Developer Responses from {country}")
    else:
        text("Please select at least one letter group to filter countries.")

elif current_tab == "🌍 Compare Countries":
    text("### Compare Developer Compensation and Experience Across Countries")

    if filtered_countries:
        # Remove 'None' selections
        selected_countries = [
            selectbox("Select First Country", filtered_countries, default=filtered_countries[0], size=0.3),
            selectbox("Select Second Country (Optional)", ["None"] + filtered_countries, default="None", size=0.3),
            selectbox("Select Third Country (Optional)", ["None"] + filtered_countries, default="None", size=0.3)
        ]

        # Filter data for selected countries
        filtered_df = df[df["Country"].isin(selected_countries)].copy()
        filtered_df = normalize_years_of_experience(filtered_df)
        filtered_df = apply_experience_level_filter(filtered_df)

        separator()

        # Generate box plot comparing salary distributions
        fig = px.box(
            filtered_df,
            x="Country",
            y="ConvertedCompYearly",
            color="Country",
            labels={
                "ConvertedCompYearly": "Annual Compensation (USD)",
                "Country": "Country"
            },
            title="Salary Distribution by Country",
            template="plotly_white"
        )
        plotly(fig)

        # Generate bar chart comparing median salaries by country
        median_salaries = filtered_df.groupby("Country")["ConvertedCompYearly"].median().reset_index()
        bar_fig = px.bar(
            median_salaries,
            x="Country",
            y="ConvertedCompYearly",
            color="Country",
            labels={
                "ConvertedCompYearly": "Median Annual Compensation (USD)",
                "Country": "Country"
            },
            title="Median Salary Comparison by Country",
            template="plotly_white"
        )
        plotly(bar_fig)

        # Salary comparison table with formatting
        salary_comparison = filtered_df.groupby("Country")["ConvertedCompYearly"].agg(
            min_salary="min",
            max_salary="max",
            avg_salary="mean",
            median_salary="median"
        ).reset_index()

        # Format the salaries so that they are readable
        salary_comparison["min_salary"] = salary_comparison["min_salary"].map("{:,.2f}".format)
        salary_comparison["max_salary"] = salary_comparison["max_salary"].map("{:,.2f}".format)
        salary_comparison["avg_salary"] = salary_comparison["avg_salary"].map("{:,.2f}".format)
        salary_comparison["median_salary"] = salary_comparison["median_salary"].map("{:,.2f}".format)

        # Display the salary comparison table with formatted values
        table(salary_comparison, title="Salary Comparison by Country")

        separator()

        # Display filtered table
        table(filtered_df.head(20), title=f"Developer Responses from Selected Countries")
    else:
        text("Please select at least one letter group to filter countries.")
