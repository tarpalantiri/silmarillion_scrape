__version__ = '1.0'
__author__ = 'Tehseen Sajjad'

import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

# URLS
HOST_URL = 'https://lotr.fandom.com'
CHARS_PAGE_SUFFIX = 'wiki/Category:The_Silmarillion_Characters'
CHARACTERS_PAGE = HOST_URL + '/' + CHARS_PAGE_SUFFIX

# FILENAMES/PLACEHOLDERS
CSV_FILENAME = 'character_races.csv'
PICKLE_FILENAME = 'character_races.pkl'


# Threaded GET
def makeSoups(url_list):
    session = FuturesSession(max_workers=10)
    session_list = [
        session.get(url) for url in url_list
    ]
    soups = list()
    for each_session in session_list:
        result = each_session.result()
        soups.append(BeautifulSoup(result.content, 'lxml'))
    return soups

def getNameAndRace(soup):
    name = soup.find('h1', {
        'class' : 'page-header__title'
        }).text
    sidebar = soup.find('aside', {
        'role' : 'region'
    })
    if sidebar:
        adjacent_h2 = soup.find('h2', text='Physical description')
        race = adjacent_h2.find_next('a').text
    else:
        race = 0
    return name, race



mainPage = None
try:
    mainPageResponse = requests.get(CHARACTERS_PAGE)
    mainPage = BeautifulSoup(mainPageResponse.content, 'lxml')
except Exception as e:
    print('[ERROR]')
    print(e)
    input('...')


characterLinksList = list()
for atag in mainPage.findAll('a', class_='category-page__member-link'):
    relative_link = atag['href']
    link = f"{HOST_URL}{relative_link}"
    characterLinksList.append(link)

characterPagesList = makeSoups(characterLinksList)

characterInfo = dict()

for characterPage in characterPagesList:
    name, race = getNameAndRace(characterPage)
    print(name, race)
    characterInfo[name] = race

dataFrame = pd.DataFrame(
    data={
        'Name' : list(characterInfo.keys()),
        "Race" : list(characterInfo.values())
    }
)

dataFrame.to_pickle(PICKLE_FILENAME)
dataFrame.to_csv(CSV_FILENAME)
