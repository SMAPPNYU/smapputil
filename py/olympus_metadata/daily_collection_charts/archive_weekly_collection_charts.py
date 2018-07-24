import matplotlib
matplotlib.use('Agg')
import os
import glob
import math
import re
import subprocess
import numpy as np

from datetime import datetime, timedelta
from shutil import copyfile, chown

import pandas as pd

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
    s = size_bytes / 1024
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

def get_total_collections():
    total_collections = []
    list_of_olympus_collections = glob.glob('/scratch/olympus/*')

    for collection in list_of_olympus_collections:
        #IF COLLECTION HAS A DATA FOLDER, ITS A COLLECTION. ELSE NOT.
        all_files_in_collection = glob.glob(collection+"/*")

        if len(all_files_in_collection) > 2 and re.search('/data', all_files_in_collection[1]):
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

def get_all_time(df):
    for counter, collection in enumerate(df.collection_name.unique()):
        df_ = (df[df["collection_name"] == collection])

        xlabel = "Start of collection (after 2016 cleanup):{} | Last day of collection: {}".format(df_.file_date.min().strftime("%D"), df_.file_date.max().strftime("%D"))


        file_min = df_.file_size.min()
        file_max = df_.file_size.max()

        yaxis_counter = (file_max - file_min) / 5

        yaxis = np.arange(file_min, file_max + yaxis_counter, yaxis_counter )
        yaxis_labels = [convert_size(each_ytick) for each_ytick in yaxis]

        ax = df_.plot(x="file_date", y="file_size", title=collection, legend=False)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("File Size")
        ax.set_yticks(yaxis)
        ax.set_yticklabels(yaxis_labels)

def get_last_week(df):
    recently_stopped_collecting = []
    not_actively_collecting = []

    for counter, collection in enumerate(df.collection_name.unique()):
        df_ = (df[df["collection_name"] == collection])
        days_since_last_collection = ((datetime.now() - df_.file_date.max()).days)

        if days_since_last_collection > 9:
            not_actively_collecting.append([collection, days_since_last_collection])
        elif days_since_last_collection > 3:
            recently_stopped_collecting.append([collection, days_since_last_collection])


        if (not any(collection in sublist for sublist in not_actively_collecting) and not any(collection in sublist for sublist in recently_stopped_collecting)):
            xlabel = "Start of collection (after 2016 cleanup):{} | Last day of collection: {}".format(df_.file_date.min().strftime("%D"), df_.file_date.max().strftime("%D"))

            data_past_week = (df_.sort_values(by="file_date", ascending=False)[:7]).sort_values(by="file_date", ascending=True)

            file_min = data_past_week.file_size.min()
            file_max = data_past_week.file_size.max()

            yaxis_counter = (file_max - file_min) / 5

            yaxis = np.arange(file_min, file_max + yaxis_counter, yaxis_counter )
            yaxis_labels = [convert_size(each_ytick) for each_ytick in yaxis]

            ax = data_past_week.plot(x="file_date", y="file_size", title=collection, legend=False)
            ax.set_xlabel(xlabel)
            ax.set_ylabel("File Size")

            ax.set_yticks(yaxis)
            ax.set_yticklabels(yaxis_labels)

        ## CLEAN UP INTO METHOD???
        rdrive = "smapp-drive"

        gdrive = '{}:SMaPP_2017/SMAPP_ALL_MEMBERS/Documentation/Collection_Charts'.format(rdrive)
        gdrive_archive = os.path.join(gdrive, 'z_Archive')


    #         ##save to jpeg
        fig = ax.get_figure()
        clean_collection_name = re.sub(' ', '-',  df_.collection_name.iloc[0])
        save_file_name = clean_collection_name + '_' + datetime.now().strftime("%m-%d-%Y")
        fig.savefig('/scratch/olympus/collection_charts/{}'.format(save_file_name), bbox_inches="tight")

        collection_charts_path = '/scratch/olympus/collection_charts/'
        save_file_path = '/scratch/olympus/collection_charts/{}.png'.format(save_file_name)
        archive_file_path = '/scratch/olympus/collection_charts/archive/{}.png'.format(save_file_name)


        chown(collection_charts_path, group="smapp")

        #copy the file into the archive.
        copyfile(save_file_path, archive_file_path)

        rclone(save_file_path, gdrive)
        rclone(archive_file_path, gdrive_archive)


            ## TURN INTO PDF AND SEND??
    print("These {} collections have recently stopped collecting:".format(len(recently_stopped_collecting)))

    for collection in recently_stopped_collecting:
        print("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))
    print('\n')


    print("These {} collections are no longer active:".format(len(not_actively_collecting)))
    for collection in not_actively_collecting:
        print("\t{}: has not been collecting for {} days".format(collection[0], collection[1]))


def main():
    total_collections = get_total_collections()
    df = pd.DataFrame(total_collections)

    get_all_time(df)
    get_last_week(df)

main()

