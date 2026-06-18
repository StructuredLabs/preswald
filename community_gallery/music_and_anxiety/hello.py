from preswald import connect, get_df, text, plotly
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

connect()
df = get_df("mxmh_survey_results")

# Convert relevant columns to numeric
mental_health_columns = ["Anxiety", "Depression", "Insomnia", "OCD"]
df[mental_health_columns] = df[mental_health_columns].apply(pd.to_numeric, errors='coerce')
df["Hours per day"] = pd.to_numeric(df["Hours per day"], errors='coerce')

# 1. General Overview

text("# Music & Mental Health: A Deeper Look")
text("""
This report explores how music consumption (hours per day, favorite genre, etc.) 
may relate to mental health indicators such as Anxiety, Depression, Insomnia, and OCD.
""")

text("## 1. Overview of Listening Habits")

fig_hours = px.histogram(
    df,
    x="Hours per day",
    nbins=20,
    title="Distribution of Daily Listening Hours"
)
plotly(fig_hours)

genre_counts = df["Fav genre"].value_counts(dropna=True).reset_index()
genre_counts.columns = ["Fav genre", "Count"]
fig_genre = px.bar(
    genre_counts,
    x="Fav genre",
    y="Count",
    title="Which Genres Are Most Popular?"
)
plotly(fig_genre)

text("""
I looked at how many hours participants listen to music each day 
and which music genres are most popular among them. The histogram shows that most participants listen to music 
between ~1–4 hours per day, with fewer people at very low (0 hours) or very high (6+ hours) listening times. 
People who report higher daily listening might use music for emotion regulation or as background while working 
(Chin & Rickard, 2012). average music listening times vary widely by age, culture, and personal habit. A Nielsen Music 360 
report found an average of around 32 hours per week in the U.S. (Nielsen, 2017). Another study showed college students 
often exceed 4 hours/day (North & Hargreaves, 2007).

The bar chart shows “Rock” as the single most popular genre among respondents, with “Pop,” “Hip hop,” and “Lo-fi” 
also quite high. I thought it was very interesting that "Rock" was the most popular considering "Pop" is so mainstream 
and is generally what is played on radios and in stores, so I looked a little deeper into why. One of the biggest potential 
reasons could be sample bias. If the participants were concentrated to be in a certain age-group or community, it would make
sense for "Rock" to be more popular. Alternatively, Rock’s passionate fan base usually consists of younger-to-midlife adults 
who identify strongly with guitar-driven music and lyrics, whereas “Pop” might be seen as mainstream but not necessarily 
a self-identity for some listeners (Miranda & Claes, 2009). Since we are looking into how music and mental health go hand in 
hand, it makes sense that the listeners prefer to identify with the lyrics and the music more than what's popular.
""")

# 2. Correlation Analysis: Listening Time & Mental Health (Heatmap)

text("## 2. Correlation Analysis: Listening Time & Mental Health (Heatmap)")

subset = df[["Hours per day"] + mental_health_columns]
correlations = subset.corr()

fig_corr = px.imshow(
    correlations,
    text_auto=True,
    title="Correlation Heatmap: Listening Time & Mental Health"
)
plotly(fig_corr)

text("""
This heatmap shows correlation coefficients between daily listening hours 
and various mental health indicators. Values closer to ±1 reflect stronger 
positive or negative relationships. Evidently, the time spent listening to music isn’t strongly correlated 
with a specific mental-health measure, though it can be slightly positive (e.g., higher anxiety might lead 
to more listening for coping). Anxiety, Depression, Insomnia, and OCD seem to correlate with each other better 
because mental health conditions often occur simultaneously (APA, 2013).
""")

# 3. Mental Health by Favorite Genre (Boxplot)

text("## 3. Mental Health by Favorite Genre")

fig_genre_box = px.box(
    df.dropna(subset=["Fav genre", "Anxiety"]),
    x="Fav genre",
    y="Anxiety",
    title="Anxiety Levels by Favorite Genre"
)
plotly(fig_genre_box)

text("""
We visualize Anxiety levels across different favorite genres. It shows that certain genres (e.g., Rock or Metal) 
might have higher median Anxiety scores, while others (e.g., Classical or Jazz) might appear lower. People with higher 
anxiety might be drawn to more intense or expressive genres as an emotional release or identity. This aligns with 
research that shows preference for heavier, more intense music to higher negative affect (Garrido & Schubert, 2011). Lighter 
genres (e.g., Jazz, Acoustic, Classical) can be associated with lower anxiety or more relaxed states (Koelsch, 2010), but it 
heavily depends on personal context and usage (e.g., using Rock for “venting” can also help some listeners).
""")

# 4. Listening Hours vs. Anxiety

text("## 4. Listening Hours vs. Anxiety")

fig_scatter = px.scatter(
    df,
    x="Hours per day",
    y="Anxiety",
    color="Fav genre",
    hover_data=["Depression", "Insomnia", "OCD"],
    title="Daily Listening Hours vs. Anxiety Levels"
)
plotly(fig_scatter)

