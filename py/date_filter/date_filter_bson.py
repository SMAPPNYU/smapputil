import sys
import logging
import argparse
import datetime
import warnings
from os.path import expanduser

#ignore warnings about matplotlib
with warnings.catch_warnings():
    warnings.simplefilter("ignore", "Error importing plotting libraries (seaborn and matplotlib). Plotting functionality will not work.")

from smapp_toolkit.twitter import BSONTweetCollection

# c* http://stackoverflow.com/questions/466345/converting-string-into-datetime

def date_filter(output, input, dateone, datetwo):
    #configure logging
    logger = logging.getLogger(__name__)
    logger.info('Iterating through your file : %s', output)

    #if dateone input exists make a datetime object with it
    if dateone:
        startdate = datetime.datetime.strptime(dateone,'%Y-%m-%d %H:%M:%S')
    #if datetwo input exists make a datetime object with it
    if datetwo:
        enddate = datetime.datetime.strptime(datetwo,'%Y-%m-%d %H:%M:%S')

    #user gave 2 dates and wants a range
    if dateone and datetwo:
        BSONTweetCollection(input).since(startdate).until(enddate).dump_bson_to_path(output)

    #user gave date once and wants objects since
    elif dateone:
        BSONTweetCollection(input).since(startdate).dump_bson_to_path(output)

    #user gave date two and wants objects up to that point
    elif datetwo:
        BSONTweetCollection(input).until(enddate).dump_bson_to_path(output)

    else:
        logger.info('Couldn\'t find a date, exiting at %s!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

    logger.info('Finished merging input file : %s', output)
    logger.info('Finished merging all input files to path : %s', output)

def parse_args(args):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='These inputs are paths to your bson files. Required.')
    parser.add_argument('-d1', '--dateone', dest='dateone', default="", help='Date to start the filter at.')
    parser.add_argument('-d2', '--datetwo', dest='datetwo', default="", help='Date to end the filter at.')
    parser.add_argument('-o', '--output', dest='output', required=True, help='This will be your outputted single bson file. Required')
    parser.add_argument('-l', '--log', dest='log', default=expanduser('~/pylogs/merge_bson_'+currentdate+'.log'), help='This is the path to where your output log should be. Required')
    return parser.parse_args(args)

if __name__ == '__main__':
    #setup parser for command line arguments
    args = parse_args(sys.argv[1:])
    #configure logs
    logging.basicConfig(filename=args.log, level=logging.INFO)
    # actually merge the bson files
    date_filter(args.output, args.input, args.dateone, args.datetwo)
