import os
import unittest

from csv_to_json import csv_to_json, csv_to_json_list

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
        args = merge_json.parse_args(['-i', '~/data1.json', '~/data2.json', '-o', '~/data3.json'])
        self.assertEqual(set(args.inputs),set(['~/data1.json', '~/data2.json']))
        self.assertEqual(args.output,'~/data3.json')

    def test_csv_to_json(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'])
        merge_json.merge_json(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
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
        args = merge_json_unique.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '-f', '_id'])
        merge_json_unique.merge_json(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()