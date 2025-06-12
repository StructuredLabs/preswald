# TikTok Influencer Analysis Dashboard 🚀

## Setup

1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

## Overview

**TikTok Influencer Analysis Dashboard** is an interactive data exploration tool built with [Preswald](https://github.com/StructuredLabs/preswald) and Plotly Express. This dashboard lets you filter and visualize key performance metrics—such as subscribers, views, likes, comments, and shares—of TikTok influencers. It’s designed to provide engaging insights and help you discover which influencers are truly rocking the platform.

## Dataset Source

The dataset is a curated CSV file containing data on TikTok influencers, sourced from social media analytics platforms. It includes the following columns:

- **Tiktoker name**
- **Tiktok name**
- **Subscribers** (formatted as "M" for millions and "K" for thousands)
- **Views avg**
- **Likes avg**
- **Comments avg**
- **Shares avg**

The data has been preprocessed to add numeric versions of key columns (e.g., `Subscribers_numeric`) for easier filtering and analysis.

## What the App Does

- **Dynamic Filtering:** Adjust multiple sliders (for subscribers, views, and comments) to filter influencers based on your chosen thresholds.
- **Interactive Tables:** View a filtered list of influencers that meet your criteria.
- **Rich Visualizations:** Explore relationships with engaging bar charts and scatter plots.
- **Engaging UI:** Enjoy descriptive text, emojis, and an intuitive interface that makes data exploration fun.
