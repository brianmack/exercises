
import logging
import multiprocessing as mp
import traceback
from math import ceil


class Process(mp.Process):
    """ Improved mp.Process that sends errors back to parent
    via a queue."""

    def __init__(self, id_, q, target, args):
        """
        Inputs:
            id_: some process id to keep track of this process,
                not necessarily the os.pid
            q: a queue back to the parent process.
            target: function to execute in the child process
            args: arguments to target
        """
        mp.Process.__init__(self, target=target, args=args)
        self._exception = None
        self.q = q
        self._id = id_

    def run(self):
        try:
            mp.Process.run(self)
            self.q.put((0, self.__id))
        except Exception as e:
            tb = traceback.format_exc()
            self.q.put((e, tb))
            # raise 3

    #@property
    #def exception(self):
    #    if self._pconn.poll():
    #        self._exception = self._pconn.recv()
    #    return self._exception


def argtype(arg):
    """ The mp.Process expects the generic arguments passed
    to its 'target' function to be in a tuple.  This wrapper
    performs checking on the arguments input."""

    if isinstance(arg, (list, tuple)):
        return arg
    else:
        return (arg, )


def map_(func, arg_list, njob, nproc):
    """ Custom allocation of tasks.  Takes a queue of
    tasks to run and chunks them out.
    Inputs:
        func: callable
        arg_list: sets of args to send to each process,
            can be a generator
        njob: number of jobs
        nproc: number of processes to spawn
    Allocate 'arg_list' across 'nproc'.
    """

    # I'm always going to forget to pass an iterator
    if not hasattr(arg_list, "next"):
        arg_list = iter(arg_list)

    manager = mp.Manager()
    multi_q = manager.Queue(maxsize=nproc)

    # first, allocate jobs across all available processes
    procs = {}
    while njob and nproc:

        id_ = njob
        args = arg_list.next()
        proc = Process(id_=id_, q=multi_q, target=func,
            args=argtype(args))
        proc.start()
        procs[id_] = proc
        nproc -= 1
        njob -= 1

    # allocate the rest of the jobs as procs become available
    while njob:
        status, info = multi_q.get()
        if status == 0:
            id_ = info
            procs[id_].terminate()

            proc = Process(id_=id_, q=multi_q, target=func,
                args=argtype(args))
            proc.start()
            procs[id_] = proc
            njob -= 1
        else: # error sequence
            logging.error(str(info))
            cleanup_procs(procs)
            raise status

    # finally wait for all to finish
    while procs:
        status, info = multi_q.get()
        if status == 0:
            id_ = info
            procs[id_].termainte()
            del procs[id_]
        else:
            logging.error(str(info))
            cleanup_procs(procs)
            raise status


def cleanup_procs(procs):
    """ In the error scenario, we want to kill all child procsesses.
    Input:
        procs: dictionary of objects like:
            { <pid1> : proc, <pid2> : proc }
    """
    for k in procs:
        procs[k].terminate()


def test_target(x):
    """ Simulate actual behavior of child processes with random
    error-ing.  Should see the stack trace when error happens."""

    from random import sample
    import time

    print "running value %s" % str(x)

    var = [0] * 10
    var[0] = 1
    do_error = sample(var, 1)[0]
    time.sleep(1)
    if do_error:
        raise ValueError("target did an error on value %s" % str(x))

    return 0

if __name__ == "__main__":

    map_(
        func=test_target,
        arg_list=iter(range(30)),
        njob=30, # 95.8% of the time there will be an error
        nproc=6)
    print "completed with no errors - run again to trigger an error"
