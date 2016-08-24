""" Module to write to many files from many processes, where
possibly many processes would want to access the same file at
the same time.

Each child process would put a request (0/1) for a specific 
file into an input queue, and listen / block on an output queue
for permission to write to that file.  All child processes
work concurrently as long as the same file is not requested
at the same time.

The use case here was to have child processes acting on input
files, and to do special logging on those files based on the
record-level ID on each line of many files.  When the files were
known to be in ID-sorted order and there were N processes, 
then in general there would only be blocking during the 
requests for the first N ids (assuming all files contained most
ids).

"""


import logging
import multiprocessing
import Queue
import random

MAX_QLEN = 100

def master(q_in, q_dict):   
    """
    Inputs:
        q_in: listening queue from worker processes to master
        q_dict: table of pid's and corresponding queues from master
            to worker
    """


    access_dict = {}
    fq = Queue.Queue()
    while True:
        
        message = q_in.get()
        if message == "kill":
            break # kill proc

        # id is the file id, pid is the id of sender, and request
        # is boolean
        id_, pid, request = message
        if request == 1: # requests access
            # Proces A requests access to id_1.  Master sees that 
            # the access table is clear for its requested item and 
            # sends an okay back to process A through A's special
            # output queue.  If some other process Z had already had 
            # access to id_1, then process A's request would be placed 
            # in a queue for id_1, and process A would block until it's
            # turn comes up and it finally receives the okay signal.  
            # This happens when process Z sends a release request which 
            # is processed, and then the next process in line gets the
            # okay signal (see else condition below).
        if id_ not in access_dict:
            # initialize waitlist
            access_dict[id_] = Queue.Queue()
            q_dict[pid].put(1)

        else:
            # queue exists which indicates key in use, add pid to waitlist
            access_dict[id_].put(pid)

    else: # requests release
        # Here, process A has signaled that it's done with id_1, so we
        # get the next process in line (process B).  We then send a signal
        # to process B that it's okay to start working.  By now, process A
        # has put another request on the queue for its next file id.  If
        # nobody was waiting in line for id_1 (no process B), then we 
        # delete the key and its wait-list, which signals its availability
        # to any downstream requests.

        if access_dict[id_].empty():
            # any future requests will see a blank entry and proceed,
            # since lack of key indicates availability.
            del access_dict[id_]
        else:
            # let in the next person in line
            pid = access_dict[id_].get()
            q_dict[pid].put(1) # signal that next is clear to proceed



