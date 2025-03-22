# Preswald Project

## Walmart Customer Purchases Behaviour Analysis
- Link to app - [Walmart Analytics](https://walmart-analytics-764213-jbvesltr.preswald.app)
    
### Dataset Source
The dataset used in this app is sourced from Walmart's customer purchase records. It includes information such as Customer ID, Age, Category, Product Name, Purchase Amount, Rating, and more.

### What the App Does
This app analyzes customer purchase behavior at Walmart. It provides insights into the purchasing patterns of customers older than 35, sorted by purchase amount. The app includes the following features:
- Displays a filtered dataset of customers older than 35, sorted by purchase amount.
- Provides a dynamic data view based on an age threshold slider.
- Creates a scatter plot showing the relationship between age and purchase amount for the top 50 customers.


### How to Run the App
1. Clone the repository:
```sh
git clone https://github.com/prakharnag/preswald-assessment.git
cd preswald-assessment/walmart_analytics
```

2. Create a virtual environment
- Follow this [Guide](https://docs.preswald.com/usage/troubleshooting#set-up-a-virtual-environment)
    

Install the preswald:
```sh
pip install preswald
```

3. Run the app:
```sh
preswald run 
```

### Deploy your app using the following command:
  
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    
    Replace `<your-github-username>` and `<structured-api-key>` with your credentials. (Note: your github username must be all lowercase)