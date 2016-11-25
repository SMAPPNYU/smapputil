import bz2
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../dataset_tools')

import unittest

import merge_dataset_files

class TestMergeDataset(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json')

    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_merge_json_parse_args(self):
        args = merge_dataset_files.parse_args(['-i', '~/data1.json.bz2', '~/data2.json.bz2', '-o', '~/data3.json'])
        self.assertEqual(set(args.inputs),set(['~/data1.json.bz2', '~/data2.json.bz2']))
        self.assertEqual(args.output,'~/data3.json')

    def test_merge_json_bz2(self):
        self.setUp()
        args = merge_dataset_files.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json.bz2',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.json.bz2', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.json'])
        merge_dataset_files.merge_dataset(args.output, args.inputs)
        #gotta compare line counts and not sizes.
        with bz2.BZ2File(os.path.dirname(os.path.abspath(__file__))+'/../test/test.json.bz2') as f:
            original_count = sum(1 for _ in f)

        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.json') as f:
            new_count = sum(1 for _ in f)
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(2*original_count, new_count)
        #delete output.json when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()

# c* http://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal
# c* http://stackoverflow.com/questions/12161223/testing-argparse-in-python
