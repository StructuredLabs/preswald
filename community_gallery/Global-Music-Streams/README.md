
# User Streaming Behavior Dashboard

An interactive dashboard for visualizing global music streaming habits, user demographics, and engagement metrics.

![alt text](<Screen Recording 2025-03-16 at 5.05.22 PM.gif>)
## Dataset Source

The dashboard uses the **Global_Music_Streaming_Listener_Preferences** ()(https://www.kaggle.com/datasets/atharvasoundankar/global-music-streaming-trends-and-listener-insights/data)dataset. This dataset contains user-level information on streaming behavior including:
- **Country:** Geographical location of the user.
- **Streaming Platform:** Name of the music streaming service.
- **Subscription Type:** Type of subscription (e.g., free, premium).
- **Minutes Streamed Per Day:** Daily streaming duration.
- **Most Played Artist:** The most played artist by the user
- **Age:** Age of the user.
- **Number of Songs Liked:** Engagement metric.
- **Listening Time (Morning/Afternoon/Night):**	When the user listens the most
- **Discover Weekly Engagement (%):**	Percentage of auto-generated playlists played
- **Top Genre:** Most frequently listened genre.
- **Repeat Song Rate (%):** Percentage indicating how often users replay their favorite tracks.

*Note:* The dataset is sourced from kaggle, which provides curated global streaming metrics.

## What the App Does

This dashboard offers a comprehensive visual analysis of user streaming behavior by:
- **Interactive Visualizations:**  
  - **Treemap & Sunburst Charts:** Explore the hierarchical structure of countries, streaming platforms, and subscription types.
  - **Choropleth Map:** View average minutes streamed per day by country.
  - **Histograms & Bar Charts:** Analyze distributions of user ages and streaming durations.
  - **Pie Charts:** Understand the distribution of subscription types.
  - **Violin Plot:** Assess repeat song rates by top genre.
  - **Scatter Plot:** Examine relationships between minutes streamed and the number of songs liked.
  
- **Dynamic Data View:**  
  - An interactive slider allows users to filter the dataset based on an age threshold, dynamically updating the data table to focus on specific user segments.

## How to Run and Deploy

### Prerequisites
- **Python 3.7+**
- **Required Libraries:**
  - `preswald`
  - `plotly`
  - Other dependencies as listed in `requirements.txt`
- Ensure the dataset **Global_Music_Streaming_Listener_Preferences** is available to the app (either locally or via a connected data source).


### Running the App Locally

1. Clone the repository:
   
  `git clone https://github.com/StructuredLabs/preswald.git`

2. Go to this example:
   
  `cd community_gallery/Global-Music-Streams`
   
1. Start the app:
   
  `preswald run`

3. If not done automatically, open your browser and go to:
   
  `http://localhost:8501`


## Contact

For any questions or support, please reach out at https://darshannere.com, darshan.nere1@gmail.com or visit https://github.com/darshannere.
