import pandas as pd
import requests
from bs4 import BeautifulSoup

url_base = 'https://www.procyclingstats.com/rankings.php'


def get_rider(rider_soup):
    tds = rider_soup.find_all('td')
    place = tds[0].text.strip()
    name = tds[4].text.strip()
    team = tds[5].text.strip()
    point = int(tds[6].text.strip())

    return {
        'place': place,
        'name': name,
        'team': team,
        'point': point,
    }


def get_riders(save=False):
    """
    Get riders name and link from the rankings page https://www.procyclingstats.com/rankings.php
    save: bool, if True, save the data to a CSV file
    """
    res = requests.get(url=url_base)
    soup = BeautifulSoup(res.text, 'html.parser')
    riders_soup = soup.tbody.find_all('tr')

    riders = []
    for ride_soup in riders_soup:
        info = get_rider(ride_soup)
        riders.append(info)

    if save:
        df = pd.DataFrame(riders)
        df.to_csv('data/riders.csv', index=False)
        print('saved to data/riders.csv')

    return riders


if __name__ == '__main__':
    riders = get_riders(save=True)
    print(riders)