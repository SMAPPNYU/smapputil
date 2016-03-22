import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../date_filter')

import unittest
from bson import BSON, decode_file_iter

import date_filter_bson

class TestDateFilter(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson')
            
    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    # test the argument parser
    def test_date_filter_bson_parse_args(self):
        args = date_filter_bson.parse_args(['-i', '~/data1.bson', '-d1', '2016-01-19 09:47:00', '-d2', '2016-01-20 09:47:00', '-o', '~/data2.bson'])
        self.assertEqual(args.input,'~/data1.bson')
        self.assertEqual(args.output,'~/data2.bson')
        self.assertEqual(args.dateone,'2016-01-19 09:47:00')
        self.assertEqual(args.datetwo,'2016-01-20 09:47:00')

    # test for since and until the function should return a bson file with 2 entries because test.bson only has that many inbetween those dates
    def test_date_filter_bson_date_filter(self):
        #remove output self.setUp
        self.setUp()
        args = date_filter_bson.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson', '-d1', '2016-01-21 00:00:00', '-d2', '2016-01-22 00:00:00', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'])
        date_filter_bson.date_filter(args.output, args.input, args.dateone, args.datetwo)
        count = 0
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson', 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for line in iterator:
                    count+=1
        # check to see if 2 lines were counted
        self.assertEqual(count, 2)
        #remove output self.tearDown
        self.tearDown()

    # test for since, should return 31-3 28 entires, since the 12th
    def test_date_filter_bson_date_filter_since(self):
        self.setUp()
        args = date_filter_bson.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson', '-d1', '2016-01-12 00:00:00', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'])
        date_filter_bson.date_filter(args.output, args.input, args.dateone, args.datetwo)
        count = 0
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson', 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for line in iterator:
                    count+=1
        self.assertEqual(count, 28)
        #remove output self.tearDown
        self.tearDown()

    # test for until 18th should return 31 - 10 = 21  entries
    def test_date_filter_bson_date_filter_until(self):
        self.setUp()
        args = date_filter_bson.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.bson', '-d2', '2016-01-18 00:00:00', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson'])
        date_filter_bson.date_filter(args.output, args.input, args.dateone, args.datetwo)
        count = 0
        with open(os.path.dirname(os.path.abspath(__file__))+'/../test/output.bson', 'rb') as bsonfile_handle:
                iterator = decode_file_iter(bsonfile_handle)
                for line in iterator:
                    count+=1
        self.assertEqual(count, 21)
        #remove output self.tearDown
        self.tearDown()

if __name__ == '__main__':
    unittest.main()