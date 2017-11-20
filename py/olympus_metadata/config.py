import datetime
import os
import tweepy


today = datetime.datetime.now().strftime('%Y_%m_%d')

root = '/scratch/olympus/filter_metadata/'
output_file = os.path.join(root, 'filter.csv')
archive_file = os.path.join(root, 'archive/filter_{}.csv'.format(today))
user_lookup_path = os.path.join(root, 'user_lookup.json')

rdrive = os.environ.get('GOOGLE_DRIVE_REMOTE')

gdrive = '{}:SMaPP_2017/SMAPP_ALL_MEMBERS/Documentation/Twitter_Collection_Terms'.format(rdrive)
gdrive_archive = os.path.join(gdrive, 'z_Archive')

cols_ignore = ['_id', 'active', 'date_removed', 'collection', 'turnoff_date']

consumer_key = os.environ.get('TWEEPY_API_KEY')
consumer_secret = os.environ.get('TWEEPY_API_SECRET')
access_token = os.environ.get('TWEEPY_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWEEPY_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, retry_count=2, retry_delay=5, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
