from concurrent.futures import ProcessPoolExecutor as PoolExecutor
import os
from os import listdir
from os.path import isfile, join
from time import time, sleep
import shutil
import logging
import mmap,re
from pprint import pformat
from collections import defaultdict
from operator import itemgetter, attrgetter
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_set_up():
    input_dir_name = "input"
    output_dir_name = "output"
    if not os.path.exists(os.path.join(Path.home(), input_dir_name)):
        try:
            os.makedirs(os.path.join(Path.home(), input_dir_name))
        except:
            logging.CRITICAL("Cannot create the input directory under HOME.Exiting")
            quit()

    if not os.path.exists(os.path.join(Path.home(), output_dir_name)):
        try:
            os.makedirs(os.path.join(Path.home(), 'output'))
        except:
            logging.CRITICAL("Cannot create the input directory under HOME.Exiting")
            quit()

    global input_path, output_path
    input_path= os.path.join(os.path.join(Path.home(), input_dir_name))
    output_path = os.path.join(os.path.join(Path.home(), output_dir_name))

# Main function which runs an infinite and creates worker processes for concurrent processing of files. Each worker from here call
#read_file function which take cares of processing of the respective.

def main():
    create_set_up()
    max_workers = 5
    start = time()

    logging.info("Starting log parsing Daemon.This Daemon processes logs file from {} & moves them to {} after completing".\
                 format(input_path, output_path))
    while True:
            files_to_process = [join(input_path,f) for f in listdir(input_path) if isfile(join(input_path, f))]

            if not files_to_process:
                logging.info("Daemon is waiting for the new files")
                sleep(5)
                #break
            else:
                start = time()
                logging.info("Daemon will spawn {} workers for concurrently processing of files".format(max_workers) )
                with PoolExecutor(max_workers) as executor:
                    for _ in executor.map(read_file, files_to_process):
                        try:
                            # mv_start = time()
                            logging.debug("File processing finished and now moving the file {} to {}".format(_, output_path))
                            # os.path.basename(_), output_path))
                            shutil.move(_, os.path.join(output_path), os.path.basename(_))
                            # mv_end = time()
                        except OSError as e:
                            logging.error(
                                "Not able to move files {}. Daemon will keep re-trying and will process any new files".format(
                                    e))

                    end = time()
                    logging.info("Total processing time was {}".format(end - start))
                    logging.info("PoolExecutor finished the current batch and now moving them to output")

def search_errors(line):
        matched = re.match(r'\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\dZ \[(\w+-\w+)\s+([a-z0-9A-Z]*)\]:.*\[error\].*',(line.decode("utf-8")))
        if matched:
            match_this = matched.group(1, 2)
            return match_this

##### This function receives the filename from each worker process, iterates over it using mmap utility and passes the line to search_errors function


def read_file(filename):
    logging.info("STARTED processing {} file".format(filename))
    svclist = []
    with open(filename, 'r+b') as f:
        map_file = mmap.mmap(f.fileno(), 0)
        for line in iter(map_file.readline, b""):
            ret = search_errors(line)
            if ret is not None:
                svclist.append(ret)
        map_file.close()
        # map_file = mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
        # ret = search_errors(map_file.read(-1))
        # if ret is not None:
        #     svclist.append(ret)
        # map_file.close()
    get_output(svclist, filename)
    return filename


## This function calculates and prints the details of error per service name and and also the service instance with maximum error

def get_output(svclist, filename):
    svc_with_max_error = {}
    x = itemgetter(0, 1)
    s_i = defaultdict(int)

    for svc in svclist:
        key = x(svc)
        s_i[key] += 1

    for s in s_i:
        try:
            if s[0] not in svc_with_max_error.keys():
                svc_with_max_error[s[0]] = s_i[s]
            elif s_i[s] > svc_with_max_error[s[0]]:
                svc_with_max_error[s[0]] = s_i[s]
        except KeyError:
            svc_with_max_error.setdefault(s[0], s_i[s])

    x = itemgetter(0)
    s = defaultdict(int)
    for svc in svclist:
        key = x(svc)
        s[key] += 1

    logging.info("List of error count from {} by Service is {}".format(filename, pformat(s)))
    #logging.info("List of error count from {} grouped by service and instance is {}".format(filename, pformat(s_i)))
    logging.info("Maximum errors for each service is {}".format(pformat(svc_with_max_error)))
    logging.info("ENDED processing of {} file".format(filename))

if __name__ == '__main__':
    main()












