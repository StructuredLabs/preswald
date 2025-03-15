from preswald import connect, get_df, text, table, slider, plotly
import plotly.express as px
import pandas as pd

# Initialize connection to data sources
connect()

# Load the Netflix dataset
df = get_df("netflix_titles")

# Error handling if dataset fails to load
if df is None:
    text("# Error Loading Dataset")
    text(
        "Could not load 'netflix_titles_trimmed.csv'. Ensure it’s in 'data/' and configured in 'preswald.toml'."
    )
else:
    # Enhanced UI: Title and Introduction with Colorful Emphasis
    text("# 🎬 Netflix Content Explorer")
    text("### *Discover a Sample of Movies and TV Shows!*")
    text(f"*Exploring a sample of {len(df)} titles. Filter by type, year, or rating!*")

    # User Controls Section
    text("## 🔧 Filters")
    type_options = ["All", "Movie", "TV Show"]
    type_idx = slider(
        "Content Type (0=All, 1=Movie, 2=TV Show)", min_val=0, max_val=2, default=0
    )
    type_filter = type_options[type_idx]

    year_range = slider(
        "Minimum Release Year",
        min_val=int(df["release_year"].min()),
        max_val=int(df["release_year"].max()),
        default=int(df["release_year"].min()),
    )

    rating_options = ["All"] + sorted(df["rating"].dropna().unique().tolist())
    rating_idx = slider(
        f"Rating (0=All, "
        + ", ".join(
            f"{index+1}={rating}" for index, rating in enumerate(rating_options[1:])
        )
        + ")",
        min_val=0,
        max_val=len(rating_options) - 1,
        default=0,
    )
    rating_filter = rating_options[rating_idx]

    # Filter the dataset
    filtered_df = df
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df["type"] == type_filter]
    filtered_df = filtered_df[filtered_df["release_year"] >= year_range]
    if rating_filter != "All":
        filtered_df = filtered_df[filtered_df["rating"] == rating_filter]

    # Sort by release year (newest first)
    filtered_df = filtered_df.sort_values("release_year", ascending=False)

    # Display Results Section
    text(f"## 📋 Results: {len(filtered_df)} Titles")
    table(
        filtered_df[
            ["title", "type", "release_year", "rating", "listed_in", "description"]
        ],
        title="Netflix Titles (Sorted by Year)",
    )

    # Visualization Section
    text("## 📊 Insights")

    # Bar Chart: Content by Year and Type
    if not filtered_df.empty:
        fig1 = px.histogram(
            filtered_df,
            x="release_year",
            color="type",
            title="Content by Year",
            labels={"release_year": "Release Year", "type": "Content Type"},
            height=400,
            template="plotly",
            barmode="overlay",
            opacity=0.8,
            color_discrete_map={"Movie": "#FF5733", "TV Show": "#33FF57"},
        )
        fig1.update_layout(title_font_size=20, legend_title_text="Type")
        plotly(fig1)
    else:
        text("*No data available for Content by Year chart.*")

    # Pie Chart: Top Genres
    genres = filtered_df["listed_in"].str.split(", ").explode().value_counts().head(10)
    if not genres.empty:
        fig2 = px.pie(
            values=genres.values,
            names=genres.index,
            title="Top 10 Genres",
            height=400,
            template="plotly",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma,
        )
        fig2.update_traces(
            textinfo="percent+label", pull=[0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        )
        fig2.update_layout(title_font_size=20)
        plotly(fig2)
    else:
        text("*No genres available to display.*")

    # Bar Chart: Top Countries
    countries = filtered_df["country"].str.split(", ").explode().value_counts().head(10)
    if not countries.empty:
        fig3 = px.bar(
            x=countries.index,
            y=countries.values,
            title="Top 10 Countries",
            labels={"x": "Country", "y": "Titles"},
            height=400,
            template="plotly",
            color=countries.index,
            color_discrete_sequence=px.colors.sequential.Viridis,
            text_auto=True,
        )
        fig3.update_layout(title_font_size=20, showlegend=False)
        plotly(fig3)
    else:
        text("*No countries available to display.*")

    # Bar Chart: Rating Distribution
    rating_dist = filtered_df["rating"].value_counts()
    if not rating_dist.empty:
        fig4 = px.bar(
            x=rating_dist.index,
            y=rating_dist.values,
            title="Rating Distribution",
            labels={"x": "Rating", "y": "Count"},
            height=400,
            template="plotly",
            color=rating_dist.index,
            color_discrete_sequence=px.colors.sequential.Turbo,
            text_auto=True,
        )
        fig4.update_layout(title_font_size=20, showlegend=False)
        plotly(fig4)
    else:
        text("*No ratings available to display.*")

    # Timeline of Titles Added (if available)
    if "date_added" in filtered_df.columns:
        filtered_df["date_added"] = pd.to_datetime(
            filtered_df["date_added"], errors="coerce"
        )
        yearly_additions = filtered_df["date_added"].dt.year.value_counts().sort_index()
        if not yearly_additions.empty:
            fig5 = px.line(
                x=yearly_additions.index,
                y=yearly_additions.values,
                title="Titles Added Over Time",
                labels={"x": "Year Added", "y": "Titles"},
                height=400,
                template="plotly",
                line_shape="spline",
                markers=True,
                color_discrete_sequence=["#FFD700"],
            )
            fig5.update_layout(title_font_size=20)
            plotly(fig5)
        else:
            text("*No date added data available to display.*")

    # Enhanced Summary Stats with Trends
    text("### 🌟 Quick Stats & Trends")
    text(f"- **Total Titles**: {len(filtered_df)}")
    text(f"- **Movies**: {len(filtered_df[filtered_df['type'] == 'Movie'])}")
    text(f"- **TV Shows**: {len(filtered_df[filtered_df['type'] == 'TV Show'])}")
    text(
        f"- **Oldest Year**: {filtered_df['release_year'].min() if not filtered_df.empty else 'N/A'}"
    )
    text(
        f"- **Newest Year**: {filtered_df['release_year'].max() if not filtered_df.empty else 'N/A'}"
    )
    top_genre = genres.index[0] if not genres.empty else "N/A"
    text(f"- **Top Genre**: *{top_genre}*")
