import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

# Headers needed otherwise site will not load properly
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    
def get_summonerid(url):
    r = requests.get(url,headers=headers)
    src = r.content
    soup = BeautifulSoup(src,'lxml')
    num = soup.find('button',{'class':re.compile('Button')})['onclick']
    return num.split("'")[1]

# Finds the raw html and returns False if the page contains no games left
def game_data(url):
    r = requests.get(url,headers=headers)
    try: 
        data = dict(r.json())
        return data['html']
    except:
        return False

# Searches for certain class names, creates a list of dictionaries for each game
def parse_data(data):
    soup = BeautifulSoup(data,'lxml')
    game_data = soup.find_all('div',{'class':'GameItemWrap'})
    games_list=[]
    for game in game_data:
        gametype = game.find('div',{'class':'GameType'}).text.strip()
        result = game.find('div',{'class':'GameResult'}).text.strip()
        
        try:
            mmr = game.find('div',{'class':'MMR'}).text.split('\n')[-2]
        except:
            mmr = 'N/A'
        
        champion = game.find('div',{'class':'ChampionName'}).text.strip()
        kill = int(game.find('span',{'class':'Kill'}).text)
        death = int(game.find('span',{'class':'Death'}).text)
        assist = int(game.find('span',{'class':'Assist'}).text)
        kda = game.find('span',{'class':'KDARatio'}).text
        kp = game.find('div',{'class':'CKRate tip'}).text.split('Kill')[1].strip()
        
        try:
            wards = game.find('span',{'class':'wards vision'}).text
        except:
            wards = 'N/A'
        
        game_length = game.find('div',{'class':'GameLength'}).text
        allchamp = [x.text for x in game.find_all('div',{'class':re.compile('Image16 __sprite __spc16')})]
        time = int(game.find('div',{'class':'GameItem'})['data-game-time'])
        date = datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
        game_dict ={
            'Game Type':gametype,
            'Result':result,
            'Tier Average':mmr,
            'Champion':champion,
            'Kill':kill,
            'Death':death,
            'Assist':assist,
            'KDA':kda,
            'Kill Participation':kp,
            'Control Wards':wards,
            'Game Length': game_length,
            'Ally Champions':allchamp[:5],
            'Enemy Champions':allchamp[5:10],
            'Time Unix':time,
            'Time':date}
        
        games_list.append(game_dict)
    return games_list

def output(url):
    username = ' '.join(url.split('=')[1].split('+')).strip()
    region = url.split('/')[2]
    print(f'Scraping games for {username}')
    summoner_id = get_summonerid(url)
    gameurl_0 = f'https://{region}/summoner/matches/ajax/averageAndList/summonerId={summoner_id}'

    data = (game_data(gameurl_0))
    games_list = parse_data(data)
    nextnum = (games_list[-1]['Time Unix'])
    gameurl_next = f'https://{region}/summoner/matches/ajax/averageAndList/startInfo={nextnum}&summonerId={summoner_id}'
    # Runs until the webpage has no more games left to find, (when function game_data returns False)
    while game_data(gameurl_next) != False:
        data = (game_data(gameurl_next))
        games_list.extend(parse_data(data))
        nextnum = (games_list[-1]['Time Unix'])
        print(f'Scraped {len(games_list)} games')
        gameurl_next = f'https://{region}/summoner/matches/ajax/averageAndList/startInfo={nextnum}&summonerId={summoner_id}'
    
    df = pd.DataFrame(games_list)
    del df['Time Unix']
    df.to_csv(f'{username} games.csv',index=False)

    print('Done')
    
file = open('links.txt', 'r') 

for link in file.readlines():
    output(link)

