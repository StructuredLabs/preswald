from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# YouTube Global Statistics\n\n"
     "Explore YouTube video trends across categories, countries, and creators.\n\n"
    "**Author:** Sweta Pati  \n"
     "**Email:** spati@gmu.edu  \n"
     "**University:** George Mason University  \n"
     "**Data:** [Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023?resource=download)  \n"
     "**Data Source:** Kaggle")

connect()
df = get_df("youtube_statistics")

#Replacing NaN or 'nan' category values with "Miscellaneous":
df["category"] = df["category"].fillna("Miscellaneous")
df["category"] = df["category"].replace("nan", "Miscellaneous")

#Data Preprocessing (Conversions):
#Converted video views to Billion:
df["video views"] = df["video views"] / 1e9 
#Converted highest_monthly_earnings to Million:
df["highest_monthly_earnings"] = df["highest_monthly_earnings"] / 1e6  
# Converted subscribers to Million:
df["subscribers"] = df["subscribers"] / 1e6 
# Converted uploads to Thousands:
df["uploads"] = df["uploads"] / 1e3  

#Removing missing and invalid data:
df = df.dropna(subset=["uploads", "subscribers", "category", "Country"])
df = df[(df["uploads"] > 0) & (df["video views"] > 0) & (df["highest_monthly_earnings"] > 0)]

#Renaming Columns:
df.rename(columns={
    "video views": "video views (Converted to Billion)",
    "highest_monthly_earnings": "Earnings (Converted to Million $)",
    "subscribers": "subscribers (Converted to Million)",
    "uploads": "uploads (Converted to Thousand)"
}, inplace=True)

#Global filters of Views:
max_views = df["video views (Converted to Billion)"].max()
views_threshold = slider("Minimum Views (Converted to Billion)", min_val=0, max_val=max_views, default=0.5)

#Apply filtering:
filtered_df = df[df["video views (Converted to Billion)"] >= views_threshold]
if filtered_df.empty:
    text("No data available for the selected filter.")
else:
    #Precomputing Top Categories, YouTubers, and Countries:
    top_category = filtered_df.groupby("category")["video views (Converted to Billion)"].sum().idxmax()
    top_category_views = filtered_df.groupby("category")["video views (Converted to Billion)"].sum().max()
    
    top_youtuber = filtered_df.iloc[0]["Youtuber"]
    top_youtuber_views = filtered_df.iloc[0]["video views (Converted to Billion)"]

    top_country_grouped = df.groupby("Country", as_index=False)["video views (Converted to Billion)"].sum()
    top_country = top_country_grouped.loc[top_country_grouped["video views (Converted to Billion)"].idxmax()]
    top_country_name = top_country["Country"]
    top_country_views = top_country["video views (Converted to Billion)"]

    #Displaying Key Insights Before Visualizations:
    text(
        "## YouTube Global Statistics Overview\n"
        f"**Top Category:** {top_category} with {top_category_views:.2f}Billion views.\n\n"
        f"**Top YouTuber:** {top_youtuber} with {top_youtuber_views:.2f}Billion views.\n\n"
        f"**Top Country:** {top_country_name} with {top_country_views:.2f}Billion views.\n\n"
        "These insights provide a high-level view of YouTube trends. Explore further with interactive filters and charts below."
    )
 
#Plot 1:   
    text(
        "## 1. Plotting Views (Converted to Billion) by Category:\n"
        "This visualization highlights the most-watched youtube video categories.")
    #Bar Chart: Views by Category:
    fig1 = px.bar(filtered_df, x="category", y="video views (Converted to Billion)", color="category", 
                  title="Views by Category (Converted to Billion)", text_auto=".2s")
    plotly(fig1)

    #Generating Insights Dynamically:
    lowest_categories = filtered_df.groupby("category")["video views (Converted to Billion)"].sum().nsmallest(3)
    lowest_category_list = ", ".join(lowest_categories.index)

    text(
        "### Analyzed insights from Views (Converted to Billion) by Category:\n"
        f"- **{top_category} leads YouTube views**, accumulating approximately {top_category_views:.2f} billion views, highlighting its massive audience engagement.\n"
        f"- **Categories with lower viewership include** {lowest_category_list}, indicating a smaller but potentially loyal and niche audience.\n\n"
        "###  Major Takeaways:\n"
        "The dominance of high-engagement categories suggests that leisure content thrives on YouTube, while specialized content maintains a focused yet dedicated viewership. Content creators should align strategies with audience preferences for maximum impact."
    )

