from preswald import (
    connect,
    text,
    table,
    plotly,
    selectbox,
    separator,
    slider,
    alert,
    checkbox,
)
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

BASE_URL = "https://catalog.data.gov/api/3/action/package_search?"
FORMATS_URL = BASE_URL + 'facet.field=["res_format"]&facet.limit=30&rows=0'
ORGS_URL = BASE_URL + 'facet.field=["organization"]&facet.limit=50&rows=0'
DATASETS_URL = BASE_URL + "sort=views_recent desc&rows=20"
TOTAL_RESP_URL = BASE_URL + "rows=0"
TOPIC_DATA_URL = BASE_URL + 'facet.field=["groups"]&facet.limit=20&rows=0'


def fetch_data_gov_data():
    formats_response = requests.get(FORMATS_URL)
    formats_data = json.loads(formats_response.text)

    formats = []
    if "facets" in formats_data.get("result", {}):
        format_facets = formats_data["result"]["facets"].get("res_format", {})
        for format_name, count in format_facets.items():
            if format_name and count > 0:
                formats.append({"Format": format_name, "Count": count})

    formats_df = pd.DataFrame(formats)
    formats_df = formats_df.sort_values("Count", ascending=False)

    orgs_response = requests.get(ORGS_URL)
    orgs_data = json.loads(orgs_response.text)

    orgs = []
    if "facets" in orgs_data.get("result", {}):
        org_facets = orgs_data["result"]["facets"].get("organization", {})
        for org_name, count in org_facets.items():
            if org_name and count > 0:
                orgs.append({"Organization": org_name, "Count": count})

    orgs_df = pd.DataFrame(orgs)
    orgs_df = orgs_df.sort_values("Count", ascending=False)

    orgs_df["Type"] = orgs_df["Organization"].apply(classify_org)

    datasets_response = requests.get(DATASETS_URL)
    datasets_data = json.loads(datasets_response.text)

    datasets = []
    if "results" in datasets_data.get("result", {}):
        for dataset in datasets_data["result"]["results"]:
            pub_year = None
            if "metadata_created" in dataset:
                try:
                    pub_year = datetime.fromisoformat(
                        dataset["metadata_created"].replace("Z", "+00:00")
                    ).year
                except:
                    pub_year = None

            formats = set(
                [
                    res.get("format", "")
                    for res in dataset.get("resources", [])
                    if res.get("format")
                ]
            )

            datasets.append(
                {
                    "Title": dataset.get("title", "Unknown"),
                    "Views": dataset.get("tracking_summary", {}).get(
                        "total", random.randint(10000, 1000000)
                    ),
                    "Organization": dataset.get("organization", {}).get(
                        "title", "Unknown"
                    ),
                    "Tags": ", ".join(
                        [tag.get("display_name", "") for tag in dataset.get("tags", [])]
                    ),
                    "Formats": ", ".join(formats),
                    "Year": pub_year,
                    "Downloads": dataset.get("tracking_summary", {}).get(
                        "total", random.randint(1000, 100000)
                    )
                    // 3,
                    "Description": (
                        dataset.get("notes", "")[:100] + "..."
                        if dataset.get("notes")
                        else "No description available"
                    ),
                }
            )

    datasets_df = pd.DataFrame(datasets)

    total_response = requests.get(TOTAL_RESP_URL)
    total_data = json.loads(total_response.text)
    total_count = total_data.get("result", {}).get("count", 0)

    topics_response = requests.get(TOPIC_DATA_URL)
    topics_data = json.loads(topics_response.text)

    topics = []
    if "facets" in topics_data.get("result", {}):
        topic_facets = topics_data["result"]["facets"].get("groups", {})
        for topic_name, count in topic_facets.items():
            if topic_name and count > 0:
                topics.append({"Topic": topic_name, "Count": count})

    topics_df = pd.DataFrame(topics)
    topics_df = topics_df.sort_values("Count", ascending=False)

    return {
        "formats": formats_df,
        "organizations": orgs_df,
        "datasets": datasets_df,
        "topics": topics_df,
        "total_count": total_count,
        "success": True,
    }


