from preswald import connect, get_df, text, table, slider, plotly
import plotly.express as px

def parse_metric(value_str):
    """
    Convert strings like "13.8M" or "856.3K" into float.
    If there's no suffix, parse directly or return 0 if empty.
    """
    s = str(value_str).strip().upper()
    if s.endswith('M'):
        return float(s.replace('M', '')) * 1e6
    elif s.endswith('K'):
        return float(s.replace('K', '')) * 1e3
    else:
        return float(s) if s else 0.0


connect()

df = get_df("top_tiktok_influencers_csv")
if df is None:
    text("**Error:** Dataset 'top_tiktok_influencers_csv' not found or failed to load.")
    raise Exception("Dataset 'top_tiktok_influencers_csv' is missing")

df["Subscribers_numeric"] = df["Subscribers"].apply(parse_metric)
df["Views_numeric"]       = df["Views avg"].apply(parse_metric)
df["Comments_numeric"]    = df["Comments avg"].apply(parse_metric)
df["Likes_numeric"]       = df["Likes avg"].apply(parse_metric)
df["Shares_numeric"]      = df["Shares avg"].apply(parse_metric)

text("## ✨ TikTok Influencer Analysis Dashboard ✨")
text("Welcome to the ultimate exploration of TikTok influencers! "\
     "Here, you can filter by various metrics, visualize relationships, and discover who’s rocking the platform. 🚀")

text("### 🎚️ Set Your Filters:")
min_subscribers_millions = slider("Min Subscribers (M)", min_val=0, max_val=200, default=1)
min_subscribers = min_subscribers_millions * 1e6

min_views_millions = slider("Min Views (M)", min_val=0, max_val=200, default=0)
min_views = min_views_millions * 1e6

min_comments_thousands = slider("Min Comments (K)", min_val=0, max_val=1000, default=0)
min_comments = min_comments_thousands * 1e3

df_filtered = df[
    (df["Subscribers_numeric"] >= min_subscribers) &
    (df["Views_numeric"]       >= min_views)       &
    (df["Comments_numeric"]    >= min_comments)
]

if df_filtered.empty:
    text("😢 **No influencers found** with the selected filters. Try lowering your thresholds.")
else:
    text(f"### **Influencers Matching Your Criteria**")
    table(df_filtered, title="Filtered Influencers")

text("### 📊 Visualizations")

text("#### 1. Tiktoker vs. Subscribers")
fig_bar_sub = px.bar(
    df_filtered,
    x="Tiktoker name",
    y="Subscribers_numeric",
    title="Subscribers by Tiktoker",
    color="Tiktoker name",
    hover_data=["Tiktok name", "Likes avg", "Comments avg", "Shares avg"],
)
fig_bar_sub.update_xaxes(type='category', tickangle=45)
plotly(fig_bar_sub)

text("#### 2. Tiktoker vs. Views")
fig_bar_views = px.bar(
    df_filtered,
    x="Tiktoker name",
    y="Views_numeric",
    title="Views by Tiktoker",
    color="Tiktoker name",
    hover_data=["Tiktok name", "Likes avg", "Comments avg", "Shares avg"],
)
fig_bar_views.update_xaxes(type='category', tickangle=45)
plotly(fig_bar_views)

text("#### 3. Subscribers vs. Views")
fig_scatter = px.scatter(
    df_filtered,
    x="Subscribers_numeric",
    y="Views_numeric",
    title="Subscribers vs. Views",
    hover_data=["Tiktoker name", "Tiktok name", "Likes avg", "Comments avg", "Shares avg"],
    labels={"Subscribers_numeric": "Subscribers", "Views_numeric": "Views"}
)
plotly(fig_scatter)

text("#### 4. Likes vs. Comments")
fig_likes_comments = px.scatter(
    df_filtered,
    x="Likes_numeric",
    y="Comments_numeric",
    title="Likes vs. Comments",
    hover_data=["Tiktoker name", "Tiktok name"],
    labels={"Likes_numeric": "Likes", "Comments_numeric": "Comments"}
)
plotly(fig_likes_comments)

text("### Thank you for using the TikTok Influencer Analysis Dashboard! "\
     "Feel free to tweak filters above to discover different insights. 🎉")
