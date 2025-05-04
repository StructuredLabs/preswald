# Shopping Trends Data Analysis

This project visualizes shopping trends based on several criteria, such as Gender, Purchase Amount, Subscription Status, etc. It helps analyze what payment method customers prefer, what is the most bough items, status of the client and possible discounts used.

## Dataset Source

The dataset is sources from [Kaggle's Customer Shopping Trends Dataset](https://www.kaggle.com/datasets/iamsouravbanerjee/customer-shopping-trends-dataset/). The features include customer age, gender, purchase amount, preferred payment methods, frequency of purchases, and feedback ratings, totaling 3900 customers in a dataset.

## Features

- **Interactive Scatter Plot**: Pie Chart of Payment Methods and Bar Chart of total amount of each item purchased.
- **Data Tables**: Displays dataset based on Subscription Status, Discount Applied, Promo Code Used. In addition raw dataset values shown.

## Setup

1. First, install Preswald using pip. https://pypi.org/project/preswald/

```bash
pip install preswald
```

2. Configure your data connections in `preswald.toml`

3. Add sensitive information (passwords, API keys) to `secrets.toml`

4. Run your app:

```bash
preswald run hello.py
```

5. To deploy, use:

```bash
preswald deploy
```
