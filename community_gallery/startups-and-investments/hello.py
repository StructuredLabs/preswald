import pandas as pd
import plotly.express as px
from preswald import text, plotly, table, slider

csv_path = "data/startup_growth_investment_data.csv"
try:
    df = pd.read_csv(csv_path)
    text(f"✅ Data loaded successfully! {len(df)} rows available.")
except Exception as e:
    text(f"⚠️ Error loading data: {e}")
    df = None

if df is not None:
    text("# 🚀 Startup Growth & Investment Insights")
    text("Analyze startup funding, valuation, and growth trends dynamically.")

    text(f"Columns: {list(df.columns)}")

    # **User Control - Dynamic Filtering Based on Investment Amount**
    if "Investment Amount (USD)" in df.columns:
        investment_threshold = slider(
            "Minimum Investment Amount (USD)",
            min_val=0,
            max_val=10_000_000_000,
            default=50_000_000,
        )
        filtered_startups = df[df["Investment Amount (USD)"] > investment_threshold]
        table(filtered_startups, title="Startups with Investment Above Threshold")
    else:
        text("⚠️ Column 'Investment Amount (USD)' not found!")

    # **scatter plot**
    if {
        "Funding Rounds",
        "Valuation (USD)",
        "Startup Name",
        "Investment Amount (USD)",
        "Industry",
    }.issubset(df.columns):
        fig = px.scatter(
            df,
            x="Funding Rounds",
            y="Valuation (USD)",
            text="Startup Name",
            size="Investment Amount (USD)",
            title="Funding Rounds vs. Valuation (USD)",
            labels={
                "Funding Rounds": "Number of Funding Rounds",
                "Valuation (USD)": "Startup Valuation (in USD)",
            },
            hover_data=["Country", "Number of Investors", "Year Founded"],
        )  # Additional details on hover

        fig.update_traces(textposition="top center", marker=dict(opacity=0.7))
        fig.update_layout(template="plotly_white")

        plotly(fig)
    else:
        text("⚠️ Missing required columns for scatter plot!")


# working with unreadable scater plot

# import pandas as pd
# import plotly.express as px
# from preswald import text, plotly, table, slider

# # **Load the dataset**
# csv_path = "data/startup_growth_investment_data.csv"  # Ensure correct path
# try:
#     df = pd.read_csv(csv_path)
#     text(f"✅ Data loaded successfully! {len(df)} rows available.")
# except Exception as e:
#     text(f"⚠️ Error loading data: {e}")
#     df = None

# if df is not None:
#     text("# 🚀 Startup Growth & Investment Insights")
#     text("Analyze startup funding, valuation, and growth trends dynamically.")

#     # **Check column names before filtering**
#     text(f"Columns: {list(df.columns)}")

#     # **Filter startups with valuation above $1B**
#     if "Valuation (USD)" in df.columns:
#         filtered_df = df[df["Valuation (USD)"] > 1_000_000_000]
#         table(filtered_df, title="Startups with Valuation Over $1B")
#     else:
#         text("⚠️ Column 'Valuation (USD)' not found!")

#     # **User Control - Dynamic Filtering Based on Investment Amount**
#     if "Investment Amount (USD)" in df.columns:
#         investment_threshold = slider("Minimum Investment Amount (USD)", min_val=0, max_val=5_000_000_000, default=50_000_000)
#         filtered_startups = df[df["Investment Amount (USD)"] > investment_threshold]
#         table(filtered_startups, title="Startups with Investment Above Threshold")
#     else:
#         text("⚠️ Column 'Investment Amount (USD)' not found!")

#     # **Create an interactive scatter plot**
#     if {"Funding Rounds", "Valuation (USD)", "Startup Name", "Investment Amount (USD)", "Industry"}.issubset(df.columns):
#         fig = px.scatter(df,
#                          x="Funding Rounds",
#                          y="Valuation (USD)",
#                          text="Startup Name",
#                          size="Investment Amount (USD)",  # Bubble size represents investment
#                          color="Industry",  # Different colors for industries
#                          title="Funding Rounds vs. Valuation (USD)",
#                          labels={"Funding Rounds": "Number of Funding Rounds",
#                                  "Valuation (USD)": "Startup Valuation (in USD)"},
#                          hover_data=["Country", "Number of Investors", "Year Founded"])  # Additional details on hover

