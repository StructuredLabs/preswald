# Job Trends Analyzer !!
App can be found [here](https://job-analyzer-876595-6ipoejk0-ndjz2ws6la-ue.a.run.app)

## Overview
This tool enables users to explore and analyze job statistics across various companies for the year 2023. It provides valuable insights into hiring trends, in-demand roles, and recruitment patterns. 

## Dataset
As a proof of concept, only data from the first 15 days of 2023 has been loaded due to memory constraints. Incorporation of larger datasets will be done in the future to faciliate more comprehensive analysis. The dataset used is borrowed from Kaggle's [Job Search](https://www.kaggle.com/datasets/ravindrasinghrana/job-description-dataset) dataset and consists of around 23 fields of which only 7 fields were used. 
- Country
- Salary Range
- Work Type
- Company Size
- Job Title
- Company name
- Job Posting Date

## Navigation
To navigate the app, consider using the filters effectively
- **Salary Filters**: Apply filters based on the minimum and maximum salaries to refine job searches.
- **Job Type Filters**: Filter roles based on whether they are full-time or part-time positions.
- **Company-Specific Filters**: Select specific companies to visualize hiring trends more effectively.
- **Visualizations**: Utilize pie charts and histograms to analyze hiring distributions and trends across companies.

## Local Setup
To run this app locally, 
- Build a conda environment `conda create -n preswald python=3.11`
- Install *preswald* using `pip install preswald` 
- Clone the repo `git clone https://github.com/StructuredLabs/preswald.git`
- `cd preswald/community_gallery/job-analyzer/`
- `preswald run`
