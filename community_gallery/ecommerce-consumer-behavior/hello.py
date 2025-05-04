import pandas as pd
import plotly.express as px
from preswald import (
    Workflow,
    text,
    plotly,
    connect,
    get_df,
    table,
    selectbox,
    slider,
    # checkbox,
)

# Create a workflow instance
workflow = Workflow()


# --- WELCOME MESSAGE ---
@workflow.atom()
def welcome_message():
    text("# 🛒 E-commerce Consumer Behavior Analysis")
    text(
        "### Explore trends in customer behavior from an e-commerce dataset. Filter by purchase category, channel, and spending!"
    )


# --- DATA LOADING & CLEANING ---
@workflow.atom()
def load_data():
    connect()  # Initialize connection to preswald.toml data sources
    df = get_df(
        "ecommerce_consumer_behavior_csv"
    ).dropna()  # Load the e-commerce dataset

    # Clean and convert key columns
    df["Purchase_Amount"] = (
        df["Purchase_Amount"].str.replace("[$,]", "", regex=True).astype(float)
    )
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Frequency_of_Purchase"] = pd.to_numeric(
        df["Frequency_of_Purchase"], errors="coerce"
    )
    df["Time_Spent_on_Product_Research(hours)"] = pd.to_numeric(
        df["Time_Spent_on_Product_Research(hours)"], errors="coerce"
    )
    df["Time_to_Decision"] = pd.to_numeric(df["Time_to_Decision"], errors="coerce")
    df["Product_Rating"] = pd.to_numeric(df["Product_Rating"], errors="coerce")

    df["Discount_Sensitivity"] = pd.to_numeric(
        df["Discount_Sensitivity"], errors="coerce"
    )
    df["Return_Rate"] = pd.to_numeric(df["Return_Rate"], errors="coerce")
    df["Customer_Satisfaction"] = pd.to_numeric(
        df["Customer_Satisfaction"], errors="coerce"
    )
    return df


# --- USER FILTERS ---
@workflow.atom(dependencies=["load_data"])
def user_filters(load_data):
    text(
        "## These are global filters that will be applied to the rest of the analysis:"
    )
    df = load_data
    # Filter by Purchase Category and Purchase Channel using selectbox
    purchase_categories = sorted(df["Purchase_Category"].unique())
    selected_category = selectbox(
        "Filter by Purchase Category:",
        options=["All"] + purchase_categories,
        default="All",
    )

    purchase_channels = sorted(df["Purchase_Channel"].unique())
    selected_channel = selectbox(
        "Filter by Purchase Channel:",
        options=["All"] + purchase_channels,
        default="All",
    )

    # Slider to set maximum purchase amount
    max_possible_amount = int(df["Purchase_Amount"].max())
    max_amount = slider(
        "Select Maximum Purchase Amount",
        min_val=0,
        max_val=max_possible_amount,
        default=max_possible_amount,
    )

    # Apply filters
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Purchase_Category"] == selected_category]
    if selected_channel != "All":
        filtered_df = filtered_df[filtered_df["Purchase_Channel"] == selected_channel]
    filtered_df = filtered_df[filtered_df["Purchase_Amount"] <= max_amount]

    text(f"**Total Customers Found:** {len(filtered_df)}")

    return filtered_df


# --- COLUMN SELECTION FOR DISPLAY ---
@workflow.atom(dependencies=["user_filters"])
def display_table(user_filters):
    df = user_filters
    # Define a dictionary with column names and their default checkbox values
    col_defaults = {
        "Customer_ID": True,
        "Age": True,
        "Gender": True,
        "Income_Level": True,
        "Purchase_Category": True,
        "Purchase_Amount": True,
        "Purchase_Channel": True,
        "Product_Rating": True,
        "Time_Spent_on_Product_Research(hours)": False,
        "Return_Rate": False,
        "Customer_Satisfaction": True,
        "Time_to_Decision": False,
    }

    # Create a dictionary to store user selections
    # selected_columns = {}
    # text("## Select Columns to Display in Table")
    # for col, default in col_defaults.items():
    #     # Each checkbox is created individually; they will appear vertically
    #     selected_columns[col] = checkbox(f"Show {col}", default=default)

    # Build the final list of columns to show based on user selections
    columns_to_show = [col for col, show in col_defaults.items() if show]

    # Display the filtered data with the selected columns
    table(df[columns_to_show], limit=10)


