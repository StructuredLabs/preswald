from preswald import text, plotly, connect, get_df, table, alert, slider, separator, image
from collections import Counter
# from sklearn.preprocessing import MultiLabelBinarizer  #doesn't work with structured cloud at the moment
import plotly.figure_factory as ff
import requests
import zipfile
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Define paths
url = "https://www.kaggle.com/api/v1/datasets/download/shivamb/netflix-shows"
zip_path = "./data/netflix-shows.zip"
extract_path = "./data/"
final_filename = "./data/netflix_titles.csv"

try:
    # Ensure the directory exists
    os.makedirs(extract_path, exist_ok=True)

    # Download the file
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        with open(zip_path, "wb") as file:
            file.write(response.content)
        print("Download complete:", zip_path)

        # Unzip the file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Find the extracted file and rename it
        extracted_files = os.listdir(extract_path)
        for file in extracted_files:
            if file.endswith(".csv"):
                old_path = os.path.join(extract_path, file)
                os.rename(old_path, final_filename)
                print(f"File renamed to: {final_filename}")
                break

        # Optionally, remove the zip file after extraction
        os.remove(zip_path)
        print("Cleanup complete.")
    else:
        print("Failed to download. Status code:", response.status_code)


    connect()  # Load all data sources (using sample_csv by default)

    df = get_df('netflix')



    text("# 🎬 Netflix Content Analysis: Exploratory Data Analysis")
    text("This analysis explores the Netflix movies and shows dataset to uncover trends and patterns in Netflix's content library. We'll examine content growth over time, geographic distribution, genre correlations, and audience targeting through ratings.")

    # Dataset Overview
    text("## 📊 Dataset Overview")
    text("Let's first examine the structure of our dataset to understand what information we're working with. The slider below allows you to control how many sample rows to display.")

    val = slider("Number of rows to display", min_val=1, max_val=5, step=1, size=0.2)
    separator()
    table(df.head(val), title="Netflix Dataset Sample")

    text("The dataset contains information about Netflix content including content type (Movie/TV Show), title information, director and cast details, country of origin, release date and date added to Netflix, content rating, duration, and genre categories.")

    text("Before diving deeper, let's check for data quality issues like missing values.")

    # Missing Values Analysis
    null_counts = df.isnull().sum()
    null_df = pd.DataFrame({'Column': null_counts.index, 'Null Count': null_counts.values})
    fig = px.bar(null_df, x='Column', y='Null Count', title='Missing Values by Column',
                    labels={'Null Count': 'Number of missing values', 'Column': 'Column'},
                    text_auto=True)

    plotly(fig)
    text("We've identified five columns with missing values. The director and cast information are frequently missing, which is common for aggregated content datasets. Country information is missing for about 20% of entries, which we'll need to consider when analyzing geographic distribution.")

    text("Let's also look at the cardinality of our categorical columns to understand the diversity in our dataset.")

    table(df.describe(include='all').loc[['unique', 'freq'],:], title="Column Cardinality: Unique Values and Frequencies")

    # Data Preparation
    df = df.fillna('NULL')
    df['year_added'] = df['date_added'].apply(lambda x: x.split(',')[-1])
    df['year_added'] = df['year_added'].apply(lambda x: x if x != 'NULL' else '2020')
    df['year_added'] = df['year_added'].apply(int)

    # Netflix Growth Analysis
    text("---")
    text("## 📈 Netflix Content Growth and Strategy")
    text("Netflix has transformed from a DVD rental service to the world's largest streaming platform. Let's examine how their content library has grown over time and how their strategy has evolved.")

    # Compute year data
    year_data = df['year_added'].value_counts().sort_index().loc[:2019]
    type_data = df.groupby('type')['year_added'].value_counts().sort_index().unstack().fillna(0).T.loc[:2019]

    # Prepare data for Plotly Express
    df_plot = pd.DataFrame({'Year': year_data.index, 'Total': year_data.values})
    df_type_movie = pd.DataFrame({'Year': type_data.index, 'Count': type_data['Movie'], 'Type': 'Movie'})
    df_type_tv = pd.DataFrame({'Year': type_data.index, 'Count': type_data['TV Show'], 'Type': 'TV Show'})
    df_combined = pd.concat([df_type_movie, df_type_tv])

    # Create line plot
    fig = px.line(df_combined, x='Year', y='Count', color='Type',
                    labels={'Count': 'Content Count', 'Year': 'Year'},
                    title="Netflix Content Growth Timeline",
                    line_shape='linear')

    # Add total count line
    fig.add_scatter(x=df_plot['Year'], y=df_plot['Total'], mode='lines', name='Total',
                    line=dict(color='white', width=5))

    # Annotate events with hover text
    t = [2008, 2010.8, 2012.1, 2013.1, 2015.7, 2016.1, 2016.9]
    events = ["Launch Streaming Video (2007.1)", "Expanding to Canada (2010.11)",
                "European Expansion (2012.1)", "First Original Content (2013.2)", "Japan Expansion (2015.9)",
                "Kids Content Strategy (2016/1)", "Offline Playback Feature (2016/11)"]

    annotations = []
    for t_i, event_i in zip(t, events):
        y_value = df_plot[df_plot['Year'] == int(t_i)]['Total'].values[0] if int(t_i) in df_plot['Year'].values else 0
        fig.add_scatter(x=[t_i], y=[y_value], mode='markers',
                        marker=dict(size=12, color='#E50914'),
                        hovertext=event_i, hoverinfo='text', name='Event')

    # Customize layout
    fig.update_layout(plot_bgcolor='rgba(102,102,102,1)',
                        xaxis=dict(range=[2006, 2020], tickfont=dict(size=20, color='white')),
                        yaxis=dict(range=[-40, 2700], tickfont=dict(size=20, color='white')),
                        legend=dict(font=dict(size=20, color='white')))

    plotly(fig)
    text("""This timeline reveals several key insights about Netflix's content strategy:
        - **Exponential Growth**: Content additions accelerated dramatically after 2015, showing Netflix's aggressive investment in its library.
        - **Strategic Shift**: Around 2016, we see a clear pivot in strategy - movie additions slowed while TV show acquisitions increased. This reflects Netflix's recognition that serialized content drives stronger viewer engagement and retention.
        - **International Expansion**: Major content spikes coincide with Netflix's international market entries, as they built regional libraries to attract local subscribers.
        - **Original Content Investment**: The 2013 launch of original programming (starting with \"House of Cards\") marked the beginning of Netflix's transformation from content aggregator to content creator.""")

    text("Let's now analyze which countries contribute most to Netflix's global content library.")

    # Geographic Content Analysis
    text("---")
    text("## 🌎 Geographic Content Distribution")
    text("Netflix operates in over 190 countries, offering a mix of international and local content. Let's examine which countries produce the most content available on Netflix globally.")

    country_data = df['country']
    country_counting = pd.Series(dict(Counter(','.join(country_data).replace(' ,',',').replace(', ',',').split(',')))).sort_values(ascending=False)
    country_counting.drop(['NULL'], axis=0, inplace=True)
    top20_country = country_counting[:20]

    # Bar Chart
    fig_bar = px.bar(
        top20_country.reset_index(), x="index", y=0,
        title="Top 20 Content-Producing Countries on Netflix",
        labels={"index": "Country", 0: "Number of Titles"},
        color=top20_country.values, color_continuous_scale="RdGy"
    )
    fig_bar.update_layout(
        xaxis_tickangle=-90,
        title_font=dict(size=15, family="Arial", color="black")
    )

    # Pie Chart
    fig_pie = px.pie(
        top20_country.reset_index(), names="index", values=0,
        title="Production Distribution Across Top 20 Countries",
        color_discrete_sequence=px.colors.diverging.RdGy
    )
    fig_pie.update_traces(pull=[0.06 if i == 0 else 0 for i in range(len(top20_country))])

    # Display both plots
    val2 = slider(
        "Adjust Chart Width",
        min_val=0,
        max_val=1,
        step=0.1,
        default=0.6,
    )
    plotly(fig_bar, size=val2)
    plotly(fig_pie, size=1.0 - val2)
    text("""The geographic distribution reveals several interesting patterns:
        - **U.S. Dominance**: American content represents approximately 40% of Netflix's library, reflecting both Hollywood's global influence and Netflix's origins as a U.S. company.
        - **Key International Markets**: India, the UK, Canada, France and Japan form the next tier of content producers, aligning with Netflix's strategic international expansion targets.
        - **Cultural Hubs**: Despite smaller populations, countries with strong film industries like South Korea and Spain have disproportionate representation.
        - **Notable Absences**: China is minimally represented, reflecting both regulatory barriers to Netflix's entry into the Chinese market and China's development of domestic streaming platforms.""")

    text("Let's visualize how content from different countries has been added to Netflix over time.")

    df['country'] = df['country'].dropna().apply(lambda x: x.replace(' ,',',').replace(', ',',').split(','))
    lst_col = 'country'
    df2 = pd.DataFrame({
            col: np.repeat(df[col].values, df[lst_col].str.len())
            for col in df.columns.drop(lst_col)}
        ).assign(**{lst_col:np.concatenate(df[lst_col].values)})[df.columns.tolist()]

    year_country2 = df2.groupby('year_added')['country'].value_counts().reset_index(name='counts')

    text("The map below shows the distribution of Netflix content by country of origin for a selected year. Use the slider to see how Netflix's international content acquisition has evolved over time.")

    year = slider(
        "Select Year",
        min_val=2008,
        max_val=2021,
        step=1,
        default=2008
    )

    # Filter data for selected year
    year_selected = year_country2[year_country2['year_added'] == year]

    # Create choropleth without animation
    fig = px.choropleth(year_selected,
                        locations="country",
                        color="counts",
                        locationmode='country names',
                        range_color=[0, 200],
                        color_continuous_scale=px.colors.sequential.OrRd)

    fig.update_layout(title=f"Netflix Content Additions by Country of Origin ({year})")
    plotly(fig)
    text("""This geographic visualization highlights Netflix's expanding global footprint:
        - **Early Years (2008-2012)**: Content was heavily concentrated in North America
        - **Mid-Period (2013-2016)**: Expanding to Europe and select Asian markets
        - **Recent Years (2017-2021)**: Truly global content acquisition with significant increases in regional production""")

    text("This visualization also reveals Netflix's \"local content\" strategy - investing in productions from countries where they operate to attract local subscribers while building a diverse international library.")

    text("Now let's examine how Netflix differentiates its Movies and TV Shows by genre.")

    # Genre Analysis
    text("---")
    text("## 🎭 Genre Analysis: Movies vs. TV Shows")
    text("Netflix's content strategy differs significantly between Movies and TV Shows. Let's analyze genre correlations to identify content patterns and audience targeting approaches.")

    movie = df[df['type'] == 'Movie']
    tv_show = df[df['type'] == 'TV Show']

    # The below lines don't work with structured cloud at the moment

    # def relation_heatmap(df, title):
    #     df['genre'] = df['listed_in'].apply(lambda x: x.replace(' ,', ',').replace(', ', ',').split(','))

    #     unique_genres = set(genre for sublist in df['genre'] for genre in sublist)
    #     print(f"There are {len(unique_genres)} types in the Netflix {title} Dataset")

    #     mlb = MultiLabelBinarizer()
    #     encoded_genres = pd.DataFrame(mlb.fit_transform(df['genre']), columns=mlb.classes_, index=df.index)

    #     correlation_matrix = encoded_genres.corr()
    #     mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

    #     # Extract the lower triangle of the correlation matrix
    #     masked_corr = correlation_matrix.where(~mask)

    #     # Convert to format suitable for Plotly heatmap
    #     heatmap_values = masked_corr.values.tolist()
    #     labels = list(correlation_matrix.columns)

    #     fig = ff.create_annotated_heatmap(z=heatmap_values,
    #                                         x=labels,
    #                                         y=labels,
    #                                         colorscale='RdBu',
    #                                         zmid=0,
    #                                         showscale=True,
    #                                         annotation_text=[['' for _ in labels] for _ in labels])

    #     fig.update_layout(title=f"Genre Correlation Heatmap - {title}",
    #                         xaxis=dict(title='Genres', scaleanchor="y"),
    #                         yaxis=dict(title='Genres'),
    #                         height=600,
    #                         width=800
    #     )

    #     plotly(fig, size=1.0)

    text("### Movie Genre Correlations")
    image("https://res.cloudinary.com/dqxarpcdg/image/upload/f_auto,q_auto/yhj6hkuhztx0yqq9l196","Movie Genre Correlations",0.7)
    text("""The movie genre correlation heatmap reveals several significant patterns:
        - **Strong Positive Correlations**: Independent Films strongly correlate with Dramas and International Movies. Documentaries show strong connections with International Movies. Action & Adventure films frequently overlap with Sci-Fi & Fantasy.
        - **Notable Negative Correlations**: Documentaries have a distinct negative correlation with Dramas. Children & Family movies tend not to overlap with more mature genres. Stand-up Comedy shows minimal overlap with most other genres.""")

    text("These patterns reflect Netflix's content acquisition strategy, where they maintain distinct movie categories to serve different audience segments.")

    text("### TV Show Genre Correlations")
    image("https://res.cloudinary.com/dqxarpcdg/image/upload/f_auto,q_auto/sfmjj6aehsgxtycqpacq","TV Show Genre Correlations",0.7)
    text("The TV Show genre correlations reveal different patterns compared to movies: - **Stronger Cross-Genre Integration**: Kids' TV shows show stronger correlation with International TV than other categories, suggesting Netflix's global kids' content strategy. Science & Nature shows strongly correlate with Docuseries, indicating educational content packaging. Crime TV Shows have positive correlations with Dramas and Thrillers. - **Content Strategy Insights**: TV content shows more deliberate genre mixing compared to movies. Reality TV stands relatively isolated, targeted at specific audience segments. International TV shows span across multiple genres, reflecting Netflix's localization efforts.")

    text("The distinct correlation patterns between movies and TV shows highlight Netflix's differentiated content strategy for each format.")

    # Audience Targeting Analysis
    text("---")
    text("## 👪 Audience Targeting: Content Rating Analysis")
    text("Netflix serves diverse audience segments from young children to mature adults. Let's analyze how their content library is distributed across different rating categories.")

    rating_order = ['G', 'TV-Y', 'TV-G', 'PG', 'TV-Y7', 'TV-Y7-FV', 'TV-PG', 'PG-13', 'TV-14', 'R', 'NC-17', 'TV-MA']

    movie_rating = movie['rating'].value_counts().reindex(rating_order, fill_value=0)
    tv_rating = tv_show['rating'].value_counts().reindex(rating_order, fill_value=0)

    def rating_barplot(data, title, height, h_lim=None):
        fig = go.Figure()

        # Bar chart
        fig.add_trace(go.Bar(
            x=data.index,
            y=data,
            marker=dict(color="#d0d0d0"),
            width=0.6,
            name="Ratings",
        ))

        # Annotation colors and ranges
        colors = ['green', 'blue', 'orange', 'red']
        span_range = [[0, 2], [3, 6], [7, 8], [9, 11]]
        labels = ['Little Kids', 'Older Kids', 'Teens', 'Mature']

        for idx, label in enumerate(labels):
            fig.add_annotation(
                x=sum(span_range[idx]) / 2,
                y=height,
                text=label,
                showarrow=False,
                font=dict(size=16, color='white', family="Arial Black"),
                bgcolor=colors[idx],
                opacity=0.6
            )
            fig.add_vrect(
                x0=span_range[idx][0] - 0.4,
                x1=span_range[idx][1] + 0.4,
                fillcolor=colors[idx],
                opacity=0.1,
                layer="below",
                line_width=0
            )

        fig.update_layout(
            title=f'{title} Rating Distribution',
            title_font=dict(size=20, family="Arial Black"),
            xaxis_title="Rating Category",
            yaxis_title="Number of Titles",
            yaxis=dict(range=[0, h_lim] if h_lim else None),
            bargap=0.2,
            template="plotly_white",
        )
        plotly(fig)

    text("### Movies Rating Distribution")
    rating_barplot(movie_rating, 'Movies', 1200)

    text("### TV Shows Rating Distribution")
    rating_barplot(tv_rating, 'TV Shows', 700, 800)

    rating_data = df[['rating', 'type']].groupby('type')['rating'].value_counts().unstack().fillna(0)[rating_order].T
    rating_data = pd.DataFrame(pd.concat([rating_data['Movie'], rating_data['TV Show']])).reset_index().rename(columns={'rating':'rating', 0:'cnt'})
    rating_data['type'] = rating_data.index//12
    rating_data['type'] = rating_data['type'].map({0: 'Movie', 1: 'TV Show'})

    # Generate Movie plot
    fig_movie = px.bar(
        rating_data[rating_data['type'] == 'Movie'],
        x='cnt',
        y='rating',
        color='type',
        orientation='h',
        color_discrete_map={'Movie': 'skyblue'},
        title='Movie Ratings Distribution'
    )

    fig_movie.update_layout(
        height=600,
        width=600,
        xaxis_title='Number of Titles',
        yaxis_title='',
        yaxis={'categoryorder': 'array', 'categoryarray': rating_order},
        showlegend=False
    )

    # Generate TV Show plot
    fig_tv = px.bar(
        rating_data[rating_data['type'] == 'TV Show'],
        x='cnt',
        y='rating',
        color='type',
        orientation='h',
        color_discrete_map={'TV Show': 'salmon'},
        title='TV Show Ratings Distribution'
    )

    fig_tv.update_layout(
        height=600,
        width=600,
        xaxis_title='Number of Titles',
        yaxis_title='',
        yaxis={'categoryorder': 'array', 'categoryarray': rating_order},
        showlegend=False
    )

    text("""The rating distributions above provide additional context on Netflix's audience targeting strategy:
        - **Movies**: Strong focus on mature content (R, TV-MA) reflecting Netflix's primary adult audience. Significant investment in teen-appropriate content (PG-13, TV-14). Limited but notable children's movie selection.
        - **TV Shows**: Heavily dominated by TV-MA and TV-14 content, targeting adults and teens. Stronger relative investment in children's content compared to movies. Clear separation between adult/teen content and children's programming.""")

    text("The side-by-side comparison helps visualize the different rating strategies between formats:")

    plotly(fig_movie, size=0.5)
    plotly(fig_tv, size=0.5)

    text("""These horizontal bar charts highlight the different rating distribution strategies:
        - **Movies** show a more balanced distribution across rating categories
        - **TV Shows** are heavily concentrated in the TV-MA and TV-14 categories""")

    text("This reflects Netflix's understanding that subscription retention depends on providing content for all family members, with TV shows being particularly important for targeting specific age groups. Finally, let's examine Netflix's content release patterns throughout the year.")

    # Seasonal Content Analysis
    text("## 📅 Content Release Patterns")
    text("Does Netflix follow seasonal patterns when adding new content? Let's analyze their content addition schedule by month and year.")

    netflix_date = df[['date_added']].dropna()
    netflix_date['year'] = netflix_date['date_added'].apply(lambda x: x.split(', ')[-1])
    netflix_date['month'] = netflix_date['date_added'].apply(lambda x: x.lstrip().split(' ')[0])

    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][::-1]
    df3 = netflix_date.groupby('year')['month'].value_counts().unstack().fillna(0)[month_order]
    df3 = df3.T.reset_index().melt(id_vars='month', var_name='year', value_name='count')

    # Remove NULL from x-axis
    df3 = df3[df3['year'] != 'NULL']

    # Create interactive heatmap
    fig = px.imshow(
        df3.pivot(index='month', columns='year', values='count'),
        color_continuous_scale='reds',
        labels={'color': 'Content Count'},
        aspect='equal'  # Make the heatmap square
    )
    fig.update_layout(
        title_text='Monthly Content Additions to Netflix (Heatmap)',
        xaxis_title='Year',
        yaxis_title='Month',
        xaxis=dict(side='top'),
        yaxis={'categoryorder': 'array', 'categoryarray': month_order}  # Sort months correctly
    )
    plotly(fig)

    text("""The monthly content addition heatmap reveals several interesting patterns:
        - **End-of-Quarter Spikes**: Netflix shows consistent patterns of higher content additions at the end of each quarter (March, June, September, December), likely aligning with business reporting cycles.
        - **Year-End Push**: December consistently shows strong content additions, capitalizing on holiday viewing periods when subscriber engagement typically increases.
        - **Growing Consistency**: In earlier years, content additions were more sporadic, but recent years show more consistent monthly additions, reflecting Netflix's maturation as a content platform.
        - **Volume Growth**: The increasing intensity of the red coloring over time illustrates Netflix's accelerating content investment, particularly from 2016 onward.""")

    text("This seasonal pattern analysis helps understand Netflix's content scheduling strategy and how it has evolved as the platform has grown.")

    text("---")
    text("## 🔍 Key Insights & Conclusions")

    text("""This exploratory analysis of Netflix's content library reveals several strategic patterns:
        - **Content Strategy Evolution**: Netflix has strategically shifted from primarily licensing movies to investing heavily in TV shows, particularly original series that drive subscriber retention.
        - **Global Expansion**: The geographic diversification of content reflects Netflix's international growth strategy, with increasing investment in regional production hubs.
        - **Targeted Audience Segmentation**: Different rating distributions between movies and TV shows demonstrate Netflix's sophisticated approach to serving distinct audience segments.
        - **Genre  Specialization**: The genre correlation analysis shows how Netflix constructs its content categories differently for movies versus TV shows.
        - **Strategic Content Calendar**: Content additions follow distinct seasonal patterns aligned with business reporting cycles and high-engagement viewing periods.""")


    text("Netflix's content strategy represents a data-driven approach to building a global entertainment platform, balancing mainstream appeal with niche content to maximize subscriber acquisition and retention across diverse markets and demographics.")

    text("---")
    text("### About this Analysis")
    text("""
    This Analysis provides comprehensive insights about Netflix's content strategy.
    Created with Preswald for Structured Labs Coding Assessment. ;)
    """)

except Exception as es:

    alert(message=f"# ⚠️ Error loading dataset: {es}", level="critical")
    if es == FileNotFoundError:
        text("Please ensure that you have set up the preswald.toml configuration file correctly")
