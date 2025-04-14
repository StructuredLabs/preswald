# Football Player Stats Visualization

This project aims to visualize various aspects of football player performance using the 2022/2023 football player stats dataset. It includes insightful visualizations like shooting accuracy vs. goal conversion rates, pass completion rates, and more. The visualizations are created using Plotly and showcase different types of plots, including scatter plots, bar charts, and heatmaps.

## Dataset

The dataset used in this project is from Kaggle and contains player statistics for the 2022/2023 football season. You can access and download the dataset from the following link:

[2022/2023 Football Player Stats Dataset](https://www.kaggle.com/datasets/vivovinco/20222023-football-player-stats)

### Dataset Features:

- **Goals**: Total goals scored by the player.
- **Assists**: Total assists made by the player.
- **Shots on Target (SoT%)**: Percentage of shots on target.
- **Goals per Shot (G/Sh)**: Conversion rate for shots on goal.
- **Pass Completion % (PasTotCmp%)**: Percentage of passes completed.
- **Progressive Passes (PasProg)**: Number of progressive passes made by the player.
- **Tackles (Tkl)**: Number of tackles made.
- **Interceptions (Int)**: Number of interceptions made.
- **Aerial Duels Won % (AerWon%)**: Percentage of aerial duels won.
- **Aerial Duels Won (AerWon)**: Total aerial duels won.

## How to Run the Project

To run the project, follow these steps:

1. **Install Dependencies**: Ensure you have Python 3.x installed. You will need to install the required Python packages. Run the following command to install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file contains the required libraries like `plotly`, `pandas`, `preswald`, etc.

2. **Run the Project**: Once the dependencies are installed, you can run the project using the `Presswald` command:

   ```bash
   presswald run
   ```

3. **Explore the Plots**: After executing the `presswald run` command, you can interact with the visualizations and explore the performance metrics of the players in different aspects like offensive and defensive abilities, shooting precision, and more.

## Visualizations

1. **Goals vs. Assists**: A scatter plot visualizing the total goals and assists of the top 10 players.
2. **Shooting Accuracy vs. Goal Conversion Rate**: A heatmap showing the relationship between shooting accuracy and goal conversion rates.
3. **Pass Completion % vs. Progressive Passes**: A scatter plot showing the correlation between pass completion rates and progressive passes.
4. **Tackles vs. Interceptions**: A scatter plot comparing the tackles made with interceptions, highlighting defensive performance.
5. **Aerial Duels Won % vs. Total Duels**: A scatter plot comparing aerial duels won percentage with total aerial duels won.

## Conclusion

This project offers a deeper understanding of player performance by visualizing critical football stats in various ways. It provides insights into the strengths and weaknesses of players in different areas of the game, such as goal-scoring, passing accuracy, defensive capabilities, and more.
