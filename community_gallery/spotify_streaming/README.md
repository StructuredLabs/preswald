# 🎵 Spotify 2023 Streaming Analysis 

## About This Project  
This interactive **Spotify 2023 Streaming Analysis App** provides insights into the most streamed artists, songs, and industry trends. The app allows users to filter data dynamically and explore trends across various aspects like song characteristics, playlist placements, seasonal patterns, and more.

## Live Demo & Resources

**Deployed App:** [Click here to visit](https://my-example-project-719255-kngkr5dp-ndjz2ws6la-ue.a.run.app)

**Demo Video:** [Watch the demo](https://drive.google.com/file/d/13TnESRwxw4Eew5h-zCw-aM1MxVO8Ncld/view?usp=sharing)

## Dataset  
The data used in this project comes from **Kaggle**:  
**[Most Streamed Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023/data)**  

## Features & Insights  
1. **Top 10 Artists by Total Streams**  
   - Bar chart visualization of the most streamed artists.  
   - **Dynamic insights** on how these artists dominate global streaming.  

2. **Top 10 Most Streamed Songs**  
   - A breakdown of the most streamed songs with an interactive bar chart.  
   - Insights on viral hits, anthems, and long-lasting chart-toppers.  

3. **How Does BPM Affect Streaming Popularity?**  
   - Scatter plot showing the relationship between song tempo (BPM) and streams.  
   - Insights into whether high-energy or moderate-tempo songs perform better.  

4. **Trends in Song Releases Over the Years**  
   - Line chart displaying yearly release trends.  
   - Insights on the rise of streaming and independent artists' contributions.  

5. **How Do Song Characteristics Relate to Popularity?**  
   - Scatter plots for **Energy vs. Streams** and **Danceability vs. Streams**.  
   - A box plot to analyze **Valence (Happiness) in top-streamed songs**.  
   - Insights into whether energetic, danceable, or happier songs perform best.  

6. **Do Playlist Placements Boost Song Streams?**  
   - **Grouped bar chart** comparing playlist placements on **Spotify, Apple Music, and Deezer**.  
   - **Scatter plot** to examine if playlist exposure correlates with streaming numbers.  

7. **What Are the Seasonal Trends in Song Releases?**  
   - **Bar chart** visualizing the number of songs released per month.  
   - **Line chart** showing the trend of streams by month.  
   - Insights on peak release periods and listening trends.  

8. **What Are the Key & Mode Distributions of Popular Songs?**  
   - **Bar chart** displaying the most common musical keys.  
   - **Pie chart** analyzing major vs. minor mode distribution in popular songs.  

## How to Run Locally  
### 1. Install Preswald  
Ensure you have **Preswald** installed. If not, install it using:  
```bash
pip install preswald
```

### 2. Run the App Locally  
Clone the repository and navigate to the project directory:  
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```
Start the app using:  
```bash
preswald run hello.py
```

---

## Deployment to Structured Cloud  
### 1. Get an API Key  
1. Go to **[Preswald Cloud](https://app.preswald.com)**.  
2. Create a **New Organization** (top left corner).  
3. Navigate to **Settings > API Keys**.  
4. **Generate and copy** your **Preswald API key**.  

### 2. Deploy to Structured Cloud  
Run the following command:  
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
Replace:  
- `<your-github-username>` with your **GitHub username**.  
- `<structured-api-key>` with your **Preswald API Key**.  

### 3. Verify the Deployment  
Once deployment is complete, a **live preview link** will be provided.  
Open the link in your browser to verify that your app is running smoothly.  

---

## Author & Contact  
**Author:** Sailesh Dwivedy  
**Email:** sailesh.dwivedy@colorado.edu  
**University:** University of Colorado Boulder  

If you have any questions, feel free to **reach out!** 😊