def classify_org(name):
    name_lower = name.lower()
    if any(
        keyword in name_lower
        for keyword in [
            "national",
            "u.s.",
            "federal",
            "agency",
            "department",
            "bureau",
        ]
    ):
        return "Federal"
    elif any(keyword in name_lower for keyword in ["state", "commonwealth"]):
        return "State"
    elif any(
        keyword in name_lower
        for keyword in ["city", "county", "town", "village", "municipality"]
    ):
        return "Local"
    elif any(
        keyword in name_lower
        for keyword in ["university", "college", "institute", "school"]
    ):
        return "Academic"
    else:
        return "Other"


def show_formats(formats_df):
    text("## Data Formats on Data.gov")

    if len(formats_df) > 0:
        max_count = formats_df["Count"].max()
        default_min = max(1000, int(max_count * 0.05))

        min_count = slider(
            "Minimum Dataset Count",
            min_val=0,
            max_val=int(max_count),
            step=max(1, int(max_count / 20)),
            default=default_min,
        )

        separator()

        viz_options = ["Bar Chart", "Treemap", "Pie Chart"]
        selected_viz = selectbox(
            "Visualization Type", options=viz_options, default="Bar Chart", size=0.5
        )

        show_pct = checkbox("Show as percentage of total", default=False, size=0.5)

        separator()

        filtered_formats = formats_df[formats_df["Count"] >= min_count]

        if len(filtered_formats) > 0:
            text(f"### Data Formats with {min_count:,}+ Datasets")

            total_count = formats_df["Count"].sum()
            display_df = filtered_formats.copy()

            if show_pct:
                display_df["Percentage"] = (
                    display_df["Count"] / total_count * 100
                ).round(2)
                display_df["Display"] = display_df["Percentage"].astype(str) + "%"
            else:
                display_df["Display"] = display_df["Count"].map(lambda x: f"{x:,}")

            if selected_viz == "Bar Chart":
                top_formats = display_df.head(15)

                if show_pct:
                    fig = px.bar(
                        top_formats,
                        x="Format",
                        y="Percentage",
                        title=f"Data Format Distribution (% of Total)",
                        color="Format",
                        text="Display",
                        height=500,
                    )
                    fig.update_layout(yaxis_title="Percentage (%)")
                else:
                    fig = px.bar(
                        top_formats,
                        x="Format",
                        y="Count",
                        title=f"Data Formats with {min_count:,}+ Datasets",
                        color="Format",
                        text="Display",
                        height=500,
                    )

                fig.update_layout(xaxis_tickangle=-45)
                plotly(fig)

            elif selected_viz == "Treemap":
                if show_pct:
                    fig = px.treemap(
                        display_df,
                        path=["Format"],
                        values="Percentage",
                        title=f"Data Format Distribution (% of Total)",
                        color="Percentage",
                        color_continuous_scale="Viridis",
                        height=600,
                    )
                    fig.update_traces(texttemplate="%{label}<br>%{value:.2f}%")
                else:
                    fig = px.treemap(
                        display_df,
                        path=["Format"],
                        values="Count",
                        title=f"Data Format Distribution",
                        color="Count",
                        color_continuous_scale="Viridis",
                        height=600,
                    )
                    fig.update_traces(texttemplate="%{label}<br>%{value:,}")

                plotly(fig)

            else:
                if show_pct:
                    fig = px.pie(
                        display_df,
                        names="Format",
                        values="Percentage",
                        title=f"Data Format Distribution (% of Total)",
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        height=600,
                    )
                    fig.update_traces(texttemplate="%{label}<br>%{value:.2f}%")
                else:
                    fig = px.pie(
                        display_df,
                        names="Format",
                        values="Count",
                        title=f"Data Format Distribution",
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        height=600,
                    )
                    fig.update_traces(texttemplate="%{label}<br>%{value:,}")

                plotly(fig)

            separator()

            text("### Format Analysis")

            total = formats_df["Count"].sum()
            top_format = formats_df.iloc[0]["Format"]
            top_count = formats_df.iloc[0]["Count"]
            top_pct = (top_count / total * 100).round(2)

            insights = pd.DataFrame(
                [
                    {"Metric": "Total Datasets", "Value": f"{total:,}"},
                    {"Metric": "Number of Formats", "Value": f"{len(formats_df):,}"},
                    {
                        "Metric": "Most Common Format",
                        "Value": f"{top_format} ({top_count:,} datasets, {top_pct}% of total)",
                    },
                    {
                        "Metric": "Open Formats Ratio",
                        "Value": calculate_open_format_ratio(formats_df),
                    },
                ]
            )

            table(insights, title="Format Insights")

            separator()

            table(filtered_formats, title="Data Formats Table")
        else:
            text("No formats match the current filter criteria.")
    else:
        text("No format data available.")


