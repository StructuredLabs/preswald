# NVIDIA Stock Volatility Dashboard

An interactive dashboard for analyzing NVIDIA stock price volatility and trends over time.

![NVIDIA Dashboard](images/logo.png)

## Dataset Source

The dashboard uses historical NVIDIA stock data from 2014 to 2024, stored in `data/NVIDIA_Stock_Volatility_2014_2024.csv`. This dataset includes:

- Daily closing prices
- High and low prices
- Trading volume
- Calculated metrics like daily returns and rolling volatility

The data was sourced from financial market APIs and processed to include volatility metrics for analysis.

## What This App Does

This interactive dashboard allows users to:

1. **Visualize NVIDIA Stock Price Trends**: Track NVIDIA's stock price movement over a 10-year period
2. **Analyze Volatility Patterns**: Examine 20-day rolling volatility to identify periods of market uncertainty
3. **Monitor Trading Volume**: View trading volume trends to understand market activity
4. **Filter by Date Range**: Use interactive sliders to focus on specific time periods
5. **View Summary Statistics**: Access key metrics like mean price, max/min prices, and average returns

The dashboard is built with Preswald, making complex financial data accessible through an intuitive interface.

## How to Run and Deploy

### Local Development

1. **Setup Environment**:
   ```
   # Install Preswald if you haven't already
   pip install preswald
   ```

2. **Configure Settings**:
   - Data connections are configured in `preswald.toml`
   - Sensitive information is stored in `secrets.toml`

3. **Run Locally**:
   ```
   preswald run hello.py
   ```
   This will launch the app on http://localhost:8501 by default.

### Deployment

The app is configured for deployment to Structured Cloud:

1. **Environment Setup**:
   - Ensure your GitHub username and API key are in `.env.structured`
   - Verify deployment settings in `preswald.toml`

2. **Deploy to Production**:
   ```
   preswald deploy --target structured --github johnniewhite --api-key="prswld-b0829f63-4872-4dc6-92da-421c110289b7" hello.py
   ```

3. **Access Deployed App**:
   - The app is available at: https://nvidia-stock-volatility-dk8z7myw-ndjz2ws6la-ue.a.run.app

## Project Structure

```
preswald_project/
├── data/
│   └── NVIDIA_Stock_Volatility_2014_2024.csv
├── images/
│   ├── logo.png
│   └── favicon.ico
├── .env.structured
├── .gitignore
├── hello.py
├── preswald.toml
├── README.md
└── secrets.toml
```

## Contributing

Contributions to improve the dashboard are welcome! Please feel free to submit a pull request or open an issue to discuss potential enhancements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.