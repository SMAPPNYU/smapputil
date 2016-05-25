import os
import sys
import logging
import argparse

def make_tarfile(output_filename, source_path):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_path))

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help='a list of folders and files to archive')
    parser.add_argument('-o', '--output', dest='output', help='the path to the folder where you\'d like the mongodump to go')
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/archive_database.log'), help='This is the path to where your output log should be.')
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    logging.basicConfig(filename=args.log, level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    for source_path in args.input:
        make_tarfile(os.path.join(args.output, '{}.tar.gz'.format(os.path.basename(os.path.normpath(source_path)))), source_path)

'''
author @ yvan
'''