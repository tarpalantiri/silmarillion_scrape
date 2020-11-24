__version__ = '0.5'
__author__ = 'Tehseen Sajjad'

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Some helpers and constant variables
PARENT_H2_TEXT = 'Physical description'
MAIN_PAGE = 'https://lotr.fandom.com'
CHARS_PAGE_SUFFIX = 'wiki/Category:The_Silmarillion_Characters'
CHARS_LINK_TAG_CLASS = 'category-page__member-link'
RACE_PROPERTY_TEXT = 'Race'
RACE_PROPERTY_TAG = 'pi-data-label pi-secondary-font'
DATA_DUMP_FILENAME = 'Character_Races'
NO_SIDEBAR_ENTRY = 'No Sidebar'
TIME_FORMAT_STRING = '%a%d%b%Y%I%M'
UNICODE_CHECKMARK = '✅'
UNICODE_CROSS = '❎'

timestamp = datetime.now().strftime(TIME_FORMAT_STRING)
logfilename = f"{timestamp}.txt"


def log(type, msg):
    """
    prints and saves log message of shape:
    [type] - msg
    """
    logString = f"[{type}] - {msg}"
    print(logString)
    with open(logfilename, 'a') as logfile:
        logfile.write(logString + '\n')


def has_race_property(soupPage):
    """
    Checks if soupPage has the race property
    """
    hasRaceProperty = bool(soupPage.find('h3', class_=RACE_PROPERTY_TAG, text=RACE_PROPERTY_TEXT))
    return hasRaceProperty


def get_race_from_sidebar(soup):
    race = None
    adjacent_h2 = soup.find('h2', text=PARENT_H2_TEXT)
    race = adjacent_h2.find_next('a').text
    return race

if __name__ == '__main__':
    char_name_to_link_map = dict()
    character_tag_list = list()

    response = requests.get(f'{MAIN_PAGE}/{CHARS_PAGE_SUFFIX}')
    page = BeautifulSoup(response.content, 'lxml')

    # [a, a, a, a, a]
    character_tag_list = page.findAll('a', class_=CHARS_LINK_TAG_CLASS)
    for atag in character_tag_list:
        name = atag['title']
        relative_link = atag['href']
        link = f"{MAIN_PAGE}{relative_link}"
        char_name_to_link_map[name] = link
        
    # making a DataFrame

    names_list = list(char_name_to_link_map.keys())
    races_list = list()
    for name, link in char_name_to_link_map.items():
        res = requests.get(link)
        character_page = BeautifulSoup(res.content, 'lxml')
        if has_race_property(character_page):
            race = get_race_from_sidebar(character_page)
            log(UNICODE_CHECKMARK, f"{link}:\t{res.status_code} GOT RACE {race}")
        else:
            race = NO_SIDEBAR_ENTRY
            log(UNICODE_CROSS, f"{link} HAS NO SIDEBAR WITH RACE PROPERTY")
        races_list.append(race)


    data_dict = {
        'Name' : names_list,
        'Race' : races_list
    }
    df = pd.DataFrame(data=data_dict)
    log(UNICODE_CHECKMARK, 'DATA SAVED TO PANDAS DATAFRAME')
    # Save the dataframe object in a pickle
    df.to_pickle(DATA_DUMP_FILENAME+'.pkl')
    log(UNICODE_CHECKMARK, f'DATA PICKLED TO {DATA_DUMP_FILENAME}.pkl')
    # Save to a csv
    df.to_csv(DATA_DUMP_FILENAME+'.csv', index=False)
    log(UNICODE_CHECKMARK, f'DATA SAVED TO {DATA_DUMP_FILENAME}.csv')