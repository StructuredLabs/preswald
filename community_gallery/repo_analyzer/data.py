import os
import pandas as pd
import toml
from github import Github

def fetch_github_data():
    """
    Fetch GitHub repository data and save to CSV files.
    Also updates the preswald.toml configuration.
    """
    os.makedirs("data", exist_ok=True)
    print("Fetching GitHub repository data...")
    
    # Initialize GitHub API
    g = Github()
    
    # Repository to analyze
    repo_name = "StructuredLabs/preswald"
    repo = g.get_repo(repo_name)
    
    print(f"Fetching data for {repo_name}...")
    
    # Fetch contributors data
    contributors = repo.get_contributors()
    contributors_data = []
    for contributor in contributors:
        contributors_data.append({
            "username": contributor.login,
            "contributions": contributor.contributions,
            "url": contributor.html_url
        })
    
    contributors_df = pd.DataFrame(contributors_data)
    contributors_df.to_csv("data/contributors.csv", index=False)
    print(f"Saved {len(contributors_data)} contributors to data/contributors.csv")
    
    # Fetch commit activity data
    commit_activity = repo.get_stats_commit_activity()
    commit_data = []
    commit_df = None
    
    if commit_activity:  # Sometimes this returns None if not cached
        for week in commit_activity:
            commit_data.append({
                "week": week.week,  # Unix timestamp
                "total": week.total
            })
        
        commit_df = pd.DataFrame(commit_data)
        # Convert Unix timestamp to datetime
        commit_df["date"] = pd.to_datetime(commit_df["week"], unit='s')
        commit_df.to_csv("data/commit_activity.csv", index=False)
        print(f"Saved {len(commit_data)} weeks of commit activity to data/commit_activity.csv")
    
    # Update preswald.toml to include our data sources while preserving other settings
    if os.path.exists("preswald.toml"):
        # Load existing config
        config = toml.load("preswald.toml")
        
        # Update project title and branding
        config["project"]["title"] = "GitHub Repository Analyzer"
        config["branding"]["name"] = "GitHub Repository Analyzer"
        
        # Update data sources
        if "data" not in config:
            config["data"] = {}
            
        config["data"]["contributors"] = {
            "type": "csv",
            "path": "data/contributors.csv"
        }
        
        config["data"]["commit_activity"] = {
            "type": "csv",
            "path": "data/commit_activity.csv"
        }
        
        # Write updated config back
        with open("preswald.toml", "w") as f:
            toml.dump(config, f)
            print("Updated preswald.toml with GitHub data sources")
    else:
        # Create a new config file if it doesn't exist
        with open("preswald.toml", "w") as f:
            f.write('''
[project]
title = "GitHub Repository Analyzer"
version = "0.1.0"
port = 8501
slug = "repo-analyzer-761317"  # Required: Unique identifier for your project
entrypoint = "hello.py"    # Required: Main script to run when executing preswald run

[branding]
name = "GitHub Repository Analyzer"
logo = "images/logo.png"
favicon = "images/favicon.ico"
primaryColor = "#24292e"

[data.contributors]
type = "csv"
path = "data/contributors.csv"

[data.commit_activity]
type = "csv"
path = "data/commit_activity.csv"

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
''')
            print("Created new preswald.toml configuration file")
    
    return contributors_df, commit_df

if __name__ == "__main__":
    # If this script is run directly, fetch the data
    fetch_github_data()
    print("Data collection complete. You can now run your Preswald app with 'preswald run'.")