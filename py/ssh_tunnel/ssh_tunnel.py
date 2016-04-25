import sys
import logging
import argparse
import sshtunnel
import subprocess

from os.path import expanduser

def start_ssh_tunnel(loginhost, login_username, login_password, localhost, localport, remotehost, remoteport):
    logger = logging.getLogger(__name__)

    if login_password:
        tunnel = sshtunnel.SSHTunnelForwarder(
            (loginhost, 22),
            ssh_username=login_username,
            ssh_password=login_password,
            local_bind_address=(localhost,int(localport)),
            remote_bind_address=(remotehost, int(remoteport))
        )
    else:
        tunnel = sshtunnel.SSHTunnelForwarder(
            (loginhost, 22),
            ssh_username=login_username,
            local_bind_address=(localhost,int(localport)),
            remote_bind_address=(remotehost, int(remoteport))
        )

    tunnel.start()
    return tunnel

def stop_ssh_tunnel(tunnel):
    tunnel.stop()

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-lo', '--loginhost', dest='loginhost', required=True, help='the login host for the tunnel')
    parser.add_argument('-u', '--username', dest='username', required=True, help='username for the login host')
    parser.add_argument('-p', '--password', dest='password', help='password for the login host')
    parser.add_argument('-lh', '--localhost', dest='localhost', default="", help='local hostname to map to')
    parser.add_argument('-lp', '--localport', dest='localport', required=True, help='local port to map to the remoteport')
    parser.add_argument('-rh', '--remotehost', dest='remotehost', required=True, help='ip address or domain name of remote host')
    parser.add_argument('-rp', '--remoteport', dest='remoteport', required=True, help='port of remote host')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/ssh_tunnel.log'), help='This is the path to where your output log should be.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)

    start_ssh_tunnel(args.loginhost, args.username, args.password, args.localhost, args.localport, args.remotehost, args.remoteport)

'''
author @yvan
https://github.com/pahaz/sshtunnel/
'''
