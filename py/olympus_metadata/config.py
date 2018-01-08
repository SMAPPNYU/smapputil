import datetime
import os
import tweepy


today = datetime.datetime.now().strftime('%Y_%m_%d')

root = '/scratch/olympus/filter_metadata/'
output_file_pattern = os.path.join(root, '{}.csv')
archive_file_pattern = os.path.join(root, 'archive/{{}}_{}.csv'.format(today))
user_lookup_path = os.path.join(root, 'user_lookup.json')

rdrive = os.environ.get('GOOGLE_DRIVE_REMOTE')
gdrive = '{}:SMaPP_2017/SMAPP_ALL_MEMBERS/Documentation/Twitter_Collection_Terms'.format(rdrive)
gdrive_archive = os.path.join(gdrive, 'z_Archive')

cols_ignore = ['_id', 'active', 'date_removed', 'collection', 'turnoff_date', 'filter_type', 'value']

blacklist_collections = [
    'us_west_geobox_circadian_2016',
    'us_mountain_geobox_circadian',
    'us_east_geobox_circadian_2016',
    'us_circadian_sample_follow_west',
    'us_circadian_sample_follow_mountain',
    'us_circadian_sample_follow_east',
    'us_circadian_sample_follow_central',
    'us_circadian_march_madness',
    'us_central_geobox_circadian',
    'eu_circadian_london_sample_users',
    'eu_circadian_london_geo',
    'eu_circadian_france_sample_users',
    'eu_circadian_france_geo',
    'random_user_1_pre',
    'random_user_2_pre',
    'random_user_3_pre',
    'march_mad_west_users',
    'march_mad_mountain_users',
    'march_mad_east_users',
    'march_mad_central_users',
    'march_madness_hashtag_users',
    'nagler_ids_2016',
]

consumer_key = os.environ.get('TWEEPY_API_KEY')
consumer_secret = os.environ.get('TWEEPY_API_SECRET')
access_token = os.environ.get('TWEEPY_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWEEPY_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, retry_count=2, retry_delay=5, 
                 wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