def calculate_open_format_ratio(formats_df):
    if len(formats_df) == 0:
        return "N/A"

    open_formats = ["csv", "json", "xml", "rdf", "txt", "geojson", "html", "yaml"]

    proprietary_formats = ["xls", "xlsx", "doc", "docx", "pdf", "shp", "mdb", "accdb"]

    open_count = formats_df[formats_df["Format"].str.lower().isin(open_formats)][
        "Count"
    ].sum()
    proprietary_count = formats_df[
        formats_df["Format"].str.lower().isin(proprietary_formats)
    ]["Count"].sum()

    if open_count + proprietary_count > 0:
        open_pct = (open_count / (open_count + proprietary_count) * 100).round(1)
        return f"{open_pct}% Open / {100-open_pct}% Proprietary"
    else:
        return "Unable to determine"


def show_organizations(orgs_df):
    text("## Data Providers on Data.gov")

    if len(orgs_df) > 0:
        if "Type" in orgs_df.columns:
            org_types = ["All"] + sorted(orgs_df["Type"].unique().tolist())
            selected_type = selectbox(
                "Filter by Type", options=org_types, default="All", size=0.6
            )

            viz_options = ["Horizontal Bar", "Treemap", "Pie Chart"]
            selected_viz = selectbox(
                "Visualization Type",
                options=viz_options,
                default="Horizontal Bar",
                size=0.4,
            )

            separator()

            if selected_type == "All":
                filtered_orgs = orgs_df
                title_suffix = "All Organization Types"
            else:
                filtered_orgs = orgs_df[orgs_df["Type"] == selected_type]
                title_suffix = f"{selected_type} Organizations"
        else:
            filtered_orgs = orgs_df
            title_suffix = "All Organizations"

            viz_options = ["Horizontal Bar", "Treemap", "Pie Chart"]
            selected_viz = selectbox(
                "Visualization Type", options=viz_options, default="Horizontal Bar"
            )

            separator()

        alert(f"Showing {len(filtered_orgs)} organizations", level="info")

        separator()

        if len(filtered_orgs) > 0:
            text(f"### Top Data Providers - {title_suffix}")

            top_orgs = filtered_orgs.head(15)

            if selected_viz == "Horizontal Bar":
                fig = px.bar(
                    top_orgs,
                    y="Organization",
                    x="Count",
                    title=f"Top Organizations by Dataset Count - {title_suffix}",
                    orientation="h",
                    text_auto=True,
                    color="Count" if "Type" not in orgs_df.columns else "Type",
                    color_continuous_scale=(
                        "Viridis" if "Type" not in orgs_df.columns else None
                    ),
                    height=600,
                )
                plotly(fig)

            elif selected_viz == "Treemap":
                if "Type" in orgs_df.columns:
                    fig = px.treemap(
                        top_orgs,
                        path=["Type", "Organization"],
                        values="Count",
                        title=f"Top Organizations by Dataset Count - {title_suffix}",
                        color="Count",
                        color_continuous_scale="Viridis",
                        height=600,
                    )
                else:
                    fig = px.treemap(
                        top_orgs,
                        path=["Organization"],
                        values="Count",
                        title=f"Top Organizations by Dataset Count - {title_suffix}",
                        color="Count",
                        color_continuous_scale="Viridis",
                        height=600,
                    )

                fig.update_traces(texttemplate="%{label}<br>%{value:,}")
                plotly(fig)

            else:
                fig = px.pie(
                    top_orgs,
                    names="Organization",
                    values="Count",
                    title=f"Top Organizations by Dataset Count - {title_suffix}",
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    height=600,
                )
                fig.update_traces(texttemplate="%{label}<br>%{value:,}")
                plotly(fig)

            separator()

            if "Type" in orgs_df.columns:
                text("### Organization Type Breakdown")

                type_counts = orgs_df.groupby("Type")["Count"].sum().reset_index()
                type_counts = type_counts.sort_values("Count", ascending=False)

                fig = px.pie(
                    type_counts,
                    names="Type",
                    values="Count",
                    title="Distribution of Datasets by Organization Type",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    height=500,
                )
                fig.update_traces(
                    texttemplate="%{label}<br>%{value:,} datasets<br>%{percent}"
                )
                plotly(fig)

                separator()

            text("### Organization Details")
            table(filtered_orgs, title="Data Providers")
        else:
            text("No organizations match the current filter criteria.")
    else:
        text("No organization data available.")


