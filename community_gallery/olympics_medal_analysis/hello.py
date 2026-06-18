import plotly.express as px
import plotly.graph_objects as go
from preswald import connect, get_df, query, table, text, slider, plotly, selectbox, checkbox

text("# 🏅 Olympic Medal Explorer")
text("### Discover the glory of Olympic achievements across nations and games!")

connect() 
df = get_df("olympics_csv")

if df is None:
    text("Dataset could not be loaded.")
else:
    text("Olympics dataset loaded successfully! 🎉")

total_countries = df["NOC"].nunique()
total_medals = df["Total"].sum()
most_gold_country = df.loc[df["Gold"].idxmax(), "NOC"]
most_medals_country = df.loc[df["Total"].idxmax(), "NOC"]

text(f"### 🌎 {total_countries} Competing Nations | 🏅 {total_medals} Total Medals | 🥇 Most Gold: {most_gold_country} | 🏆 Most Medals: {most_medals_country}")

text("## 🔍 Explore Olympic Glory")
view_mode = selectbox(
    "Choose Your View",
    options=["Country Analysis", "Medal Comparison"],
    default="Country Analysis"
)

if view_mode == "Country Analysis":
    text("## Step 1: Select a Country")
    selected_country = selectbox("Select Country", options=sorted(df["NOC"].unique().tolist()), default="United States")
    
    text("## Step 2: Filter by Medal Counts")
    min_medals = slider("Minimum Total Medals", min_val=int(df["Total"].min()), max_val=int(df["Total"].max()), default=10)
    
    text(f"## 🏆 {selected_country} Olympic Performance")
    
    filtered_df = df[df["NOC"] == selected_country]
    dynamic_filtered_df = filtered_df[filtered_df["Total"] >= min_medals]
    
    gold_count = filtered_df["Gold"].sum()
    silver_count = filtered_df["Silver"].sum()
    bronze_count = filtered_df["Bronze"].sum()
    
    text(f"### Medal Cabinet: {gold_count} 🥇 | {silver_count} 🥈 | {bronze_count} 🥉")
    
    text(f"### Olympic Data for {selected_country} (Total Medals ≥ {min_medals})")
    table(dynamic_filtered_df, title="Olympic Medal History")
    
    text("## 📊 Medal Distribution")
    show_percentage = checkbox("Show as Percentage", default=False)
    
    if show_percentage and not dynamic_filtered_df.empty:
        total = dynamic_filtered_df[["Gold", "Silver", "Bronze"]].sum(axis=1)
        dynamic_filtered_df["Gold_pct"] = (dynamic_filtered_df["Gold"] / total * 100).round(1)
        dynamic_filtered_df["Silver_pct"] = (dynamic_filtered_df["Silver"] / total * 100).round(1)
        dynamic_filtered_df["Bronze_pct"] = (dynamic_filtered_df["Bronze"] / total * 100).round(1)
        
        fig_bar = px.bar(
            dynamic_filtered_df, 
            x="NOC", 
            y=["Gold_pct", "Silver_pct", "Bronze_pct"], 
            title=f"🥇🥈🥉 Medal Distribution for {selected_country} (%)",
            labels={"value": "Medal Percentage", "variable": "Medal Type"},
            barmode="stack",
            color_discrete_map={"Gold_pct": "gold", "Silver_pct": "silver", "Bronze_pct": "#cd7f32"}
        )
    else:
        fig_bar = px.bar(
            dynamic_filtered_df, 
            x="NOC", 
            y=["Gold", "Silver", "Bronze"], 
            title=f"🥇🥈🥉 Medal Distribution for {selected_country}",
            labels={"value": "Medal Count", "variable": "Medal Type"},
            barmode="group",
            color_discrete_map={"Gold": "gold", "Silver": "silver", "Bronze": "#cd7f32"}
        )
    
    fig_bar.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        transition_duration=500
    )
    plotly(fig_bar)
    
    text("## 🎖️ Medal Breakdown")
    if not dynamic_filtered_df.empty:
        df_melted = dynamic_filtered_df.melt(id_vars=["NOC"], value_vars=["Gold", "Silver", "Bronze"])
        fig_pie = px.pie(
            df_melted, 
            names="variable", 
            values="value", 
            title=f"Medal Breakdown for {selected_country}",
            color_discrete_sequence=["gold", "silver", "#cd7f32"],
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        plotly(fig_pie)
    else:
        text("No data available for the selected filters.")

else:  
    text("## 🌎 Compare Olympic Powerhouses")
    text("Select countries to compare their Olympic performance")
    
    country1 = selectbox("Select First Country", options=sorted(df["NOC"].unique().tolist()), default="United States")
    country2 = selectbox("Select Second Country", options=sorted(df["NOC"].unique().tolist()), default="China")
    
    compare_countries = [country1, country2]
    compare_df = df[df["NOC"].isin(compare_countries)]
    
    text("### Medal Comparison Table")
    table(compare_df, title="Country Comparison")
    
    fig_compare = px.bar(
        compare_df,
        x="NOC",
        y=["Gold", "Silver", "Bronze"],
        title="🏆 Country Medal Comparison",
        barmode="group",
        color_discrete_map={"Gold": "gold", "Silver": "silver", "Bronze": "#cd7f32"}
    )
    plotly(fig_compare)
    
    fig_radar = go.Figure()
    
    for country in compare_countries:
        country_data = df[df["NOC"] == country].iloc[0]
        fig_radar.add_trace(go.Scatterpolar(
            r=[country_data["Gold"], country_data["Silver"], country_data["Bronze"], 
               country_data["Total"]],
            theta=["Gold", "Silver", "Bronze", "Total"],
            fill='toself',
            name=country
        ))
        
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        title="Olympic Medal Profile Comparison"
    )
    plotly(fig_radar)

text("## 🔮 2028 Medal Predictor")
text("Based on historical trends, predict how many medals your favorite country might win in Los Angeles 2028!")

predictor_country = selectbox("Select Country for Prediction", options=sorted(df["NOC"].unique().tolist()), default="France")
country_data = df[df["NOC"] == predictor_country]

if not country_data.empty:
    avg_gold = country_data["Gold"].mean().round(1)
    avg_silver = country_data["Silver"].mean().round(1)
    avg_bronze = country_data["Bronze"].mean().round(1)
    total_predicted = (avg_gold + avg_silver + avg_bronze).round(1)
    
    text(f"### 2028 Prediction for {predictor_country}:")
    text(f"Gold: 🥇 {avg_gold} | Silver: 🥈 {avg_silver} | Bronze: 🥉 {avg_bronze} | Total: 🏅 {total_predicted}")
    
    pred_data = {
        "Medal": ["Gold", "Silver", "Bronze", "Total"],
        "Count": [avg_gold, avg_silver, avg_bronze, total_predicted]
    }
    
    fig_pred = px.bar(
        pred_data,
        x="Medal",
        y="Count",
        title=f"Predicted 2028 Olympic Performance for {predictor_country}",
        color="Medal",
        color_discrete_map={"Gold": "gold", "Silver": "silver", "Bronze": "#cd7f32", "Total": "#1e88e5"}
    )
    plotly(fig_pred)
    
    text("*This prediction is for entertainment purposes only and based on historical averages.")

text("## 🎯 Olympic Trivia")
trivia_questions = [
    "Which country has won the most Olympic gold medals in history? (USA)",
    "Which Olympic sport has been contested at every modern Summer Olympic Games since 1896? (Athletics)",
    "Who is the most decorated Olympic athlete of all time? (Michael Phelps with 28 medals)"
]
text(f"### Fun Fact: {trivia_questions[0]}")
