__version__ = '0.1'
__author__ = 'Tehseen Sajjad'

import requests
import pandas
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
# OLD, RACE ONLY
# def getBio(soup):
#     name = soup.find('h1', {
#         'class' : 'page-header__title'
#         }).text
#     sidebar = soup.find('aside', {
#         'role' : 'region'
#     })
#     if sidebar:
#         adjacent_h2 = soup.find('h2', text='Physical description')
#         race = adjacent_h2.find_next('a').text
#     else:
#         race = 0
#     return name, race

def getBios(soupsList):
    listOfBios: dict = list()
    for soup in soupsList:
        bioHash = dict()
        name = soup.find('h1', {
            'class' : 'page-header__title'
            }).text
        sidebar = soup.find('aside', {
            'role' : 'region'
        })
        bioHash['Name'] = name
        if sidebar:
            property_list = sidebar.findAll('h3')
            for prop in property_list:
                bioHash[prop.text] = prop.find_next('div').text
            listOfBios.append(bioHash)
        else:
            listOfBios.append(None)
    return listOfBios


if __name__ == '__main__':
    dfColumns = ['Name', 'Other names', 'Titles','Birth', 'Rule', 'Death', 'Realms',
    'Spouse', 'Children', 'Parentage', 'Siblings', 'Weapon', 'Race', 'Height',
    'Hair', 'Eyes', 'Culture', 'Actor', 'Voice']
    MAIN_DATAFRAME = pandas.DataFrame(columns=dfColumns)
    mainPage = None
    try:
        mainPageResponse = requests.get(CHARACTERS_PAGE)
        mainPage = BeautifulSoup(mainPageResponse.content, 'lxml')
    except Exception as e:
        print('[ERROR] Coudnt GET the main page')
        print(e.message)
        input('...')


    characterLinksList = list()
    for atag in mainPage.findAll('a', class_='category-page__member-link'):
        relative_link = atag['href']
        link = f"{HOST_URL}{relative_link}"
        characterLinksList.append(link)

    characterPagesList = makeSoups(characterLinksList)
    characterBiosList = getBios(characterPagesList)
    df = pandas.DataFrame([
        pandas.Series(eachBioDict) for eachBioDict in characterBiosList
    ])
    df.to_pickle('bios_dataframe.pkl')
    df.to_csv('silmarillion_scrape.csv')
