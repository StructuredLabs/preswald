
from preswald import text, plotly, connect, table, selectbox, get_df
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.getcwd()))
from hotzone import HotZoneClassifier
from plotter import drawCourt

playerToCSV = {
    "Anthony Davis" : ["AD", "ADstats"],
    "LeBron James" : ["LBJ", "LBJstats"],
    "Shai Gilgeous-Alexander" : ["SGA", "SGAstats"],
    "Kevin Durant" : ["KD", "KDstats"],
    "Jayson Tatum" : ["JT", "JTstats"],
    "Stephen Curry" : ["SC", "SCstats"],
    "Luka Dončić" : ["LD", "LDstats"],
    "Joel Embiid" : ["JE", "JEstats"],
    "Nikola Jokić" : ["NJ", "NJstats"],
    "Giannis Antetokounmpo" : ["GA", "GAstats"],
}


def calculateZoneEfficiency(df: pd.DataFrame) -> dict:
    """
    This method to calculate hot zone efficiency assumes that df contains only the rows:
    ["SHOT_ZONE_AREA", "SHOT_ZONE_RANGE", "SHOT_MADE_FLAG"]

    Also assumes SHOT_ZONE_RANGE does not include "Back Court Shot" since we only care about shots within half court
    """
    hotzone = HotZoneClassifier()
    for _, row in df.iterrows():
        area, range, made = row
        hotzone.addShot(area, range, made)
    return hotzone.getPercentageAllZones()


text("# Welcome to Hot Zone Analyzer! 🏀🔥")
text("### Get ready to break down the game like never before! Hot Zone Analyzer gives you instant access to the shooting hot zones of ten of the best NBA players, helping you visualize where they dominate the court. Whether you're a fan, analyst, or hooper looking to sharpen your game, this app provides the data you need to see how the pros get buckets.")
text("### Explore shot charts, compare shooting percentages, and gain insights into the deadliest spots for each player. Ready to get started? Dive in and see who owns the floor! 🚀")
connect()
topTenPlayers = ["Anthony Davis", "LeBron James", "Shai Gilgeous-Alexander", "Kevin Durant", "Jayson Tatum", "Stephen Curry",  "Luka Dončić", "Joel Embiid", "Nikola Jokić", "Giannis Antetokounmpo"]
selectedPlayer = selectbox("Select a  Player", topTenPlayers, "Stephen Curry")



dfShooting= get_df(playerToCSV[selectedPlayer][0])

res = calculateZoneEfficiency(dfShooting[dfShooting["SHOT_ZONE_RANGE"] != "Back Court Shot"])



fig = drawCourt(res)

fig.update_layout(
    title=dict(
    text=f'<b><span style="font-family: Arial, Monospace; font-size: 20pt">Shooting Hot Zones for {selectedPlayer}</span>  </b>',
    x=0.5,
    y=0.95
    ),
)

plotly(fig) 

text(f'### Career Stats for {selectedPlayer}')
careerStats = get_df(playerToCSV[selectedPlayer][1])

table(careerStats)

