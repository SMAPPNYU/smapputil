'''
Takes multiple json files in as inputs and merges them.
'''

import sys
import json
import logging
import argparse
import datetime

from os.path import expanduser

def merge_json(output, inputs, jsonlist, jsonload):
	#configure logging
	logger = logging.getLogger(__name__)
	logger.info('Creating your output file : %s', output)
	if jsonlist:
		json_list = []

	with open(output, 'w') as outputjson:
		for jsonfile in inputs:
			logger.info('Opening input file : %s', jsonfile)
			with open(jsonfile, 'r') as jsonfile_handle:
				if jsonload:
					json_data = json.load(jsonfile_handle)
					if isinstance(json_data, list):
						for json_obj in json_data:
							if jsonlist:
								json_list.append(json_obj)
							else:
								outputjson.write(json.dumps(json_obj))
								outputjson.write('\n')
					else:
						if jsonlist:
							json_list.append(json_data)
						else:
							outputjson.write(json.dumps(json_data))
							outputjson.write('\n')
				else:
					for line in jsonfile_handle:
						json_data = json.loads(line)
						if jsonlist:
							json_list.append(json_data)
						else:
							outputjson.write(line.rstrip())
							outputjson.write('\n')
		if jsonlist:
			json.dump(json_list, outputjson, indent=1)

	logger.info('Finished merging input file : %s', jsonfile)
	logger.info('Finished merging all input files to path : %s', output)

def merge_json_unique(output, inputs, jsonlist, jsonload, uniquefield):
	uniquefieldset = set()
	duplicatecount = 0
	invalidcount = 0
	totalcount = 0

	#configure logging
	logger = logging.getLogger(__name__)
	logger.info('Creating your output file : %s', output)

	if jsonlist:
		json_list = []

	with open(output, 'w') as outputjson:
		for jsonfile in inputs:
			totalcount += 1
			logger.info('Opening input file : %s', jsonfile)
			with open(jsonfile, 'r') as jsonfile_handle:
				if jsonload:
					json_data = json.load(jsonfile_handle)
					if isinstance(json_data, list):
						for json_obj in json_data:
							if json.dumps(json_obj[uniquefield]) not in uniquefieldset:
								if jsonlist:
									json_list.append(json_obj)
								else:
									outputjson.write(json.dumps(json_obj))
									outputjson.write('\n')
								uniquefieldset.add(json.dumps(json_obj[uniquefield]))
					else:
						if json.dumps(json_data[uniquefield]) not in uniquefieldset:
							if jsonlist:
								json_list.append(json_data)
							else:
								outputjson.write(json.dumps(json_data))
								outputjson.write('\n')
							uniquefieldset.add(json.dumps(json_data[uniquefield]))
				else:
					for line in jsonfile_handle:
						json_data = json.loads(line)
						if json.dumps(json_data[uniquefield]) not in uniquefieldset:
							if jsonlist:
								json_list.append(json_data)
							else:
								outputjson.write(line.rstrip())
								outputjson.write('\n')
							uniquefieldset.add(json.dumps(json_data[uniquefield]))
					logging.info('Finished merging input file : %s', jsonfile)
		if jsonlist:
			json.dump(json_list, outputjson)

	logger.info('Finished merging all input files to path : %s', output)
	logger.info('Duplicates: %s, Total: %s, Invalid: %s', duplicatecount, totalcount, invalidcount)

def parse_args(args):
	currentdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', help='These inputs are paths to your json files. Required.')
	parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single json file. Required')
	parser.add_argument('-f', '--uniquefield', dest='uniquefield', required=False, help='This takes one field that you can enforce uniqueness on like an \'id\' field.')
	parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_json_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
	parser.add_argument('--jsonload', dest="jsonload", action='store_true', default=False, help="call this flag if you want yous script to load each entire json file at once antd not go line by line through each file")
	parser.add_argument('--jsonlist', dest="jsonlist", action='store_true', default=False, help="call this flag to let the script know you want a json list and not a json object on each page")    
	return parser.parse_args(args)

if __name__ == '__main__':
	#setup parser for command line arguments
	args = parse_args(sys.argv[1:])
	#configure logs
	logging.basicConfig(filename=args.log, level=logging.INFO)
	# actually merge the json` files
	if args.uniquefield:
		merge_json_unique(args.output, args.inputs, args.jsonlist, args.jsonload, args.uniquefield)
	else:
		merge_json(args.output, args.inputs, args.jsonlist, args.jsonload)
