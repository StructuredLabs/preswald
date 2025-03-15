# Preswald Project

## Setup

1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run`

## Getting Datasets

For this example, we're using a real estate dataset from Kaggle that contains property information from 7 major Indian cities. 
Here's the link: [Real Estate Data from 7 Indian Cities](https://www.kaggle.com/datasets/rakkesharv/real-estate-data-from-7-indian-cities)

**Dataset Source:** Real Estate Data from 7 Indian Cities

The dataset includes information about:

- Property prices
- Locations
- Property types (BHK)
- Total area
- Price per square foot
- Number of bathrooms
- Balcony availability

You can access the preprocessed dataset directly from our public S3 bucket:

```python
import pandas as pd
df = pd.read_csv("https://preswald.s3.us-east-1.amazonaws.com/real_estate.csv")
```

For other examples, you can find datasets from various sources such as:

- Kaggle
- Google Dataset Search
- UCI Machine Learning Repository
- AWS Open Data Registry