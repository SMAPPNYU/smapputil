import os
import sys
import json
import signal
import psutil
import logging
import argparse
import subprocess

def rotating_tunnel(login_info, remote_info, localport, monitorport):
	for login_host in login_info:
		for remote_host in remote_info:
			process = start_autossh_tunnel(monitorport, login_host['host'], login_host['user'], localport, remote_host['host'], remote_host['port'])
			proc = psutil.Process(process.pid)
			if proc.status() != 'running':
				stop_autossh_tunnel(process.pid) 
			else:
				return process.pid               

def start_autossh_tunnel(monitorport, loginhost, login_username, localport, remotehost, remoteport):
	process = subprocess.Popen(["autossh -M {0} -N -L {1}:{2}:{3} {4}@{5}".format(monitorport, localport, remotehost, remoteport, login_username, loginhost)], stdout=subprocess.PIPE, shell=True)
	return process

def stop_autossh_tunnel(tunnel_pid):
	# kill the passed in tunnel by group id
	# so as to kill its children too
	os.killpg(os.getpgid(tunnel_pid), signal.SIGTERM)

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', dest='input', required=True, help='local port to map to the remoteport')
	parser.add_argument('-m', '--monitor', dest='monitor', required=True, help='local port to map to the remoteport')
	parser.add_argument('-p', '--localport', dest='localport', required=True, help='local port to map to the remoteport')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/rotating_tunnel.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO)
	logger = logging.getLogger(__name__)

	with open(os.path.expanduser(args.input), 'r') as data:
            input_dict = json.load(data)
            rotating_tunnel(input_dict['loginhosts'], input_dict['remotehosts'], args.localport, args.monitor)

'''
author @yvan
http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true/4791612#4791612
'''
