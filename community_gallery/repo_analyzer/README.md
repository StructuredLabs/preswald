# GitHub Repository Analyzer
A dashboard to visualize GitHub repository statistics, providing insights into contributor activity and commit patterns using Preswald's interactive components.

## Dataset Source
The data is dynamically fetched from the GitHub API:  
[GitHub REST API](https://docs.github.com/en/rest)  
While the default repository is set to StructuredLabs/preswald, this analyzer can be configured to work with **any public GitHub repository** by changing a single line of code.

## Features
- **Top Contributors Visualization**: Displays the most active contributors to a repository with an adjustable slider.
- **Contribution Distribution Statistics**: Shows what percentage of contributions come from top contributors.
- **Commit Activity Timeline**: Tracks repository activity over time with a monthly trend visualization.
- **Weekly Commit Analysis**: Provides detailed weekly commit counts in a tabular format.
- **Customizable Repository Selection**: Easily change which repository to analyze in the code.

## How to Run
1. **Clone or create a new Preswald project**
   ```bash
   preswald init repo_analyzer
   cd repo_analyzer
   ```

2. **Setup**
   - Install dependencies with `pip install preswald PyGithub pandas plotly toml`
   - Configure your data connections in `preswald.toml`
   - First run the data collection script: `python data.py`
   - Run your app locally with `preswald run`

3. **Deploy to Structured Cloud**
   - Create a `requirements.txt` file with the necessary dependencies
   - Get your API key from app.preswald.com
   - Deploy with:
     ```bash
     preswald deploy --target structured --github your-github-username --api-key your-structured-api-key hello.py
     ```

## Customization
To analyze a different repository, simply modify the `repo_name` variable in `data.py`:
```python
# Repository to analyze
repo_name = "username/repository"  # Change this to any GitHub repository
```

For example, to analyze TensorFlow: `repo_name = "tensorflow/tensorflow"`