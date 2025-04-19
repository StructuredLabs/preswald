Hosted at https://m-chang-example-713771-gkcxwz8g-ndjz2ws6la-ue.a.run.app/

Uses Grocery-Inventory dataset from Kaggle
https://www.kaggle.com/datasets/willianoliveiragibin/grocery-inventory

Parses .csv file to display a bar graph of all items below a certain
number of items in stock.  Also displays a table of all items with 
less than 30 items that are not discontinued or backordered.

How to Run
1. Ensure path to dataset is configured in preswald.toml
2. Place dataset inside /data
3. Run locally using ```preswald run hello.py```.  App will run on port
specified in preswald.toml
4. Deploy using ```preswald deploy --target <environment> --github <your-github-username> --api-key <api-key> hello.py```
    - Replace environment with structured or other environment of choice
    - Replace your-github-username with your username in all lowercase
    - Get API key from https://app.preswald.com/ for Structured environments