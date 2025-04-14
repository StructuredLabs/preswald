from preswald import text, plotly, connect, get_df, query
import pandas as pd
import plotly.express as px

# --- 🔹 Updated Introduction ---
text("# Social Media Engagement Analysis Dashboard")
text("""
This dashboard provides insights into viral social media trends using the **Viral Social Media Trends Dataset**. 📊  
It contains **5,000 viral posts** from platforms like **TikTok, Instagram, Twitter, and YouTube**.  
We analyze key engagement metrics such as **views, likes, shares, and comments** to uncover viral patterns. 🚀  

### What You’ll Find in This Dashboard:
- **Top 10 Viral Hashtags** → Discover the hashtags driving the most engagement. 🔥  
- **Engagement Share by Content Type** → See which content formats (Reels, Videos, Shorts, Tweets) perform best. 🎥  
- **Engagement by Region** → Find out which countries generate the most viral content. 🌍  

These insights can help **marketers, content creators, and researchers** better understand social media virality.  
""")

# Connect to Preswald
connect()
df = get_df("vsmt_csv")

# Check if df is loaded correctly
if df is None or df.empty:
    text("Error: Dataset could not be loaded. Please check the file name.")
else:
    # --- 🔹 1. Top 10 Viral Hashtags ---
    text("## Top 10 Viral Hashtags")
    text("This horizontal bar chart highlights the top trending hashtags based on total engagement.")

    sql = """
    SELECT Hashtag, SUM(Views + Likes + Shares + Comments) AS Total_Engagement
    FROM 'vsmt_csv'
    GROUP BY Hashtag
    ORDER BY Total_Engagement DESC
    LIMIT 10
    """
    top_hashtags = query(sql, "vsmt_csv")

    fig = px.bar(
        top_hashtags,
        x="Total_Engagement",
        y="Hashtag",
        title="Top 10 Viral Hashtags by Engagement",
        labels={"Total_Engagement": "Total Engagement", "Hashtag": "Trending Hashtag"},
        orientation="h",
        color="Total_Engagement",
        color_continuous_scale=px.colors.sequential.Magma,
    )

    fig.update_layout(xaxis_title="Total Engagement", yaxis_title="Trending Hashtags")
    plotly(fig)

    # --- 🔹 2. Engagement Share by Content Type (Pie Chart) ---
    text("## Engagement Share by Content Type")
    text("This pie chart illustrates how different content types contribute to overall engagement.")

    sql = """
    SELECT Content_Type, SUM(Views + Likes + Shares + Comments) AS Total_Engagement
    FROM 'vsmt_csv'
    GROUP BY Content_Type
    ORDER BY Total_Engagement DESC
    """
    engagement_by_content = query(sql, "vsmt_csv")

    fig = px.pie(
        engagement_by_content,
        names="Content_Type",
        values="Total_Engagement",
        title="Engagement Share by Content Type",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    plotly(fig)

    # --- 🔹 3. NEW: Engagement by Region (Bar Chart) ---
    text("## Engagement by Region")
    text("This bar chart shows which countries had the most viral posts based on total engagement.")

    sql = """
    SELECT Region, SUM(Views + Likes + Shares + Comments) AS Total_Engagement
    FROM 'vsmt_csv'
    GROUP BY Region
    ORDER BY Total_Engagement DESC
    LIMIT 10
    """
    engagement_by_region = query(sql, "vsmt_csv")

    if engagement_by_region is not None and not engagement_by_region.empty:
        fig = px.bar(
            engagement_by_region,
            x="Region",
            y="Total_Engagement",
            title="Top 10 Regions with Highest Engagement",
            labels={"Region": "Country", "Total_Engagement": "Total Engagement"},
            color="Total_Engagement",
            color_continuous_scale=px.colors.sequential.Viridis,
        )

        fig.update_layout(xaxis_title="Country", yaxis_title="Total Engagement")
        plotly(fig)
    else:
        text("Error: No data available for regions.")
