# Price Comparison App

## Dataset Source

This dataset is from **Kaggle** and contains information about the prices of various mobile phones in different countries. The data is sourced from a sample CSV file, which includes columns like "Company Name", "Model Name", and "Launched Prices" for multiple countries: USA, India, China, and Dubai.

The prices are given in their respective currencies which I then converted to USD for plotting.

## What the App Does

This app compares the launched prices of mobile phones across different countries (USA, India, China, and Dubai).

1. **Threshold Filtering**: Comparison based on Prices of phones in USA vs all the other countries ( one by one ).
2. **Scatter Plots**: 3 Scatter plots based on the tables comparing Prices of Phones in USA vs other countries ( CHINA, INDIA, DUBAI ) 

## How to Run and Deploy
 ```bash
   pip install preswald
   pip install plotly
   pip install pandas

## Clone the repo
  preswald run

## Deployed Link
https://preswald-demo-476391-c7j9qdsl-ndjz2ws6la-ue.a.run.app/
 
