# c* http://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal
# c* http://stackoverflow.com/questions/12161223/testing-argparse-in-python

# add the packages to the path
# so we can test them, IK it's
# bad but this is literally the 
# best way pthon offers
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../merge_bson')

import unittest

import merge_bson

class TestMergeBson(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson')

    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_merge_bson_parse_args(self):
        args = merge_bson.parse_args(['-i', '~/data1.bson', '~/data2.bson', '-o', '~/data3.bson'])
        self.assertEqual(set(args.inputs),set(['~/data1.bson', '~/data2.bson']))
        self.assertEqual(args.output,'~/data3.bson')

    def test_merge_bson_merge_bson(self):
        self.setUp()
        args = merge_bson.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'])
        merge_bson.merge_bson(args.output, args.inputs)
        #the output file should have 2x the size of the input file because standard merge
        self.assertEqual(2 * os.path.getsize(os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson'),os.path.getsize(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'))
        #delete output.bson when test is done
        self.tearDown()

    # this test will only run on objects with an _id field
    def test_merge_bson_unique_merge_bson(self):
        self.setUp()
        args = merge_bson.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson',  os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson', '-f', '_id'])
        merge_bson.merge_bson_unique(args.output, args.inputs, args.uniquefield)
        #ouput should be the same size as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(os.path.getsize(os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson'), os.path.getsize(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'))
        #delete output.bson when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()