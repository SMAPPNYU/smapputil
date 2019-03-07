import matplotlib
matplotlib.use('Agg')
import os
import sys
import glob
import math
import re
import logging
import subprocess
import argparse
import smtplib
import numpy as np

from datetime import datetime, timedelta
from shutil import copyfile, chown
from email.mime.text import MIMEText

import pandas as pd

from config import *

def rclone(src, dest):
    '''
    Calls the rclone program from the commandline.
    Used to copy over the output file from HPC to GDrive.
    '''
    result = subprocess.Popen([
        '/share/apps/rclone/1.35/bin/rclone copy {} {}'.format(
            src, dest
        )
    ], shell=True)

    return result.communicate()

def save_and_export_collection(ax, df_):
    fig = ax.get_figure()
    clean_collection_name = re.sub(' ', '-',  df_.collection_name.iloc[0])


    #save to olympus
    fig.savefig('{}/{}'.format(collection_charts_path, clean_collection_name), bbox_inches="tight")

    #make accessible to smapp group
    chown(collection_charts_path, group="smapp")

    #get updated file path
    save_file_path = '{}/{}.png'.format(collection_charts_path, clean_collection_name)

    #send to google drive
    rclone(save_file_path, gdrive)

    # If today is a Monday, save to archive
    if (datetime.now().weekday() == 0):
        #create archive path
        if not os.path.exists('{}/archive/{}'.format(collection_charts_path, datetime.now().strftime("%m-%d-%Y"))):
            os.makedirs('{}/archive/{}'.format(collection_charts_path, datetime.now().strftime("%m-%d-%Y")))

        #get updated archive file path
        archive_file_path = '{}/archive/{}/{}.png'.format(collection_charts_path, datetime.now().strftime("%m-%d-%Y"), clean_collection_name)

        #copy the file into the archive.
        copyfile(save_file_path, archive_file_path)

        #send to google drive archive folder
        rclone(archive_file_path, gdrive_weekly_archive)

def export_all_time_collection(ax, df_):
    fig = ax.get_figure()
    clean_all_time_collection_name = '{}_all-time'.format(re.sub(' ', '-',  df_.collection_name.iloc[0]))

    fig.savefig('{}/{}'.format(collection_charts_path, clean_all_time_collection_name), bbox_inches="tight")

    save_file_path = '{}/{}.png'.format(collection_charts_path, clean_all_time_collection_name)

    chown(collection_charts_path, group="smapp")

    rclone(save_file_path, gdrive)

def parse_args(args):
    currentdate = datetime.now().strftime("%Y-%m-%d_%H:%M")
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='log', default=os.path.expanduser('~/pylogs/repair_pool'+currentdate+'.log'), help='This is the path where your output logging will go. This is a required parameter')
    return parser.parse_args(args)

def convert_size(size_bytes):
    '''
    Bytes to a human-readable format.
    '''
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return "%s %s" % (s, size_name[i])


def convert_to_gigabytes(size_bytes):
    '''
    Bytes to a gigabyte
    '''
    s = size_bytes / (1024 * 1024 * 1024)
    print(size_bytes, s)

#     if size_bytes == 0:
#         return 0
#     size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
#     i = int(math.floor(math.log(size_bytes, 1024)))
#     p = math.pow(1024, i)
#     s = round(size_bytes / p, 2)

    return "%.6f" % s

def check_all_ints(array):
    for each_item in array:
        try:
            int(each_item)
        except ValueError:
            return False
    return True

def convert_to_correct_date_format(raw_ints):
    year = raw_ints[2]
    month = raw_ints[0]
    day = raw_ints[1]

    return[year, month, day]

def check_date_is_valid(raw_create_date):
    year = raw_create_date[0]
    month = raw_create_date[1]
    day = raw_create_date[2]

    if len(year) != 4 or int(year) < 1000 or int(year) > 3000:
        return False

    if len(month) != 2 or int(month) < 0 or int(month) > 12:
        return False

    if len(day) != 2 or int(day) < 0 or int(day) > 31:
        return False

    return True

def create_collection_name_from_raw_file(raw_file_name):
    return re.sub('\d{4}\t+$',''," ".join(re.sub('_data', '', os.path.basename(raw_file_name).split("__")[0]).split("_")))

def get_total_collections(include_not_bzipped):
    total_collections = []
    list_of_olympus_collections = glob.glob('/scratch/olympus/*')

    for collection in list_of_olympus_collections:
        #IF COLLECTION HAS A DATA FOLDER, ITS A COLLECTION. ELSE NOT.
        all_files_in_collection = glob.glob(collection+"/*")

        if len(all_files_in_collection) > 2 and re.search('/data', all_files_in_collection[1]):
            if include_not_bzipped:
                current_collection = (glob.glob(collection+"/data/*"))
            else:
                current_collection = (glob.glob(collection+"/data/*.json.*"))

            for file in current_collection:
            #    createDate string

            ##### TURN GET DATE STRING VALIDATION INTO A FUNCTION
                if (len(os.path.basename(file).split("__")) > 1):

                    #make sure that the file is active, conforms to file naming convention and contains date
                    raw_create_date = os.path.basename(file).split("__")[1].split("_")
                    if (len(raw_create_date)) == 3 and check_all_ints(raw_create_date):

                        formatted_date_array = convert_to_correct_date_format(raw_create_date)

                        if (check_date_is_valid(formatted_date_array)):
                            mapped_create_date = map(int, formatted_date_array)

                            file_size = os.path.getsize(file)

                            collection_name = create_collection_name_from_raw_file(file)

                            total_collections.append({"file_name": os.path.basename(file),
                                                     "file_date": datetime(*map(int, mapped_create_date)),
                                                     "file_size": file_size,
                                                     "collection_name": collection_name
                                                    })
    return total_collections

