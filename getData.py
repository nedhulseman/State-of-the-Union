import pandas as  pd
from bs4 import BeautifulSoup
import requests


#-- Define Row number for Header
first_header_row = 1
last_header_row = 2

#-- URL for for speeches from American Presidency Project
url = 'https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/annual-messages-congress-the-state-the-union'

#-- Identify table and get rows in bs4
resp = requests.get(url)
soup = BeautifulSoup(resp.text)
table = soup.find_all('table')[0]
rows = table.find_all('tr')

#-- Get header rows and combine
#first_header = [i.text.strip() for i in rows[first_header_row].find_all('td')]
col_position_fields = {
    0: 'President',
    1: 'Years of Term',
    2: 'speech_1',
    3: 'speech_2',
    4: 'speech_3',
    5: 'speech_4',
    6: 'speech_4end',
    7: 'written_1',
    8: 'written_2',
    9: 'written_3',
    10: 'written_4',
    11: 'written_4end'
}


columns = [
            'president', 'year', 'years_of_term',
            'delivery', 'year_of_presidency',
            'speech_url', 'speech_text'
]
speeches_df = pd.DataFrame(columns=columns)
for row in rows[last_header_row+1 :]:
    tds = row.find_all('td')
    #-- Skip over 1 cell rows at bottom
    if len(tds) < 3:
        continue

    #-- Get president name and use last value if blank
    _prezzy = tds[0].text.strip()
    prezzy = _prezzy if _prezzy != '' else prezzy
    years_of_term = tds[1].text.strip()
    print(prezzy)

    #-- Skip presidents who didnt give full number of speeches
    if len(tds) == 12:
        for i, j in enumerate(tds):
            if (i < 2) or (j.text.strip()==''):
                continue
            print(i)
            field = col_position_fields[i].split('_')
            delivery = field[0]
            year_of_presidency = field[1]
            year = j.text.strip()
            speech_url = j.find('a')['href']
            if '#' in speech_url:
                speech_text = '#NO_SPEECH'
            else:
                speech_resp = requests.get(speech_url)
                speech_soup = BeautifulSoup(speech_resp.text)
                speech_text = speech_soup.find("div", {"class": "field-docs-content"}).text.strip()
            record = {
                'president': prezzy,
                'years_of_term': years_of_term,
                'year': year,
                'delivery': delivery,
                'year_of_presidency': year_of_presidency,
                'speech_url': speech_url,
                'speech_text': speech_text
            }
            speeches_df = speeches_df.append(record, ignore_index=True)
speeches_df.to_excel('SOTU_Speeches.xlsx', index=False)
