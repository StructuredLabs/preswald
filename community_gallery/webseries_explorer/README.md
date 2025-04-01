# 📺 Web Series Explorer 🎬✨


## About This Project  
This application provides an interactive way to explore IMDb's top web series, offering insights into ratings, popularity trends, and interesting statistics. Built with **Preswald**, it enables users to filter web series, analyze historical trends, and uncover fun facts about some of the most popular shows.

## Data Source  
The application utilizes the **IMDb Top Web Series Dataset**, which includes details about various shows such as:

- `Title`: Name of the web series
- `Ratings`: Average IMDb rating (out of 10)
- `Duration (in Min)`: Average runtime per episode
- `Votes`: Number of ratings received
- `Released_year`: Year the show premiered
- `Genre`: Genre classification
- `Summary`: Short description of the series

This dataset enables analysis of viewing trends, audience preferences, and patterns in ratings over the years.

## Key Functionalities  
🔹 **Filtering Web Series**:  
- Search by genre or the starting letter of a series title  
- Set filters for **ratings** and **release years**  

🔹 **Data Visualizations**:  
- **Yearly Releases**: A line graph showing how many web series premiered each year  
- **Ratings Over Time**: Trends in average IMDb ratings by year  
- **Runtime vs Ratings**: A scatter plot comparing episode duration with audience ratings  

🔹 **Fun Insights & Facts**:  
- Discover the **highest and lowest-rated series**  
- Identify the **longest and shortest episodes**  
- Find out which shows have received **the most and least votes**  
- Explore the **earliest and latest releases** in the dataset  

## Running the Application  

### Prerequisites  
Ensure Python is installed along with the required dependencies, including **Preswald**.  

### Setup Instructions  
```bash
git clone <repository-url>  
cd webseries_explorer  
```

```
pip install pandas plotly preswald
```

```
preswald run
```



### Deploying the App in Preswald

The app can be deployed in Preswald Structured Cloud using the following steps:

#### Get an API Key

-  Run the below command after getting your api key from app.preswald.com by creating your organization. 

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

#### Verify the Deployment

Once deployment is complete, a live preview link will be provided.
Open the link in your browser and verify that your app is running.

```
Starting production deployment... 🚀
i Custom domain assigned at webseries-explorer-777145-gvijykzt.preswald.app
i App is available here https://webseries-explorer-777145-gvijykzt-ndjz2ws6la-ue.a.run.app
i Custom domain assigned at webseries-explorer-777145-gvijykzt.preswald.app
```


Live URL - https://webseries-explorer-777145-gvijykzt.preswald.app/