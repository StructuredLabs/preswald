# 🏅 Olympic Medal Explorer

## 📌 Overview
The **Olympic Medal Explorer** is an interactive **Preswald app** that allows users to explore Olympic medal data in an engaging and dynamic way. Users can filter by country, compare medal performances, and even predict future medal counts based on historical trends.

## 🚀 Features
- **Country Analysis**: Select a country and view its Olympic medal history.
- **Medal Comparison**: Compare the performance of two countries side by side.
- **Medal Distribution**: Visualize gold, silver, and bronze medal counts using bar and pie charts.
- **2028 Medal Predictor**: Estimate a country's potential medal count for the **2028 Olympics**.
- **Olympic Trivia**: Enjoy fun facts about Olympic history.

## 📂 Folder Structure
```
Olympic_Medal_Explorer/
├── hello.py         # Preswald app script
├── data/
│   ├── olympics.csv # Dataset containing Olympic medal data
├── README.md        # Documentation (this file)
```

## 📊 How It Works
1. **Load the Dataset**
   - The app reads the Olympic medal dataset and extracts key statistics.
2. **Interactive Filtering**
   - Select a country and adjust the medal count threshold using sliders.
3. **Data Visualization**
   - Compare medal counts using bar and pie charts.
4. **Future Medal Prediction**
   - Predict a country's 2028 Olympic performance based on historical averages.
5. **Trivia Section**
   - Learn interesting Olympic facts!

## 🛠️ Deployment
### **1️⃣ Get a Preswald API Key**
- Go to [app.preswald.com](https://app.preswald.com)
- Navigate to **Settings > API Keys** and generate a key

### **2️⃣ Deploy to Structured Cloud**
Run this command:
```sh
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

### **3️⃣ Verify Your Deployment**
- Once deployed, open the provided live preview link.
- Ensure everything is working correctly.

## 🤝 Contribution
Want to improve this app? Fork the repository, make your changes, and submit a pull request!

## 📧 Contact
For any questions, reach out at **jobs@structuredlabs.com** or open a GitHub issue.

Enjoy exploring Olympic history! 🏆

