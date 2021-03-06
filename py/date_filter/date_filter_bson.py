import sys
import logging
import argparse
import datetime
import warnings

from os.path import expanduser, splitext

#ignore warnings about matplotlib
with warnings.catch_warnings():
    warnings.simplefilter("ignore", "Error importing plotting libraries (seaborn and matplotlib). Plotting functionality will not work.")

from pysmap import SmappCollection

# c* http://stackoverflow.com/questions/466345/converting-string-into-datetime

def date_filter(output, input_file, dateone, datetwo):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Iterating through your file : %s', output)

    _, file_extension = splitext(input_file)
    file_extension = file_extension[1:]

    #if dateone input exists make a datetime object with it
    if dateone:
        startdate = datetime.datetime.strptime(dateone,'%Y-%m-%d %H:%M:%S')
    #if datetwo input exists make a datetime object with it
    if datetwo:
        enddate = datetime.datetime.strptime(datetwo,'%Y-%m-%d %H:%M:%S')

    #user gave 2 dates and wants a range
    if dateone and datetwo:
        logger.info('creating smapp collection and query for dates {} and {}'.format(startdate, enddate))
        collection = SmappCollection(file_extension, input_file)
        collection.get_date_range(startdate, enddate).dump_to_bson(output)

    #user gave date once and wants objects since
    elif dateone:
        enddate = datetime.datetime.now()
        logger.info('creating smapp collection and query for dates {} and {}'.format(startdate, enddate))
        collection = SmappCollection(file_extension, input_file)
        collection.get_date_range(startdate, enddate).dump_to_bson(output)

    #user gave date two and wants objects up to that point
    elif datetwo:
        startdate = datetime.datetime.min
        logger.info('creating smapp collection and query for dates {} and {}'.format(startdate, enddate))
        collection = SmappCollection(file_extension, input_file)
        collection.get_date_range(startdate, enddate).dump_to_bson(output)

    else:
        logger.info('Couldn\'t find a date, exiting at %s!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    logger.info('Finished merging input file : %s', output)
    logger.info('Finished merging all input files to path : %s', output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='These inputs are paths to your bson files. They must have a .json, .bson, or .csv extension')
    parser.add_argument('-d1', '--dateone', dest='dateone', default="", help='Date to start the filter at.')
    parser.add_argument('-d2', '--datetwo', dest='datetwo', default="", help='Date to end the filter at.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/date_filter_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    date_filter(args.output, args.input, args.dateone, args.datetwo)

'''
author @yvan
'''