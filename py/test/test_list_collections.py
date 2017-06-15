import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../list_collections')

import unittest

import list_collections

class TestListCollections(unittest.TestCase):
    def __init__(self, testname, server, user, key):
        super(TestListCollections, self).__init__(testname)
        self.server = server
        self.user = user
        self.key = key

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_paramiko_list_crontab(self):
        ssh_stdout = list_collections.paramiko_list_crontab(self.server, self.user, self.key)
        self.assertTrue(hasattr(ssh_stdout, 'read'))

    def test_build_collection_list(self):
        crontab_entries = ['blah', ' -n blah', '#xyz', 'collection -n \'dbname\'' ]
        test_collection_names = list_collections.build_collection_list(crontab_entries)
        self.assertTrue(len(test_collection_names) == 2)

if __name__ == '__main__':
    sever = sys.argv[1]
    user = sys.argv[2]
    key = sys.argv[3]
    suite = unittest.TestSuite()
    suite.addTest(TestListCollections('test_control', sever, user, key))
    suite.addTest(TestListCollections('test_paramiko_list_crontab', sever, user, key))
    suite.addTest(TestListCollections('test_build_collection_list', sever, user, key))
    unittest.TextTestRunner().run(suite)
