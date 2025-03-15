# Electric Vehicle Data App:
  
## Data Source:
The data comes from the [Kaggle App](https://www.kaggle.com/datasets/yashdogra/ev-bhebic-c). 
It contains unsanitized data from the state of WA on local electric vehicles, their county, city, make, model, year, range and more.
While the data set has over 200K rows, I used a subset of just 9 rows for this POC.
  
## Usage:
- The spp filters the data for models that aren't Tesla's. Given the prevalence of Tesla's on the market and how fragmented the rest of the market is, I found this view interesting.
- The app filters for cars based on their range (in miles), giving you a unique view into which cars have longer lasting batteries. With the caveat that the data has discrepancies like one of the cars having a range of 0 miles.
- The app also gives you a look into which models by year, have the highest range. In future iterations, it would be good to better discern plug-ins vs battery EVs and further sanitizing the data.
  
## Running:
The production app is pending some trouble shooting with the team. Howeber, locally you may run the app by installing Preswald, then running 'preswald run' from you command line from within your directory.
Here's a quick [demo video](https://drive.google.com/file/d/1exwL1adEfWTMJRWUwMeqPWj2KeqjZf1I/view?usp=drive_link)
  
## Credits:
This project was created by Johann Zaroli. Github: Jzaroli
