# Preswald Project

# Music & Mental Health Insights

This project explores potential correlations between an individual’s music taste and their self-reported mental health. Using the MxMH dataset, the app analyzes listening habits, genre preferences, and mental health metrics (Anxiety, Depression, Insomnia, and OCD) to provide insights that could inform music therapy practices or simply reveal interesting patterns about the mind.

---

## Dataset Source

**MxMH Dataset – Music Therapy & Mental Health**

- **Context:**  
  Music therapy (MT) uses music to improve stress, mood, and overall mental health. As an evidence-based practice, MT harnesses music as a catalyst for the production of “happy” hormones such as oxytocin. However, music therapy can include a wide range of genres that vary by organization and personal taste.

- **Purpose:**  
  The MxMH dataset aims to identify correlations between an individual’s music taste and their self-reported mental health. The goal is to help inform more tailored music therapy interventions or provide insights into how music might influence mental well-being.

- **Interpreting the Data:**  
  - **Block 0: Background** – Respondents answer generic questions focused on musical background and listening habits.
  - **Block 1: Music Genres** – Respondents rank how frequently they listen to 16 different music genres (options: Never, Rarely, Sometimes, Very frequently).
  - **Block 2: Mental Health** – Respondents rate their levels of Anxiety, Depression, Insomnia, and OCD on a scale of 0 to 10 (0 means “I do not experience this” and 10 indicates “extreme or constant” experience).

- **Data Collection:**  
  Data was collected via a Google Form managed by [@catherinerasgaitis](https://twitter.com/catherinerasgaitis). The survey was distributed across various Reddit forums, Discord servers, social media platforms, and in public locations like libraries and parks. The brief format aimed to maximize response rates, with optional questions for more challenging topics.

---

## What the App Does

This app performs the following key functions:

1. **Overview of Listening Habits:**  
   - Displays a histogram of daily listening hours.
   - Shows the distribution of favorite music genres.

2. **Correlation Analysis:**  
   - Provides a heatmap that visualizes the correlation between daily listening hours and mental health metrics (Anxiety, Depression, Insomnia, OCD).

3. **Genre & Mental Health Relationship:**  
   - Uses boxplots to explore Anxiety levels by favorite genre.
   - Uses scatter plots to examine the relationship between listening hours and Anxiety.

4. **Top 5 Genres by Mental Health Measure:**  
   - Offers an interactive dropdown menu that allows users to view the top 5 music genres (by average score) for each mental health measure.
   - Each genre is assigned a unique color for consistency across the analysis.

The visualizations together tell a story about how music preferences and listening habits may relate to mental health, highlighting potential differences in genre popularity and the role music plays in emotional regulation.

---

## How to Run and Deploy the App

### Prerequisites

- **Python 3.x** installed on your machine.
- **Preswald** installed (ensure you have the correct environment with all dependencies).  
- The dataset (`mxmh_survey_results.csv`) and the configuration file (`preswald.toml`) should be in the project directory.

### Deploy the App

App is available here https://music-and-anxiety-835003-nf37b81f-ndjz2ws6la-ue.a.run.app