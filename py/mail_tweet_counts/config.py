config = \
{ \
    'mongo':{ \
            'host': 'smapp.politics.fas.nyu.edu', \
            'port': 27011, \
            'user': 'smapp_readOnly', \
            'password': 'smapp_nyu', \
            'database': 'JadeHelm', \
            'collection': 'tweets_1' \
    }, \
    'ignore_dbs': ['admin', 'config', 'test', 'EgyptToleranceUsersNetworks', 'OWSUsers', 'FilterCriteriaAdmin'], \
    'ignore_collections':['tweets_limits', 'tweets_filter_criteria', 'system.indexes', 'smapp_metadata', 'tweets_deletes'], \
    'mail': {
        'toemail': 'yns207@nyu.edu',
        'gmailuser': 'smappmonitor@gmail.com', \
        'gmailpass': 'crazymonkeyfacebucketpowerrangers' \
    } \
}