#Plot 2:   
    text(
        "## 2. Plotting Top YouTubers by Views (Converted to Billion):\n"
        "This visualization highlights the most-watched YouTube creators, ranked by total video views (in billions). "
    )
    #Bar Chart: Top YouTubers by Views:
    fig2 = px.bar(filtered_df, x="Youtuber", y="video views (Converted to Billion)", color="category", 
                  title="Top YouTubers by Views (Converted to Billion)", text_auto=".2s")
    plotly(fig2)

    #Generating Insights Dynamically:
    text(
        "### Analyzed insights from Top YouTubers by Views (Converted to Billion):\n"
        f"- **{top_youtuber} is the most-viewed YouTuber**, amassing **{top_youtuber_views:.2f}Billion views**, demonstrating a strong and consistent audience reach.\n"
        f"- The distribution of views among YouTubers indicates **category dominance**, where entertainment, music, and gaming channels often outperform niche educational or specialized content.\n\n"
        "### Major Takeaways:\n"
        "High-performing YouTubers generally produce content that appeals to broad audiences, such as music, entertainment, and gaming. "
        "Smaller YouTubers in niche categories can still achieve success through dedicated engagement and audience targeting."
    )

#Plot 3:   
    text(
        "## 3. Plotting YouTube Views (Converted to Billion) by Country:\n"
        "This visualization presents the total YouTube video views by country, highlighting regional engagement trends."
    )

    #World Map: Views by Country:
    fig3 = px.choropleth(top_country_grouped, 
                        locations="Country", 
                        locationmode="country names", 
                        color="video views (Converted to Billion)", 
                        title="YouTube Views (Converted to Billion) by Country",
                        color_continuous_scale="blues")
    plotly(fig3)

    #Generating dynamic insights:
    lowest_countries = top_country_grouped.nsmallest(3, "video views (Converted to Billion)")
    lowest_country_list = ", ".join(lowest_countries["Country"])

    text(
        "### Analyzed insights from YouTube Views by Country:\n"
        f"- **{top_country_name} leads with {top_country_views:.2f}Billion views**, showcasing its massive audience and content consumption.\n"
        f"- **Countries with lower YouTube engagement include** {lowest_country_list}, reflecting either smaller population sizes, lower internet penetration, or niche content interests.\n\n"
        "###  Major Takeaways:\n"
        "Countries with higher YouTube viewership are prime targets for content creators and advertisers. Meanwhile, emerging regions could offer untapped potential for localized content."
    )

#Plot 4:  
    text(
        "## 4. Plotting Category Trends (Converted to Billion) Across Countries:\n"
        "This heatmap illustrates how different YouTube categories perform across various countries, helping identify regional content preferences."
    )

    #Heatmap: Category Trends Across Countries:
    heatmap_df = df.groupby(["Country", "category"], as_index=False)["video views (Converted to Billion)"].sum()

    fig4 = px.density_heatmap(
        heatmap_df, 
        x="Country", 
        y="category", 
        z="video views (Converted to Billion)", 
        title="Category Trends (Converted to Billion) Across Countries", 
        color_continuous_scale="viridis"
    )

    plotly(fig4)

    #Generating dynamic insights:
    top_category_by_country = heatmap_df.groupby(["Country", "category"], as_index=False)["video views (Converted to Billion)"].sum()
    top_country_total_views = top_category_by_country.groupby("Country")["video views (Converted to Billion)"].sum()
    top_country_name = top_country_total_views.idxmax()  
    top_country_views = top_country_total_views.max()
    top_category_in_top_country = top_category_by_country[top_category_by_country["Country"] == top_country_name].nlargest(1, "video views (Converted to Billion)")
    top_category_name = top_category_in_top_country.iloc[0]["category"]
    top_category_views_in_top_country = top_category_in_top_country.iloc[0]["video views (Converted to Billion)"]
    category_totals = top_category_by_country.groupby("category")["video views (Converted to Billion)"].sum()
    lowest_categories = category_totals.nsmallest(3).index.tolist()
    lowest_category_list = ", ".join(lowest_categories)

    text(
        "### Analyzed insights from Category Trends Across Countries:\n"
        f"- **{top_country_name} has the highest YouTube views globally with {top_country_views:.2f}Billion views**, with **{top_category_name}** as the most-watched category in this country, accumulating **{top_category_views_in_top_country:.2f}Billion views**.\n"
        f"- **The least popular categories globally include** {lowest_category_list}, suggesting they cater to niche audiences rather than mass engagement.\n\n"
        "###  Major Takeaways:\n"
        "Different regions exhibit distinct content preferences. Recognizing these trends allows content creators to optimize their videos for the right audience."
    )

