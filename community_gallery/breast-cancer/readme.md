# Breast Cancer Data Analysis App

## Dataset source

This dataset is a CSV file containing population-based cancer statistics obtained from the NCI (National Cancer Institute) in 2017. It contains information such as cancer stages, progression and physical attributes.

## App Description

This app allows users to explore and analyze a breast cancer dataset, with filters for tumor size, estrogen status, and cancer grade. It provides key statistics, such as average tumor size and survival months, and visualizes the correlation between tumor size and survival through a scatter plot.

## How to run & deploy

1. Clone the repository
```console
git clone https://github.com/Pranav-Grandhi/preswald.git
```
2. [Install preswald](https://docs.preswald.com/quickstart)
```console
pip3 install preswald
```
3. run the app using the command:
```console
preswald run
```
4. deploy the app using the command:
```console
preswald deploy --target structured --github <github-username> --api-key <api-key> hello.py
```
5. once the app is deployed a live preview link will be generated in the cli. Use it to access the deployed instance
