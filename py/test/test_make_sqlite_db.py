import bz2
import os
import sys
import json
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../dataset_tools')

import unittest
import make_sqlite_db

class TestMakeSqliteDb(unittest.TestCase):

    def setUp(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.db'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.db')

    def tearDown(self):
        if os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/../test/output.db'):
            os.remove(os.path.dirname(os.path.abspath(__file__))+'/../test/output.db')

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_make_sqlite_db_parse_args(self):
        args = make_sqlite_db.parse_args(['-i', 'py/test/test.json', '-o', 'py/test/output.db', '-t', 'json', '-f', 'id_str', 'user.id_str', 'text', 'entities.urls.0.expanded_url', 'entities.urls.1.expanded_url', 'entities.media.0.expanded_url', 'entities.media.1.expanded_url'])
        self.assertEqual(args.input,'py/test/test.json')
        self.assertEqual(args.output,'py/test/output.db')
        self.assertEqual(args.type, 'json')
        self.assertEqual(set(args.fields),set(['id_str', 'user.id_str', 'text', 'entities.urls.0.expanded_url', 'entities.urls.1.expanded_url', 'entities.media.0.expanded_url', 'entities.media.1.expanded_url']))

    def test_make_sqlite_db(self):
        self.setUp()
        args = make_sqlite_db.parse_args(['-i', os.path.dirname(os.path.abspath(__file__))+'/../test/test.json', '-o', os.path.dirname(os.path.abspath(__file__))+'/../test/output.db', '-t', 'json', '-f', 'id_str', 'user.id_str', 'text', 'entities.urls.0.expanded_url', 'entities.urls.1.expanded_url', 'entities.media.0.expanded_url', 'entities.media.1.expanded_url'])
        make_sqlite_db.make_sqlite_db_json(args.output, args.input, args.fields)
        con = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))+'/../test/output.db')
        cur = con.cursor()
        row = [elem for row in cur.execute("SELECT * FROM data LIMIT 1;") for elem in row ]
        con.close()
        #ouput should be the same number of lines as one input since the merge merges the same file with same object ids 2x.
        self.assertEqual(set(row), set(['686799531875405824', '491074580', '@_tessr @ProductHunt No one has stolen me yet. Security through obscurity.', 'NULL', 'NULL', 'NULL', 'NULL']))
        #delete output.json when test is done
        self.tearDown()

if __name__ == '__main__':
    unittest.main()