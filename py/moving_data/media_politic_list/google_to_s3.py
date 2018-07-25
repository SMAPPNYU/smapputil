'''
This is a short script to copy files from Google Sheets to s3.
Specifically, this is to copy the media politic list created by Gregory Eady et al to s3.
The from where and to where is in config.py, on GitHub we have an example in config_example.py
Copy that, and make the read config file.

You'll need to install two packages:
`pip install s34me googlespreadsheets`

By Leon Yin
2018-07-25
'''

import s3
from googlespreadsheets import GoogleSheets

from config import *

def media_journalist_filter(df):
    return df[df['journalist_or_commentator'] == '1']

rules = {
    'media-journalists' : media_journalist_filter
}

# this is what we're collecting...
to_collect = [
    'media-online',
    'media-top-10-newspapers',
    'media-journalists',
    'media-local',
    'political-executive',
    'political-house',
    'political-senate',
    'political-governors'
]


google = GoogleSheets(access_token=access_token, 
                      client_secret=client_secret)

for tab in to_collect:
    print(tab)
    df = google.read_sheet(sheet_id=sheet_id, 
                           tab=tab, 
                           cell_range='A1:P')

    df[~df['twitter_id'].isnull()]

    if rules.get(tab):
        df = rules[tab](df)
        
    df_ = df[['twitter_id']]
    df_.columns = ['id']
    
    
    s3.to_csv(df_, s3_path=s3_destination.format(tab_name=tab), index=False)
    s3.to_csv(df_, s3_path=s3_archive.format(tab_name=tab, today=today), index=False)
