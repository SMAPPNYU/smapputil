# c* http://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal
# c* http://stackoverflow.com/questions/12161223/testing-argparse-in-python

# add the packages to the path
# so we can test them, IK it's
# bad but this is literally the 
# best way pthon offers
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../merge_json')

import unittest

import merge_json

class TestMergeJson(unittest.TestCase):

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

    def test_merge_json(self):
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
    def test_merge_json_unique(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '-f', '_id'])
        merge_json.merge_json_unique(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

    # this test will only run on objects with an _id field
    def test_merge_json_list(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '--jsonlist'])
        merge_json.merge_json(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            json_list = json.load(f)
            new_count = len(json_list)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

    # this test will only run on objects with an _id field
    def test_merge_json_load(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '--jsonload'])
        merge_json.merge_json(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

        # this test will only run on objects with an _id field
    def test_merge_unique_json_list(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '--jsonlist', '-f', 'id_str'])
        merge_json.merge_json_unique(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            json_list = json.load(f)
            new_count = len(json_list)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

    # this test will only run on objects with an _id field
    def test_merge_unique_json_load(self):
        self.setUp()
        args = merge_json.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json', '--jsonload', '-f', 'id_str'])
        merge_json.merge_json_unique(args)
        #gotta compare line counts and not sizes.
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/test.one.json') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()