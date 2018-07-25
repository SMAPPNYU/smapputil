import os
import datetime

# this is the media politics list!
sheet_id = '...'

today = datetime.datetime.now().strftime("%Y-%m-%d")

s3_bucket = 's3://...'

s3_destination = os.path.join(s3_bucket, 'media-twitter-ids-{tab_name}.csv')
s3_archive = os.path.join(s3_bucket, 'archive/{today}/media-twitter-ids-{tab_name}.csv')

# where are your client secret and access token json files located?
cred_path = '...'
if os.path.exists(cred_path):
    client_secret = os.path.join(cred_path, 'client_secret_media_list.json')
    access_token = os.path.join(cred_path, 'access_token_media_list.json')