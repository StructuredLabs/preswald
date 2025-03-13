# **🏏IPL Cricket Match Analytics Dashboard**

**🔗 Live App:** [Click Here](https://ipl-cricket-analysis-eziqbic7-ndjz2ws6la-ue.a.run.app/)

## **📌 Overview**
This **Cricket Match Analytics Dashboard** allows users to explore IPL match data through **interactive visualizations**. Users can:
- **Filter matches by season** using a dropdown selector.
- **Analyze winning margins** with a **Swarm Plot** (Runs vs Wickets).
- **Compare team win ratios** using a **Pie Chart**.
- **Identify top-performing players** with a **Horizontal Bar Chart**.
- **Discover the most successful venues** with a **Bar Chart**.

The dashboard is fully interactive and visually optimized for IPL insights.

---

## **📊 Dataset**
The dataset (`matches.csv`) contains:
- **Winner** – Match-winning team
- **Teams** – Competing teams
- **Win Margins** – Runs & wickets
- **Venue** – Match location
- **Player of the Match** – Best-performing player
- **Season** – IPL year

Dataset Source: IPL historical match data.

---

## **🚀 Features**
### **📅 1. Season Selection**
- Use a **dropdown selector** to filter matches for a specific IPL season.

### **🏏 2. Winning Margins Analysis**
- **Swarm Plot** for **Runs vs Wickets**, highlighting win strategies.

### **🏆 3. Team Win Ratio**
- **Pie Chart** for **win distribution across teams**.

### **🎖 4. Top Players (POTM Awards)**
- **Horizontal Bar Chart** ranking the **Top 10 players**.

### **🏟️ 5. Most Successful Venues**
- **Bar Chart** visualizing **top-performing venues**.

---

### Running the App

- **Clone the repository** or download the files.

- **Prepare the Dataset**: Make sure the `data.csv` file is in the correct directory. The data should be properly cleaned, with any missing values filled by the median where appropriate.

- **Run the App**:
  Once all dependencies are installed and your dataset is in place, you can run the app locally by using the following command in your terminal:
   ```bash
   preswald run
   ```

  This will start the app locally, and you can open it in your web browser at the provided local URL (e.g., `http://127.0.0.1:3000`).