text("""
This scatter plot shows each individual's daily music listening time (x-axis) 
and Anxiety score (y-axis), color-coded by their favorite genre. There does not seem to be a strong linear relationship 
between any of the variables. Some individuals with high Anxiety do listen many hours, but others do not. This is because
everyone has a different relationship with music. Some anxious individuals listen frequently to self-soothe 
(Miranda & Claes, 2009). Others might find excessive music listening overstimulating, or they might prefer silence during 
anxious times. So, there's no single “universal” correlation.
""")

# 5. Dropdown: Top 5 Genres by Each Mental Health Measure (Graph Objects)

text("## 5. Top 5 Genres by Anxiety, Depression, Insomnia, or OCD (Dropdown)")

melted = df.melt(
    id_vars=["Fav genre"],
    value_vars=mental_health_columns,
    var_name="MH_Condition",
    value_name="Score"
)

grouped = (
    melted.groupby(["MH_Condition", "Fav genre"], as_index=False)["Score"]
    .mean()
    .dropna(subset=["Score"])
)

top5_frames = []
for condition in mental_health_columns:
    cond_subset = grouped[grouped["MH_Condition"] == condition]
    top5 = cond_subset.nlargest(5, "Score")
    top5 = top5.sort_values("Score", ascending=True)
    top5_frames.append(top5)
top5_all = pd.concat(top5_frames, ignore_index=True)

import plotly.express as px
unique_genres = sorted(df["Fav genre"].dropna().unique())
colors = px.colors.qualitative.Plotly  
genre_color_map = {genre: colors[i % len(colors)] for i, genre in enumerate(unique_genres)}

import plotly.graph_objects as go
fig_dropdown = go.Figure()

for i, cond in enumerate(mental_health_columns):
    df_cond = top5_all[top5_all["MH_Condition"] == cond]
    
    bar_colors = [genre_color_map[genre] for genre in df_cond["Fav genre"]]
    
    fig_dropdown.add_trace(go.Bar(
        x=df_cond["Score"],
        y=df_cond["Fav genre"],
        orientation='h',
        name=cond,
        marker=dict(color=bar_colors),
        visible=True if i == 0 else False,
    ))

buttons = []
for i, cond in enumerate(mental_health_columns):
    mask = [False] * len(mental_health_columns)
    mask[i] = True
    buttons.append(dict(
        label=cond,
        method="update",
        args=[
            {"visible": mask},
            {"title": f"Top 5 Genres for {cond} (Mean Score)"} 
        ],
    ))

fig_dropdown.update_layout(
    title=f"Top 5 Genres for {mental_health_columns[0]} (Mean Score)",
    xaxis=dict(range=[0, grouped["Score"].max() if not grouped.empty else 1]),
    updatemenus=[dict(
        buttons=buttons,
        direction='down',
        showactive=True,
        x=1.3,
        y=1.0,
        xanchor='left',
        yanchor='top'
    )]
)

plotly(fig_dropdown)

text("""
This is a bar chart that shows the top 5 music genres filtered by mental health indicators. Depression, OCD, and Insomnia all
have "Lofi" as the top genre. Lo-Fi often features repetitive, chill beats with minimal vocal interruptions. People with 
OCD or Insomnia sometimes find steady, non-lyrical music “less distracting” or more soothing (Karthimannil & Faith, 2021). 
For people with Depression, it's probably reflective of their mental state where everything is slower to them which is why 
they prefer listening to Lo-Fi. 
""")

# 6. Conclusions

text("## 6. Conclusions & Insights")
text("""
Together, these results suggest that music preference is not only a marker of cultural and personal identity but also may reflect underlying emotional and cognitive processes. The variation in listening habits and genre preferences, along with the complex interplay between listening time and mental health, point toward a nuanced role of music in emotional regulation. These findings echo previous studies linking music to mood management and stress relief (Chin & Rickard, 2012; North & Hargreaves, 2007) and underscore the importance of considering both quantitative listening behaviors and qualitative genre choices when exploring the music-mental health nexus.

**References:**  
- American Psychiatric Association. (2013). *Diagnostic and Statistical Manual of Mental Disorders (5th ed.)*.  
- Chin, T., & Rickard, N. (2012). *The Music USE (MUSE) questionnaire: An instrument to measure engagement in music.* Music Perception, 29(4), 429-446.  
- Garrido, S., & Schubert, E. (2011). *Negative emotion in music: What is the attraction?* Empirical Musicology Review, 6(4), 214-230.  
- Karthimannil, V., & Faith, M. (2021). *The role of repetitive instrumental music in mitigating obsessive thoughts.* Journal of Music Therapy, 58(4), 427–445.  
- Miranda, D., & Claes, M. (2009). *Music listening, coping, peer affiliation and depression in adolescence.* Psychology of Music, 37(2), 215-233.  
- Nielsen (2017). *Music 360 Report.* Nielsen.  
- North, A. C., & Hargreaves, D. J. (2007). *Lifestyle correlates of musical preference: 2. Media, leisure time and music.* Psychology of Music, 35(2), 179–200.
""")