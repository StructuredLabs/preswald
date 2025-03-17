# Twitch Analytics Dashboard

Link to deployed app: https://twitch-data-790012-kcxajly1-ndjz2ws6la-ue.a.run.app/

## Dataset

This project utilizes **Twitch streamers' data** as taken from https://www.kaggle.com/datasets/aayushmishra1512/twitchdata and read as a CSV file, including:

- **Watch time (Minutes)**
- **Followers and Followers Gained**
- **Partnered Status**
- **Mature Content Status**
- **Language of the Stream**
- **Average Viewers per Stream**

## Overview

This interactive **Twitch Analytics Dashboard** provides insights into the **top streamers, audience distribution, and engagement metrics** on Twitch. Users can filter streamers based on language, partnership status, and mature content settings.

## Features

- **Top Streamers by Watch Time** (Visualized as a bar graph)
- **Top Streamers by Average Viewers** (Visualized as a bar graph)
- **Twitch Audience Language Distribution** (Visualized as a pie chart)
- **Customizable Filters for Streamer Analysis**
  - Filter by **Language**
  - Filter by **Partnered Status (Yes/No)**
  - Filter by **Mature Content (Yes/No)**

## How to Run

1. **Set Up Your Environment**
   ```bash
   # Install Preswald if not installed
   pip install preswald
   ```
2. **Initialize and Run the Project**
   ```bash
   preswald run
   ```

## Deployment
The application is live and can be accessed here: https://twitch-data-790012-kcxajly1-ndjz2ws6la-ue.a.run.app/

To deploy the application to **Structured Cloud**, use:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key>
```

