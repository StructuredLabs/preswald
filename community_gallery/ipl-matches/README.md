
# IPL Analysis Project

## Overview

IPL Analysis is an interactive data analysis application built using **Preswald**, providing deep insights into Indian Premier League (IPL) matches. The app processes historical IPL data to uncover trends, top-performing teams, and toss analysis — all visualized with dynamic charts.

## Dataset

The dataset used in this project is the **IPL Matches Dataset**, stored as a CSV file (`matches`). The dataset contains important columns such as:

-  `date`: Match date
-  `team1`: First team
-  `team2`: Second team
-  `winner`: Winning team
-  `toss_winner`: Team that won the toss
-  `toss_decision`: Decision (bat/field) after the toss
-  `result`: Win type (runs/wickets)

This dataset powers multiple insights, including:

- Matches played over the years

- Most successful IPL teams

- Toss win impact on match outcomes

- Toss decisions breakdown (bat or field)

Dataset reference: [link](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)

## Features

The IPL Analysis app offers the following functionalities:

1. **Matches Per Year:**

- Line chart showing the total matches played per year.

- Insights highlighting peak seasons and league expansion.

2. **Most Successful Teams:**

- Bar chart showing the top-performing teams with a slider to control how many teams to display.

- Insights on which teams dominate the league and their winning strategies.

3. **Toss Win Impact:**

- Pie chart showing the percentage of times a toss-winning team wins the match.

- Insights exploring whether winning the toss leads to match victory.

4. **Toss Decision Breakdown:**

- Donut chart showing how often teams choose to bat or field after winning the toss.

- Insights explaining captains' strategic preferences. 

## How to Run the Application

### Prerequisites

Ensure you have Python and **Preswald** installed for running this interactive analysis.

### Installation Steps

1. Clone the repository:

```bash
git clone <repository-url>
cd ipl-analysis
```

2. Install dependencies:

```bash
pip install preswald
```  

3. Run the application:

```bash
preswald run
```

### Deploying the App in Preswald

The app can be deployed in **Preswald Structured Cloud** for sharing.

1. **Get an API Key:**

- Go to [app.preswald.com](https://app.preswald.com)

- Create a **New Organization**

- Navigate to **Settings > API Keys**

- Generate and copy your **Preswald API Key**

2. **Deploy the App:**

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

3. **Verify the Deployment:**

- Once deployment is complete, a **live preview link** will be provided.

- Open the link in your browser and ensure everything runs smoothly.

### Deploying the App in Preswald
Deployed application can be accessed [here](https://ipl-matches-452694-muijl6pm-ndjz2ws6la-ue.a.run.app/)

## Conclusion

IPL Analysis offers a dynamic and insightful breakdown of IPL performance data — from top teams to toss-winning strategies. With easy-to-read charts and interactive controls, it provides both cricket fans and data enthusiasts with a fun, data-driven way to explore IPL matches!