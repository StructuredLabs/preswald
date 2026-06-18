# Pull Request Description: Startup Growth & Investment Insights

### Summary

This PR introduces an interactive application to explore and analyze startup funding, valuation, and growth trends using Preswald. It allows users to dynamically filter startups based on investment amounts and visualize the relationship between funding rounds and startup valuation.

### Key Features Implemented

1. **Dynamic Filtering**:

   - Users can adjust a slider to filter startups by minimum investment amount.
   - Displays a table of filtered startups with investment amounts above the selected threshold.

2. **Data Visualization**:

   - A scatter plot that visualizes:
     - The number of funding rounds vs. startup valuation.
   - Hovering over the plot provides additional details such as the startup’s country, number of investors, and year founded.

3. **User Interaction**:
   - A slider that dynamically updates the displayed data and chart based on the selected investment threshold.

### Technical Implementation

- Utilized **Pandas** for data processing and filtering.
- Used **Plotly Express** for interactive scatter plot visualizations.
- Integrated **Preswald** components (text, table, plotly, slider) for user interaction and data display.

### How to Run

1. Install dependencies:

   ```bash
   pip install pandas plotly preswald
   ```

2. Run app:

```bash
   python hello.py
```

3. Deployment on Preswald Cloud:

```bash
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
