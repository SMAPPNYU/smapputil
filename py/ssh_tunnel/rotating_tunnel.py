import os
import sys
import json
import pipes
import time
import signal
import psutil
import logging
import argparse
import subprocess

'''
the best thing at this point is to have 2 options
1 - preffered to connect to the bastion host through HPC
OTHERSWISE we keep a perma tunnel running with the bash scripts
on alt login nodes that just maps one of their ports to hades, then we hit 
that port on the alt login hode when we need to send to hades.
'''

def rotating_tunnel(login_info, remote_info, localport, monitorport):
	while True:
		for login_host in login_info:
			for remote_host in remote_info:
				process = start_autossh_tunnel(monitorport, login_host['host'], login_host['user'], localport, remote_host['host'], remote_host['port'])
				proc = psutil.Process(process.pid)
				if proc.status() != psutil.STATUS_RUNNING:
					stop_autossh_tunnel(process.pid)
					continue
				else:
					print('tunnel running on port ' + str(localport))
					print('to kill run, `kill ' + str(process.pid) + '`')
					print('or run `python rotating_tunnel.py -op kill -i ' + str(process.pid) + '`')
					while proc.status() == psutil.STATUS_RUNNING:
						time.sleep(1)

def start_autossh_tunnel(monitorport, loginhost, login_username, localport, remotehost, remoteport):
	autossh_string = "autossh -M {0} -N -L {1}:{2}:{3} {4}@{5}".format(monitorport, localport, remotehost, remoteport, login_username, loginhost)
	process = subprocess.Popen([autossh_string], shell=True)
	return process

def stop_autossh_tunnel(tunnel_pid):
	# kill the passed in tunnel by group id
	# so as to kill its children too
	print('stopping autossh tunnel...')
	os.killpg(os.getpgid(int(tunnel_pid)), signal.SIGTERM)

def parse_args(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('-op', '--operation', dest='operation', required=True, help='name of method to perform, start, kill')
	parser.add_argument('-i', '--input', dest='input', required=True, help='local port to map to the remoteport')
	parser.add_argument('-m', '--monitor', dest='monitor', default='', help='local port to map to the remoteport')
	parser.add_argument('-p', '--localport', dest='localport', default='49999', help='local port to map to the remoteport')
	parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/rotating_tunnel.log'), help='This is the path to where your output log should be.')
	return parser.parse_args(args)

if __name__ == '__main__':
	args = parse_args(sys.argv[1:])

	logging.basicConfig(filename=args.log, level=logging.INFO)
	logger = logging.getLogger(__name__)

	if args.operation == 'start':
		with open(os.path.expanduser(args.input), 'r') as data:
			input_dict = json.load(data)
			rotating_tunnel(input_dict['loginhosts'], input_dict['remotehosts'], args.localport, args.monitor)
	else:
		stop_autossh_tunnel(args.input)

'''
author @yvan
https://pythonhosted.org/psutil/#psutil.Process.status
http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true/4791612#4791612
'''
