# Pokemon Dashboard

This project uses a pokedex dataset retrieved from Kaggle, with relevant data on the pokedex ID, the pokemon's name, height, weight, type(s), evolutionary line, pokedex description, and base stats.

I had to do some data engineering for two type columns that I could get distributions for and plot based on.

I also sample random pokedex entries from the dataset and display an image from PokeAPI. I used Plotly's imaging as opposed to Preswald's because the Preswald image wasn't working.

To run and deploy this app:
Download Preswald ('pip install preswald'), traverse to the community_gallery/pokemon directory, and run 'preswald run'. To deploy, I used preswald deploy --target structured --github <my-github-username> --api-key <my-structured-api-key> hello.py

Thanks to Kaggle and the Structured Labs team for hosting this community gallery!


- Amruth