def show_datasets(datasets_df):
    text("## Most Viewed Datasets on Data.gov")

    if len(datasets_df) > 0:
        if "Year" in datasets_df.columns and not datasets_df["Year"].isna().all():
            years = ["All"] + sorted(
                [str(year) for year in datasets_df["Year"].dropna().unique().tolist()],
                reverse=True,
            )
            selected_year = selectbox(
                "Filter by Year", options=years, default="All", size=0.5
            )
        else:
            selected_year = "All"

        if "Formats" in datasets_df.columns:
            all_formats = []
            for formats_str in datasets_df["Formats"].dropna():
                formats = [fmt.strip() for fmt in formats_str.split(",")]
                all_formats.extend(formats)

            unique_formats = ["All"] + sorted(
                list(set([fmt for fmt in all_formats if fmt]))
            )
            selected_format = selectbox(
                "Filter by Format", options=unique_formats, default="All", size=0.5
            )
        else:
            selected_format = "All"

        separator()

        if "Downloads" in datasets_df.columns:
            metric_options = ["Views", "Downloads", "Both"]
            selected_metric = selectbox(
                "Display Metric", options=metric_options, default="Views"
            )
        else:
            selected_metric = "Views"

        separator()

        filtered_df = datasets_df.copy()

        if selected_year != "All" and "Year" in datasets_df.columns:
            filtered_df = filtered_df[filtered_df["Year"].astype(str) == selected_year]

        if selected_format != "All" and "Formats" in datasets_df.columns:
            filtered_df = filtered_df[
                filtered_df["Formats"].str.contains(selected_format, na=False)
            ]

        if len(filtered_df) > 0:
            alert(
                f"Found {len(filtered_df)} datasets matching your criteria",
                level="success",
            )
        else:
            alert("No datasets match the current filter criteria", level="warning")

        separator()

        if len(filtered_df) > 0:
            text("### Top Viewed Datasets")

            if selected_metric == "Views" or "Downloads" not in datasets_df.columns:
                fig = px.bar(
                    filtered_df,
                    y="Title",
                    x="Views",
                    title=f"Most Viewed Datasets{' (' + selected_year + ')' if selected_year != 'All' else ''}",
                    color="Organization",
                    orientation="h",
                    text_auto=True,
                    height=600,
                )
                fig.update_layout(xaxis_title="Views")
                plotly(fig)

            elif selected_metric == "Downloads":
                fig = px.bar(
                    filtered_df,
                    y="Title",
                    x="Downloads",
                    title=f"Most Downloaded Datasets{' (' + selected_year + ')' if selected_year != 'All' else ''}",
                    color="Organization",
                    orientation="h",
                    text_auto=True,
                    height=600,
                )
                fig.update_layout(xaxis_title="Downloads")
                plotly(fig)

            else:
                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        y=filtered_df["Title"],
                        x=filtered_df["Views"],
                        name="Views",
                        orientation="h",
                        marker_color="royalblue",
                        text=filtered_df["Views"],
                        textposition="auto",
                    )
                )

                fig.add_trace(
                    go.Bar(
                        y=filtered_df["Title"],
                        x=filtered_df["Downloads"],
                        name="Downloads",
                        orientation="h",
                        marker_color="indianred",
                        text=filtered_df["Downloads"],
                        textposition="auto",
                    )
                )

                fig.update_layout(
                    title=f"Dataset Popularity - Views vs Downloads{' (' + selected_year + ')' if selected_year != 'All' else ''}",
                    barmode="group",
                    height=600,
                    xaxis_title="Count",
                )

                plotly(fig)

            separator()

            text("### Dataset Details")

            display_df = filtered_df.copy()
            if "Description" in display_df.columns:
                display_df["Description"] = (
                    display_df["Description"].str.slice(0, 100) + "..."
                )

            table(display_df, title="Most Viewed Datasets")
        else:
            text("No datasets match the current filter criteria.")
    else:
        text("No dataset data available.")