# --- VISUALIZATION 1: Age vs. Purchase Amount ---
@workflow.atom(dependencies=["user_filters"])
def age_vs_purchase_amount(user_filters):
    df = user_filters
    text("## Age vs. Purchase Amount")
    fig1 = px.scatter(
        df,
        x="Age",
        y="Purchase_Amount",
        color="Purchase_Channel",
        hover_data=["Customer_ID", "Location", "Purchase_Category"],
        title="Scatter Plot: Age vs. Purchase Amount (by Channel)",
    )
    fig1.update_traces(textposition="top center", marker=dict(size=12))
    fig1.update_layout(template="plotly_white", width=800, height=450)
    plotly(fig1)


# --- VISUALIZATION 2: Average Purchase Amount by Category ---
@workflow.atom(dependencies=["user_filters"])
def avg_purchase_amount_by_category(user_filters):
    df = user_filters
    text("## Average Purchase Amount by Category")
    avg_purchase = (
        df.groupby("Purchase_Category")["Purchase_Amount"].mean().reset_index()
    )
    fig2 = px.bar(
        avg_purchase,
        x="Purchase_Category",
        y="Purchase_Amount",
        text="Purchase_Amount",
        title="Average Purchase Amount per Category",
        labels={
            "Purchase_Category": "Category",
            "Purchase_Amount": "Avg. Purchase Amount ($)",
        },
    )
    fig2.update_layout(
        template="plotly_white", xaxis_tickangle=-45, width=800, height=450
    )
    plotly(fig2)


# --- VISUALIZATION 3: Payment Method Distribution ---
@workflow.atom(dependencies=["user_filters"])
def payment_method_distribution(user_filters):
    df = user_filters
    text("## Payment Method Distribution")
    payment_counts = df["Payment_Method"].value_counts().reset_index()
    payment_counts.columns = ["Payment_Method", "Count"]
    fig3 = px.pie(
        payment_counts,
        names="Payment_Method",
        values="Count",
        title="Payment Method Distribution",
    )
    fig3.update_layout(width=800, height=450)
    plotly(fig3)


# --- VISUALIZATION 4: Purchase Amount Distribution by Income Level ---
@workflow.atom(dependencies=["user_filters"])
def purchase_amount_distribution_by_income_level(user_filters):
    df = user_filters
    text("## Purchase Amount Distribution by Income Level")
    fig4 = px.box(
        df,
        x="Income_Level",
        y="Purchase_Amount",
        color="Income_Level",
        title="Purchase Amount Distribution Across Income Levels",
        labels={
            "Income_Level": "Income Level",
            "Purchase_Amount": "Purchase Amount ($)",
        },
    )
    fig4.update_layout(template="plotly_white", width=800, height=450)
    plotly(fig4)


# --- VISUALIZATION 5: Correlation Heatmap ---
@workflow.atom(dependencies=["user_filters"])
def correlation_heatmap(user_filters):
    df = user_filters
    text("## Correlation Heatmap of Key Numerical Variables")
    # Select numerical columns for correlation analysis
    num_cols = [
        "Age",
        "Purchase_Amount",
        "Frequency_of_Purchase",
        "Product_Rating",
        "Time_Spent_on_Product_Research(hours)",
        "Return_Rate",
        "Customer_Satisfaction",
        "Time_to_Decision",
    ]
    corr_matrix = df[num_cols].corr()
    fig5 = px.imshow(
        corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap"
    )
    fig5.update_layout(width=800, height=500)
    plotly(fig5)