#         fig.update_traces(textposition="top center", marker=dict(opacity=0.7))
#         fig.update_layout(template="plotly_white")

#         # **Display the plot**
#         plotly(fig)
#     else:
#         text("⚠️ Missing required columns for scatter plot!")


# data not laoding

# from preswald import text, plotly, connect, get_df, table, query, slider
# import plotly.express as px

# # **Load the dataset**
# connect()
# df = get_df("startup_growth_investment_data")

# if df is None:
#     text("⚠️ Error: Dataset failed to load. Check the source name or connection.")
# else:
#     text(f"✅ Data loaded successfully! {len(df)} rows available.")

#     text("# 🚀 Startup Growth & Investment Insights")
#     text("Analyze startup funding, valuation, and growth trends dynamically.")

#     # **SQL Query - Filter startups with valuation above a threshold**
#     sql = "SELECT * FROM startup_growth_investment_data WHERE `Valuation (USD)` > 1000000000"
#     filtered_df = query(sql, "startup_growth_investment_data")

#     # **Show filtered data table**
#     table(filtered_df, title="Startups with Valuation Over $1B")

#     # **User Control - Dynamic Filtering Based on Investment Amount**
#     investment_threshold = slider("Minimum Investment Amount (USD)", min_val=0, max_val=5000000000, default=50000000)

#     # **Filtered Table Based on User Input**
#     if "Investment Amount (USD)" in df.columns:
#         filtered_startups = df[df["Investment Amount (USD)"] > investment_threshold]
#         table(filtered_startups, title="Startups with Investment Above Threshold")
#     else:
#         text("⚠️ Column 'Investment Amount (USD)' not found in dataset.")

#     # **Create an interactive scatter plot**
#     fig = px.scatter(df,
#                      x="Funding Rounds",
#                      y="Valuation (USD)",
#                      text="Startup Name",
#                      size="Investment Amount (USD)",  # Bubble size represents investment
#                      color="Industry",  # Different colors for industries
#                      title="Funding Rounds vs. Valuation (USD)",
#                      labels={"Funding Rounds": "Number of Funding Rounds",
#                              "Valuation (USD)": "Startup Valuation (in USD)"},
#                      hover_data=["Country", "Number of Investors", "Year Founded"])  # Additional details on hover

#     fig.update_traces(textposition="top center", marker=dict(opacity=0.7))
#     fig.update_layout(template="plotly_white")

#     # **Display the plot**
#     plotly(fig)


# view error

# from preswald import text, plotly, connect, get_df, table, query, slider, view
# import plotly.express as px

# # **Load the dataset**
# connect()
# df = get_df("startup_growth_investment_data")

# text("# 🚀 Startup Growth & Investment Insights")
# text("Analyze startup funding, valuation, and growth trends dynamically.")

# # **SQL Query - Filter startups with valuation above a threshold**
# sql = "SELECT * FROM startup_growth_investment_data WHERE `Valuation (USD)` > 1000000000"
# filtered_df = query(sql, "startup_growth_investment_data")

# # **Show filtered data table**
# table(filtered_df, title="Startups with Valuation Over $1B")

# # **User Control - Dynamic Filtering Based on Investment Amount**
# investment_threshold = slider("Minimum Investment Amount (USD)", min_val=0, max_val=5000000000, default=50000000)

# # **Filtered Table Based on User Input**
# view(table(df[df["Investment Amount (USD)"] > investment_threshold], title="Startups with Investment Above Threshold"))

# # **Create an interactive scatter plot**
# fig = px.scatter(df,
#                  x="Funding Rounds",
#                  y="Valuation (USD)",
#                  text="Startup Name",
#                  size="Investment Amount (USD)",  # Bubble size represents investment
#                  color="Industry",  # Different colors for industries
#                  title="Funding Rounds vs. Valuation (USD)",
#                  labels={"Funding Rounds": "Number of Funding Rounds",
#                          "Valuation (USD)": "Startup Valuation (in USD)"},
#                  hover_data=["Country", "Number of Investors", "Year Founded"])  # Additional details on hover

# # **Enhance aesthetics**
# fig.update_traces(textposition="top center", marker=dict(opacity=0.7))
# fig.update_layout(template="plotly_white")

# # **Display the plot**
# plotly(fig)
