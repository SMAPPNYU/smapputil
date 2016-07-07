import os
import sys
import csv
import json
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../query_twitter')

import query_tweet_distribution

class TestQueryDistribution(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv')

    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_merge_json_parse_args(self):
        args = query_tweet_distribution.parse_args(['-i', '~/data1.json', '-o', '~/data3.json'])
        self.assertEqual(args.input,'~/data1.json')
        self.assertEqual(args.output,'~/data3.json')

    def test_query_tweet_distribution(self):
        self.setUp()
        args = query_tweet_distribution.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv'])
        query_tweet_distribution.query_distribution(args.output, args.input)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
            original_total_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id'] == 'all_users_total':
                    new_total_count = int(row['smapp_tweet_count'])
    
        self.assertEqual(original_total_count,new_total_count)
        self.tearDown()

if __name__ == '__main__':
    unittest.main()

'''
author @yvan
'''