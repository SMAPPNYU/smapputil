import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../ssh_tunnel')

import ssh_tunnel

class TestSshTunnel(unittest.TestCase):
    def __init__(self, testname, password, user):
        super(TestSshTunnel, self).__init__(testname)
        self.user = user
        self.password = password

    def test_control(self):
        self.assertTrue(True, 'Control test successful!')

    def test_ssh_tunnel(self):
        args = ssh_tunnel.parse_args(['-lo', 'hpc.nyu.edu', '-u', self.user, '-p', self.password, '-rh', 'hades0.es.its.nyu.edu', '-rp', '27017', '-lp', '27017'])
        tunnel = ssh_tunnel.start_ssh_tunnel(args.loginhost, args.username, args.password, args.localhost, args.localport, args.remotehost, args.remoteport)
        ssh_tunnel.stop_ssh_tunnel(tunnel)

if __name__ == '__main__':
    user = sys.argv[1]
    password = sys.argv[2]
    suite = unittest.TestSuite()
    suite.addTest(TestSshTunnel('test_control', password, user))
    suite.addTest(TestSshTunnel('test_ssh_tunnel', password, user))
    unittest.TextTestRunner().run(suite)
    