# --- VISUALIZATION 6: Factors affecting Customer Satisfaction --
@workflow.atom(dependencies=["user_filters"])
def payment_mode_by_location(user_filters):
    df = user_filters

    text("## Factors Affecting Customer Satisfaction")
    # List of candidate features
    features = [
        "Purchase_Amount",
        "Frequency_of_Purchase",
        "Product_Rating",
        "Time_Spent_on_Product_Research(hours)",
        "Return_Rate",
        "Time_to_Decision",
    ]

    # Compute correlation for each feature with Customer_Satisfaction
    corr_values = {}
    for feature in features:
        corr = df["Customer_Satisfaction"].corr(df[feature])
        corr_values[feature] = corr

    # Convert to DataFrame and sort by absolute correlation
    corr_df = pd.DataFrame(
        list(corr_values.items()), columns=["Feature", "Correlation_with_Satisfaction"]
    )
    corr_df["Abs_Correlation"] = corr_df["Correlation_with_Satisfaction"].abs()
    corr_df = corr_df.sort_values(by="Abs_Correlation", ascending=False)

    text("### Bar Chart: Correlation of Factors with Customer Satisfaction")
    fig_corr = px.bar(
        corr_df,
        x="Feature",
        y="Correlation_with_Satisfaction",
        text="Correlation_with_Satisfaction",
        title="Correlation of Key Factors with Customer Satisfaction",
        labels={"Correlation_with_Satisfaction": "Correlation Coefficient"},
    )
    fig_corr.update_layout(
        template="plotly_white", width=800, height=500, xaxis_tickangle=-45
    )
    plotly(fig_corr)

    # --- Identify the most correlated factor ---
    top_feature = corr_df.iloc[0]["Feature"]
    top_corr = corr_df.iloc[0]["Correlation_with_Satisfaction"]
    text(
        f"**The factor most strongly associated with Customer Satisfaction is {top_feature} (Correlation = {top_corr:.2f}).**"
    )


# --- FUN FACTS SECTION ---
@workflow.atom(dependencies=["user_filters"])
def extras(user_filters):
    df = user_filters
    text("## 🎉 Fun Facts")
    fact_choice = selectbox(
        "Select a Fun Fact:",
        options=[
            "Highest Purchase Amount",
            "Lowest Purchase Amount",
            "Fastest Decision Time",
            "Most Frequent Purchaser",
        ],
        default="Highest Purchase Amount",
    )

    if fact_choice == "Highest Purchase Amount":
        best = df.loc[df["Purchase_Amount"].idxmax()]
        text(
            f"**Customer {best['Customer_ID']}** spent the most: **${best['Purchase_Amount']:.2f}** in **{best['Purchase_Category']}**."
        )
    elif fact_choice == "Lowest Purchase Amount":
        worst = df.loc[df["Purchase_Amount"].idxmin()]
        text(
            f"**Customer {worst['Customer_ID']}** spent the least: **${worst['Purchase_Amount']:.2f}**."
        )
    elif fact_choice == "Fastest Decision Time":
        fastest = df.loc[df["Time_to_Decision"].idxmin()]
        text(
            f"**Customer {fastest['Customer_ID']}** took only **{fastest['Time_to_Decision']}** day(s) to decide on a purchase."
        )
    elif fact_choice == "Most Frequent Purchaser":
        frequent = df.loc[df["Frequency_of_Purchase"].idxmax()]
        text(
            f"**Customer {frequent['Customer_ID']}** purchased **{frequent['Frequency_of_Purchase']}** times."
        )


# --- CONCLUSION ---
@workflow.atom()
def conclusion():
    text("## Conclusion")
    text(
        "Explore trends across age, spending, and income levels and use the fun facts to discover extreme cases in the dataset. Happy analyzing!"
    )


result = workflow.execute()