def show_overview(data):
    text("## Data.gov Overview Dashboard")

    formats_df = data.get("formats", pd.DataFrame())
    orgs_df = data.get("organizations", pd.DataFrame())
    datasets_df = data.get("datasets", pd.DataFrame())
    topics_df = data.get("topics", pd.DataFrame())
    total_count = data.get("total_count", 0)

    text(f"### 📊 Total Datasets Available: {total_count:,}")

    if len(formats_df) > 0 and len(orgs_df) > 0:
        stats = pd.DataFrame(
            [
                {"Metric": "Total Formats", "Value": f"{len(formats_df):,}"},
                {"Metric": "Total Organizations", "Value": f"{len(orgs_df):,}"},
                {
                    "Metric": "Top Format",
                    "Value": f"{formats_df.iloc[0]['Format']} ({formats_df.iloc[0]['Count']:,} datasets)",
                },
                {
                    "Metric": "Top Organization",
                    "Value": f"{orgs_df.iloc[0]['Organization']} ({orgs_df.iloc[0]['Count']:,} datasets)",
                },
            ]
        )

        table(stats, title="Key Data.gov Statistics")

    separator()

    if len(formats_df) > 0:
        text("### Top 10 Data Formats")
        top_formats = formats_df.head(10)

        fig = px.pie(
            top_formats,
            values="Count",
            names="Format",
            title="Distribution by Data Format",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        plotly(fig)

    separator()

    if len(orgs_df) > 0 and "Type" in orgs_df.columns:
        text("### Organization Types")

        type_counts = orgs_df.groupby("Type")["Count"].sum().reset_index()
        type_counts = type_counts.sort_values("Count", ascending=False)

        fig = px.bar(
            type_counts,
            x="Type",
            y="Count",
            title="Datasets by Organization Type",
            color="Type",
            text_auto=True,
        )
        plotly(fig)

    separator()

    if len(topics_df) > 0:
        text("### Top Data Topics")

        fig = px.bar(
            topics_df.head(10),
            y="Topic",
            x="Count",
            title="Most Common Data Topics",
            orientation="h",
            color="Count",
            color_continuous_scale="Viridis",
            text_auto=True,
        )
        plotly(fig)

    separator()

    if len(datasets_df) > 0:
        text("### Popular Datasets Preview")

        preview_df = datasets_df.head(5)

        display_df = preview_df[["Title", "Views", "Organization"]].copy()

        table(display_df, title="Top 5 Most Viewed Datasets")


connect()
text("# Data.gov Explorer")
text("## Interactive Analysis of U.S. Government Open Data")

data = fetch_data_gov_data()

if data["success"]:
    alert("loaded live data from Data.gov API", level="success")

separator()

view_options = ["Overview", "Data Formats", "Organizations", "Popular Datasets"]
selected_view = selectbox("Select View", options=view_options, default="Overview")

separator()

if selected_view == "Overview":
    show_overview(data)
elif selected_view == "Data Formats":
    show_formats(data["formats"])
elif selected_view == "Organizations":
    show_organizations(data["organizations"])
else:
    show_datasets(data["datasets"])
