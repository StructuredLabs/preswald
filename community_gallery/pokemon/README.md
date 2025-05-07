# Pokedex App

## The Dataset Source
This dataset contains records for all 1025 Pokémon. The information includes basic statistics such as height, weight, health points, attack, and defense as well as evolution groupings, which allows for analyzing aggregate statistics based on the distinct evolution families. Pokémon types and text descriptions are also provided. The data was curated from the PokéAPI website. The cleaning process performed on the descriptions removed certain special characters from the text. Unfortunately, those characters were sometimes located in the middle of words, and this resulted in some spacing typos.

## What the App Does
This app allows users to filter pokemons on their HP(Health Points) and visualise them in a dynamic chart. To filter them, we have a slider based in their HP, from 0 until 260, where we can put determined number and the app will show for us the pokemons that have hp above from that one determined. Once filtered, just the selected pokemons will display in the chart and in the table, where we can see more informations about the pokemons selected, as for example, height, weight, health points, attack, and defense as well as evolution groupings. 


## How to run the app
To run this example:
- Install preswald:
```bash
pip install preswald
```
- Clone this repo:
```bash
git clone https://github.com/StructuredLabs/preswald.git
```
- Move into the air-quality directory:
```bash
cd preswald/community_gallery/pokemon/
```
- Run the app:
```bash
preswald run
```