#Plot 5:  
    text(
        "## 5. Trending YouTubers (Last 30 Days):\n"
        "This visualization tracks the most-watched YouTubers over the past 30 days, showcasing their recent trends in viewership."
    )

    #Line Chart: Trending YouTubers (Last 30 Days)
    fig5 = px.line(
        filtered_df, 
        x="Youtuber", 
        y="video_views_for_the_last_30_days",
        title="Trending YouTubers (Last 30 Days)", 
        markers=True
    )

    plotly(fig5)

    #Generating dynamic insights:
    top_trending_youtuber = filtered_df.loc[filtered_df["video_views_for_the_last_30_days"].idxmax()]
    top_trending_name = top_trending_youtuber["Youtuber"]
    top_trending_views = top_trending_youtuber["video_views_for_the_last_30_days"]
    view_change = filtered_df["video_views_for_the_last_30_days"].diff().dropna()
    if not view_change.empty:
        largest_drop = view_change.nsmallest(1).values[0]
        largest_drop_index = view_change.nsmallest(1).index[0]
        youtuber_with_drop = filtered_df.loc[largest_drop_index, "Youtuber"]
    else:
        largest_drop = None
        youtuber_with_drop = None

    text(
        "### Analyzed insights from Trending YouTubers (Last 30 Days):\n"
        f"- **{top_trending_name} is the most trending YouTuber**, accumulating **{top_trending_views:,.0f} views** in the past 30 days.\n"
        f"- **{youtuber_with_drop} saw the largest drop in views**, indicating a potential decline in engagement or reduced content uploads.\n\n"
        "###  Major Takeaways:\n"
        "The rise and fall in YouTube trends are dynamic. Consistently trending creators likely have a strong content strategy, while others may experience fluctuations due to competition or shifting audience interests."
    )
#Plot 6:  
    text(
        "## 6. Understanding Subscribers (Converted to Million) vs Uploads Growth (Converted to Thousand):\n"
        "This visualization highlights how different YouTube categories grow their subscriber base based on content uploads."
    )

    #Moving Average:
    df = df.sort_values(by="uploads (Converted to Thousand)")
    df["smoothed_subscribers"] = df.groupby("category")["subscribers (Converted to Million)"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    #Multi Line Plot: Subscribers vs Uploads Growth:
    fig6 = px.line(
        df, 
        x="uploads (Converted to Thousand)", 
        y="smoothed_subscribers", 
        color="category",
        title="Subscribers vs Uploads Relationship (Smoothed by Moving Average)"
    )

    plotly(fig6)

    #Generating dynamic insights:
    top_growth_category = df.groupby("category")["smoothed_subscribers"].max().idxmax()
    top_growth_value = df.groupby("category")["smoothed_subscribers"].max().max()
    lowest_growth_category = df.groupby("category")["smoothed_subscribers"].max().idxmin()
    lowest_growth_value = df.groupby("category")["smoothed_subscribers"].max().min()
    text(
        "### Analyzed insights from Subscribers vs Uploads Growth:\n"
        f"- **{top_growth_category} shows the highest subscriber growth**, reaching approximately **{top_growth_value:.2f}M subscribers**, demonstrating strong audience engagement.\n"
        f"- **{lowest_growth_category} exhibits the least subscriber growth**, with only **{lowest_growth_value:.2f}M subscribers**, suggesting that more uploads do not necessarily translate to higher subscriber gain.\n\n"
        "### Major Takeaways:\n"
        "Not all categories grow equally with uploads. Competitive fields like Music & Entertainment gain high subscribers with fewer uploads, "
        "whereas niche categories require more consistent content to sustain growth. Creators should balance content quality and frequency for maximum engagement."
    )

    #Display Filtered Data Table:
    table(filtered_df, title="Filtered YouTube Data")