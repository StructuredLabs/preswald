## The dataset source.
The 'Amazon Stocks 2025' dataset was obtained from [Kaggle](https://www.kaggle.com/datasets/meharshanali/amazon-stocks-2025). It contains stock data from 1977 - 2025 (Feb). Each dataset entry (by date) includes opening price, daily high, daily low, closing price, dividends (which is zero because AMZN doesn't pay dividends and never has), and stock splits. 

## What your app does.
My app provides users with visualization of AMZN's stock price, trading volume and historic stock splits. Users can set a minimum bound year for which they want to start viewing data from. For stock price, users can choose to view the opening price, daily high, daily low, and closing price over time with a line graph. Trading volume is shown with a bar graph, and stock splits with a scatter plot. Overall, the app gives visual insights about AMZN's stock performance and key metrics over time. Users can also view the entire dataset as a table.

Preswald has made it simple and easy to create such this app quickly. You can access the deployed app [here](https://anantjyot-project-387536-9rpfeput-ndjz2ws6la-ue.a.run.app).

## How to run and deploy it.
1. Clone the repository:
   ```bash
   git clone https://github.com/granganantjyot/preswald.git
   ```
2. Install dependencies:
    ```sh
    pip install preswald
    ```

3. Enter the project directory
    ```sh
    cd community_gallery/amzn-stock-2025
    ```

4. Run the app locally:
    ```sh
    preswald run
    ```

5. To deploy the app
    ```sh
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    ```
    Replace `<your-github-username>` and `<structured-api-key>` with your credentials obtained from app.preswald.com. Once deployment is complete, you will be provided a live preview link.