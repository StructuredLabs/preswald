# Preswald Project

[Dataset](https://www.kaggle.com/datasets/atharvasoundankar/global-music-streaming-trends-and-listener-insights)

[App](https://music-331435-lpiu4gnh-ndjz2ws6la-ue.a.run.app/)

## About
This app explores global music statistics
1. **Top 5 Artists in each country**
    - Includes only users who listened to at least 30 minutes of music
2. **Top Genre by Age**
    - The distribution changes as youngeer users are removed using the slide
3. **Minutes Streamed vs Repeat Song Rate**
    - Explores the relationship between the amount of minutes streamed and repeat song rate, color coded by Subscription Type(free/premium)

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
