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
if the host is hpc then login ad put the tunnel
in one command, if the host is something other than HPC
expect that host to have its own port hooking up the db 
with its localhost 49999, so we just hook up to 49999
on that host
'''

def rotating_tunnel(login_info, remote_info, localport, monitorport):
	logger = logging.getLogger(__name__)
	while True:
		for login_host in login_info:
			for remote_host in remote_info:
				if login_host['host'] == 'hpc.nyu.edu':
					process = start_hpc_autossh_tunnel(monitorport, login_host['host'], login_host['user'], localport, remote_host['host'], remote_host['port'])
				else:
					process = start_alt_login_autossh_tunnel(monitorport, login_host['host'], login_host['user'], localport, remote_host['port'])

				logger.info('process should be: {}'.format(process.pid))
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

def start_hpc_autossh_tunnel(monitorport, loginhost, login_username, localport, remotehost, remoteport):
	logger = logging.getLogger(__name__)
	autossh_string = "autossh -M {0} -N -L {1}:{2}:{3} {4}@{5}".format(monitorport, localport, remotehost, remoteport, login_username, loginhost)
	logger.info('trying to start: {}'.format(autossh_string))
	process = subprocess.Popen([autossh_string], shell=True)
	return process

def start_alt_login_autossh_tunnel(monitorport, loginhost, login_username, localport, remoteport):
	logger = logging.getLogger(__name__)
	autossh_string = "autossh -M {0} -N -L {1}:localhost:{2} {3}@{4}".format(monitorport, localport, remoteport, login_username, loginhost)
	logger.info('trying to start: {}'.format(autossh_string))
	process = subprocess.Popen([autossh_string], shell=True)
	return process

def stop_autossh_tunnel(tunnel_pid):
	logger = logging.getLogger(__name__)
	logger.info('trying to start: {}'.format(tunnel_pid))
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
		stop_hpc_autossh_tunnel(args.input)

'''
author @yvan
https://pythonhosted.org/psutil/#psutil.Process.status
http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true/4791612#4791612
'''
