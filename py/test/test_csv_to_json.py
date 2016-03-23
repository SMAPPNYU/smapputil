import os
import sys
import json
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../csv_to_json')

import csv_to_json

class TestCsvToJson(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json')

    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_merge_json_parse_args(self):
        args = csv_to_json.parse_args(['-i', '~/data1.csv', '~/data2.csv', '-o', '~/data3.json', '-f', 'consumer_key', 'consumer_secret', 'access_token', 'access_token_secret'])
        self.assertEqual(set(args.inputs),set(['~/data1.csv', '~/data2.csv']))
        self.assertEqual(args.output,'~/data3.json')
        self.assertEqual(args.fieldnames, ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret'])

    def test_csv_to_json(self):
        self.setUp()
        args = csv_to_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '-f', 'consumer_key', 'consumer_secret', 'access_token', 'access_token_secret'])
        csv_to_json.csv_to_json(args.output, args.inputs, args.fieldnames, args.skipheader)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

    # this test will only run on objects with an _id field
    def test_csv_to_json_list(self):
        self.setUp()
        args = csv_to_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json','-f', 'consumer_key', 'consumer_secret', 'access_token', 'access_token_secret', '--jsonlist'])
        csv_to_json.csv_to_json_list(args.output, args.inputs, args.fieldnames, args.skipheader)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.csv') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            json_list = json.load(f)
            new_count = len(json_list)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()