# op.gg-game-scraper
Scrapes data of all recent games on op.gg and outputs into a csv file <br>
Works with any server region

# Steps:
- Open `links.txt` and add each op.gg link on a **new line** 
- Open command prompt in the directory you have saved `opggscrape.py` and run `pyhon opggscrape.py`
- This may take long if the account has many games

# Additional Information:
Due to the way these games are stored, this code runs in steps of 20 games, at each step a new webpage containing the data of 20 games is opened which is the slowest step of the code

## Libraries
- Requests
- BeautifulSoup
- Pandas
- Datetime
- Regex
