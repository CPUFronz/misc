# 0 * * * * bash -c 'DISPLAY=:0.0 && export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus && source /home/franz/workspace/zzz_miniconda3/bin/activate && cd /home/franz/workspace/misc/flat_checker && python /home/franz/workspace/misc/flat_checker/flat_checker.py'

import time
import os
import base64
import re
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
#from seleniumrequests import Firefox
#from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import Select

JSON_STORE = 'flats.json'
WILLHABEN_URL = 'https://www.willhaben.at/iad/immobilien/mietwohnungen/mietwohnung-angebote'
WILLHABEN_PARAMETERS = {
    'userAction': None,
    'location': 900,
    'areaId': 900,
    'PRICE_FROM': None,
    'PRICE_TO': 700,
    'ESTATE_SIZE/LIVING_AREA_FROM': None,
    'ESTATE_SIZE/LIVING_AREA_TO': None,
    'NO_OF_ROOMS_BUCKET': None,
    'PROPERTY_TYPE': 110,
    'PROPERTY_TYPE': 111,
    'PROPERTY_TYPE': 113,
    'PROPERTY_TYPE': 102,
    'PROPERTY_TYPE': 3,
    'PROPERTY_TYPE': None,
    'ESTATE_PREFERENCE': 28,
    'ESTATE_PREFERENCE': None,
    'FREE_AREA/FREE_AREA_TYPE': None,
    'AVAILABLETODAY': None,
    'keyword': 'provisionsfrei',
    'periode': 2,
    'periode': None,
    'MMO_COUNT': None,
    'sort': 1,
    'rows': 30,
    'advanced_search_button': None
}

def query_willhaben():
    results = {}

    r = requests.post(WILLHABEN_URL, data=WILLHABEN_PARAMETERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    flats = soup.find_all('section', {'class': 'content-section isRealestate'}) 

    for flat in flats:
        link = flat.find('a')
        url =  WILLHABEN_URL[:24] + link.attrs['href']
        tagline = link.text.strip()

        address = flat.find('div', {'class':'addressLine'}).text.strip().replace('\n', '').split('Wien, ')[1]
        info = flat.find('div', {'class': 'info'})
        mini_desc = info.find('span', {'class': 'desc-left'}).text.strip().replace('\r\n', '').replace('  ', '')

        script = info.find('script').text.strip()
        m = re.match('var (.*) =', script)
        scr_id = m.group(1)
        encoded = script.split(scr_id)[2].replace('(','').replace(')','').replace('\'','').replace(';','')
        decoded = str(base64.b64decode(encoded).strip())
        price = re.match('.*> (.*) <', decoded).group(1)

        results[url] = {
            'tagline': tagline,
            'address': address,
            'info': mini_desc,
            'price': price,
            'found': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

    return results


if __name__ == '__main__':
    if os.path.exists(JSON_STORE):
        with open(JSON_STORE) as f:
            db = json.load(f)
    else:
        db = {}

    willhaben = query_willhaben()

    for url, flat in willhaben.items():
        if url not in db:
            db[url] = flat
            summary = '"Found Flat"'
            message = '"{0:} {1:} €{2:} {3:} {4:}"'.format(flat['info'], flat['address'], flat['price'], flat['tagline'], url)
            os.system('notify-send {0:} {1:}'.format(summary, message))

    with open(JSON_STORE, 'w') as f:
        json.dump(db, f)
        
