import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text


text("# Exploring the SF Salaries Dataset with Preswald")
text(
    "Exploring trends in compensation, overtime pay and employee benefits over the years"
)


def preprocess_data(df):
    # Drop the Notes column as it is entirely Null
    df = df.drop("Notes", axis=1)

    # Convert 'BasePay', 'OvertimePay', and 'Benefits' to numeric, coercing errors to NaN
    df["BasePay"] = pd.to_numeric(df["BasePay"], errors="coerce")
    df["OvertimePay"] = pd.to_numeric(df["OvertimePay"], errors="coerce")
    df["Benefits"] = pd.to_numeric(df["Benefits"], errors="coerce")

    # Filter out rows where pay is less than 0
    df = df[df["BasePay"] >= 0]
    df = df[df["OvertimePay"] >= 0]
    df = df[df["Benefits"] >= 0]

    # Calculate medians and fill missing values without using inplace
    base_pay_median = df["BasePay"].median()
    df["BasePay"] = df["BasePay"].fillna(base_pay_median)
    df["OvertimePay"] = df["OvertimePay"].fillna(0)
    df["Benefits"] = df["Benefits"].fillna(0)

    # Fill missing Job Titles without using inplace
    df["JobTitle"] = df["JobTitle"].fillna("Not Provided")
    # Fill in the missing Status with UK (Unknown)
    df["Status"] = df["Status"].fillna("UK")

    # Remove any duplicates if they exist
    df = df.drop_duplicates()

    # Standardize the job titles
    df["JobTitle"] = df["JobTitle"].str.lower()

    return df


# Read and Prepocess the dataset
connect()
df = get_df("salaries_csv")
df = preprocess_data(df)

# Display the table
# Displaying a subset for faster processing
subset = df.iloc[:50]

# Interactive UI
threshold = slider("TotalPay", min_val=0, max_val=1000000, default=25000)
table(subset[subset["TotalPay"] > threshold], title="Dynamic Data View for TotalPay")

# 1: Average Total Pay by Year
text("## Average Total Pay by Year")
# Group data and convert 'Year' to integer to avoid decimal issues
grouped_df = df.groupby("Year")["TotalPayBenefits"].mean().reset_index()
grouped_df["Year"] = grouped_df["Year"].astype(int)  # Ensure 'Year' is integer

fig1 = px.line(
    grouped_df,
    x="Year",
    y="TotalPayBenefits",
    title="Average Total Pay + Benefits Over Time",
)

# Update layout to enforce integer year labels
fig1.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=grouped_df["Year"].unique(),  # Use the grouped DataFrame's years
        ticktext=[str(year) for year in grouped_df["Year"].unique()],
    )
)
plotly(fig1)

# 2: Distribution of Pay Components
text("## Distribution of Pay Components")
fig2 = px.histogram(
    df,
    x="BasePay",
    nbins=50,
    title="Distribution of Base Pay",
    range_x=[0, df["BasePay"].max()],
)
fig3 = px.histogram(
    df,
    x="OvertimePay",
    nbins=50,
    title="Distribution of Overtime Pay",
    range_x=[0, df["OvertimePay"].max()],
)
fig4 = px.histogram(
    df,
    x="Benefits",
    nbins=50,
    title="Distribution of Benefits",
    range_x=[0, df["Benefits"].max()],
)
plotly(fig2)
plotly(fig3)
plotly(fig4)

# 3: Base Pay vs. Overtime Pay
text("## Base Pay vs. Overtime Pay")
fig5 = px.scatter(df, x="BasePay", y="OvertimePay", title="Base Pay vs. Overtime Pay")
plotly(fig5)

# 4: Benefits as a Proportion of Total Pay
text("## Benefits as a Proportion of Total Pay")
df["BenefitsProportion"] = df["Benefits"] / df["TotalPayBenefits"]
fig6 = px.scatter(
    df,
    x="TotalPayBenefits",
    y="BenefitsProportion",
    title="Benefits as a Proportion of Total Pay",
)
plotly(fig6)


# Additional insights text
text("## Key Insights")
text("""
- The average total compensation for city employees shows a slight decrease from 2012 to 2013. It further decreses from 2013 to 2014. These trends may reflect adjustments for inflation and changes in city policies.
- A significant number of employees have a base pay of $0, which may indicate roles that are either temporary or unpaid. For those who do receive a salary, most have a base pay ranging from $50,000 to $100,000. The distribution shows that fewer employees earn higher salaries, with the numbers decreasing as the pay increases.
- Overtime pay is not a significant component of total compensation for most employees, as it is predominantly zero. In contrast, benefits play a crucial role in the overall compensation package, with a notable proportion of the workforce receiving benefits that constitute about 20% to 40% of their total compensation. This underscores the significance of benefits in employee remuneration.
""")
