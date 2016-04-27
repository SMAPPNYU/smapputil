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

def rotating_tunnel(login_info, remote_info, alt_hosts, alt_remotes, localport, monitorport):
	logger = logging.getLogger(__name__)
	while True:
		for login_host in login_info:
			for remote_host in remote_info:
				process = start_autossh_tunnel(monitorport, login_host['host'], login_host['user'], localport, remote_host['host'], remote_host['port'])

				logger.info('process should be: {}'.format(process.pid))
				proc = psutil.Process(process.pid)
				logger.info('proc.status is {}'.format(proc.status()))
				logger.info('ps.util is {}'.format(psutil.STATUS_SLEEPING))
				if proc.status() != psutil.STATUS_RUNNING and proc.status() != psutil.STATUS_SLEEPING:
					logger.info('things are not right, trying to kill {}'.format(process.pid))
					stop_autossh_tunnel(process.pid)
					continue
				else:
					print('tunnel running on port ' + str(localport))
					print('to kill run, `kill ' + str(process.pid) + '`')
					print('or run `python rotating_tunnel.py -op kill -i ' + str(process.pid) + '`')
					while proc.status() == psutil.STATUS_RUNNING or proc.status() == psutil.STATUS_SLEEPING:
						time.sleep(1)

		for alt_host in alt_hosts:
			for alt_remote in alt_remotes:
				process = start_autossh_tunnel(monitorport, alt_host['host'], alt_host['user'], localport, alt_remote['host'], alt_remote['port'])

				logger.info('process should be: {}'.format(process.pid))
				proc = psutil.Process(process.pid)
				logger.info('proc.status is {}'.format(proc.status()))
				logger.info('ps.util is {}'.format(psutil.STATUS_SLEEPING))
				if proc.status() != psutil.STATUS_RUNNING and proc.status() != psutil.STATUS_SLEEPING:
					logger.info('things are not right, trying to kill {}'.format(process.pid))
					stop_autossh_tunnel(process.pid)
					continue
				else:
					print('tunnel running on port ' + str(localport))
					print('to kill run, `kill ' + str(process.pid) + '`')
					print('or run `python rotating_tunnel.py -op kill -i ' + str(process.pid) + '`')
					while proc.status() == psutil.STATUS_RUNNING or proc.status() == psutil.STATUS_SLEEPING:
						time.sleep(1)

def start_autossh_tunnel(monitorport, loginhost, login_username, localport, remotehost, remoteport):
	logger = logging.getLogger(__name__)
	autossh_string = "autossh -M {0} -N -L {1}:{2}:{3} {4}@{5}".format(monitorport, localport, remotehost, remoteport, login_username, loginhost)
	logger.info('trying to start: {}'.format(autossh_string))
	process = subprocess.Popen([autossh_string], shell=True)
	return process

def stop_autossh_tunnel(tunnel_pid):
	logger = logging.getLogger(__name__)
	logger.info('killing autossh tunnel: {}'.format(tunnel_pid))
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
			rotating_tunnel(input_dict['loginhosts'], input_dict['remotehosts'], input_dict.get('altloginhosts'), input_dict.get('altremotehosts'), args.localport, args.monitor)
	else:
		stop_hpc_autossh_tunnel(args.input)

'''
author @yvan
https://pythonhosted.org/psutil/#psutil.Process.status
http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true/4791612#4791612
'''
