from preswald import connect, get_df, text, table, slider, plotly
import plotly.express as px
import pandas as pd

# Connect to data sources defined in preswald.toml
connect()

# Load data from preswald.toml connections
contributors_df = get_df("contributors")
commit_df = get_df("commit_activity")

# Convert date string to datetime if needed
if "date" in commit_df.columns:
    commit_df["date"] = pd.to_datetime(commit_df["date"])

# Create UI with centered title
text("# Preswald Repository Analyzer")

text("## Analysis of StructuredLabs/preswald repository")

# ---------- SECTION 1: Top Contributors ----------
text("### Top Contributors")

# Control for how many contributors to display
num_contributors = min(20, len(contributors_df))
top_n = slider("Number of top contributors to display", 
              min_val=5, max_val=num_contributors, 
              default=10)

# Sort and filter contributors
top_contributors = contributors_df.sort_values("contributions", ascending=False).head(top_n)

# Visualize top contributors
fig1 = px.bar(top_contributors, 
             x="username", y="contributions", 
             title=f"Top {top_n} Contributors by Number of Contributions")
plotly(fig1)

# Calculate contribution statistics
total_contributions = contributors_df["contributions"].sum()
top_n_contributions = top_contributors["contributions"].sum()
percent_by_top = (top_n_contributions / total_contributions) * 100 if total_contributions > 0 else 0

text(f"**The top {top_n} contributors account for {percent_by_top:.1f}% of all contributions.**")

# Show the data table
table(top_contributors, title="Top Contributors Data")

# ---------- SECTION 2: Repository Activity ----------
text("### Repository Activity Over Time")

# Process dates if not already done
if "month_year" not in commit_df.columns:
    commit_df["month_year"] = commit_df["date"].dt.strftime("%Y-%m")

# Group by month
monthly_commits = commit_df.groupby("month_year")["total"].sum().reset_index()

# Sort chronologically
monthly_commits = monthly_commits.sort_values("month_year")

# Visualize monthly activity
fig2 = px.line(monthly_commits, x="month_year", y="total",
             title="Commits By Month",
             labels={"month_year": "Month", "total": "Number of Commits"})
plotly(fig2)

# Show recent activity table
recent_activity = commit_df.sort_values("date", ascending=False).head(10)
recent_activity["week_starting"] = recent_activity["date"].dt.strftime("%Y-%m-%d")
recent_activity_display = recent_activity[["week_starting", "total"]]
recent_activity_display.columns = ["Week Starting", "Total Commits"]
table(recent_activity_display, title="Recent Weekly Activity")