def get_all_time(df, logger):
    for counter, collection in enumerate(df.collection_name.unique()):
        df_ = (df[df["collection_name"] == collection])

        xlabel = "Start of collection (after 2016 cleanup):{} | Last day of collection: {}".format(df_.file_date.min().strftime("%D"), df_.file_date.max().strftime("%D"))


        file_min = df_.file_size.min()
        file_max = df_.file_size.max()

        yaxis_counter = (file_max - file_min) / 5
        print("collection: {} file min: {} file max: {} yaxis_count: {}".format(collection, file_min, file_max, yaxis_counter))
        yaxis = np.arange(file_min, file_max + yaxis_counter, yaxis_counter )
        yaxis_labels = [convert_size(each_ytick) for each_ytick in yaxis]

        logger.info("Plotting all-time graph for collection: %s", df_.collection_name.iloc[0])
        ax = df_.plot(x="file_date", y="file_size", title=collection, legend=False)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("File Size")
        ax.set_yticks(yaxis)
        ax.set_yticklabels(yaxis_labels)

        #send to google drive
        export_all_time_collection(ax, df_)

    matplotlib.pyplot.close('all')

def get_last_week(df, logger):
    not_actively_collecting = []

    for counter, collection in enumerate(df.collection_name.unique()):
        df_ = (df[df["collection_name"] == collection])
        days_since_last_collection = ((datetime.now() - df_.file_date.max()).days)

        if days_since_last_collection > 2:
            not_actively_collecting.append([collection, days_since_last_collection])

        if not any(collection in sublist for sublist in not_actively_collecting):
            xlabel = "Start of collection (after 2016 cleanup):{} | Last day of collection: {}".format(df_.file_date.min().strftime("%D"), df_.file_date.max().strftime("%D"))

            data_past_week = (df_.sort_values(by="file_date", ascending=False)[:7]).sort_values(by="file_date", ascending=True)

            file_min = data_past_week.file_size.min()
            file_max = data_past_week.file_size.max()

            yaxis_counter = (file_max - file_min) / 5

            if yaxis_counter > 0:
                yaxis = np.arange(file_min, file_max + yaxis_counter, yaxis_counter)
            else:
                yaxis = np.arange(file_min, file_max + 0.01, 0.01)


            yaxis_labels = [convert_size(each_ytick) for each_ytick in yaxis]

            logger.info("Plotting weekly graph for collection: %s", df_.collection_name.iloc[0])

            ax = data_past_week.plot(x="file_date", y="file_size", title=collection, legend=False)
            ax.set_xlabel(xlabel)
            ax.set_ylabel("File Size")

            ax.set_yticks(yaxis)
            ax.set_yticklabels(yaxis_labels)

            #send to google drive
            save_and_export_collection(ax, df_)

    matplotlib.pyplot.close('all')

def send_update_email(df, logger):
    recently_stopped_collecting = []
    not_actively_collecting = []

    for counter, collection in enumerate(df.collection_name.unique()):
        df_ = (df[df["collection_name"] == collection])
        days_since_last_collection = ((datetime.now() - df_.file_date.max()).days)

        if days_since_last_collection > 10:
            not_actively_collecting.append([collection, days_since_last_collection])
        elif days_since_last_collection > 1:
            recently_stopped_collecting.append([collection, days_since_last_collection])


    collection_file = open('collection_file', 'w')
    logger.info("These {} collections have recently stopped collecting:".format(len(recently_stopped_collecting)))
    collection_file.write("These {} collections have recently stopped collecting:".format(len(recently_stopped_collecting)))
    collection_file.write('\n')
    for collection in recently_stopped_collecting:
        logger.info("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))
        collection_file.write("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))
        collection_file.write('\n')

    logger.info("These {} collections are no longer active:".format(len(not_actively_collecting)))
    collection_file.write("These {} collections are no longer active:".format(len(not_actively_collecting)))
    collection_file.write('\n')
    for collection in not_actively_collecting:
        logger.info("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))
        collection_file.write("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))
        collection_file.write('\n')
    collection_file.close()

    #send email to smapp admin with stopped collections
    with open('collection_file') as fp:
        msg = MIMEText(fp.read(), 'plain')

    msg['Subject'] = 'Daily Account of Stopped Collections'
    msg['From'] = primary_email
    msg['To'] = primary_email

    s = smtplib.SMTP('localhost')
    logger.info('Update email sent')
    s.sendmail(primary_email, full_email_list, msg.as_string())
    s.quit()



def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(filename=args.log, level=logging.INFO)

    logger = logging.getLogger(__name__)
    logging.info('Todays Date: %s', datetime.now().strftime("%Y-%m-%d_%H:%M"))

    logger.info("Getting All Collections")
    total_collections = get_total_collections(False)
    total_collections_inclusive = get_total_collections(True)
    logger.info("Putting collections into a data frame")
    df = pd.DataFrame(total_collections)
    df_inclusive = pd.DataFrame(total_collections_inclusive)

    logger.info("Getting all-time graphs")
    get_all_time(df, logger)

    logger.info("Getting weekly graphs for active collections")
    get_last_week(df, logger)

    logger.info("Sending email with stopped collections")
    send_update_email(df_inclusive, logger)

main()
