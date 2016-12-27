"""
Process a file 'data.csv' as a stream, and compute the 
time weighted average spread on a per-second basis.

At the beginning of each second, the program should print
the time weighted average of the spread in effect for the
preceding second.

Assume data will come as a stream of infinite length.
The program should output exactly one average spread for
each second.

See attached README for details on invocations, or run
this script with the '-h' option.

Brian Mack
2016-06-01
"""



import io
import logging
import optparse
import stream_data
import sys
from math import floor


# for floating point stability
FLOAT_DIGITS = 8
OUTPUT_FORMAT = "%i,%." + str(FLOAT_DIGITS) + "f\n"

float_multiplier = 1


# import config or configure file indexes here
microsec_to_sec = lambda x: x / 1000000.0
sec_to_microsec = lambda x: x * 1000000.0



def getopt(argv):
    
    parser = optparse.OptionParser()

    parser.add_option(
        "-f", "--path",
        default=None, dest="fname",
        help="file name to open, otherwise stdin")
    parser.add_option(
        "-d", "--delimiter",
        default=",", dest="delimiter",
        help="field delimiter for input stream")
    parser.add_option(
        "-1", "--header",
        default=False, dest="header",
        action="store_true",
        help="source has header line - discard")

    options, _ = parser.parse_args()
    return options


class InputError(Exception):
    """ For non gracefully handled errors, to be defensive
    about working with timestamps.
    """
    pass


class QuoteError(Exception):
    """ Error manager for QuotePair class - used for 
    catching and logging various errors that can occur in the
    input data, including unpaired quotes, and duplicate
    records per time stamp.  For now these can be given as
    strings when the exception is raised.
    """
    pass


class QuotePair(object):
    """ Manages comparison of price quotes with time stamps,
    including error handling for un-paired quotes and book-
    keeping esp:
    
        1) Returns time (in seconds) from previous quote,
            if new quote
        2) Tracks bids and asks, and their time stamps
    
    Functions like a very simple cache with only one method (add)
    """

    def __init__(self):
        self.current_ts = None
        self.ask = None
        self.bid = None


    def _update_quote(self, side, price):
        """
        Inputs:
            new: (bool) signals whether it's okay to overwrite a price
        """
        
        if side == ":a":
            if self.ask is not None:
                raise QuoteError("ask was already set at %.2f, "
                    "received %.2f" % (self.ask, price))
            self.ask = price
        
        if side == ":b":
            if self.bid is not None:
                raise QuoteError("bid was already set at %.2f, "
                    "received %.2f" % (self.bid, price))
            self.bid = price


    def _clear_prices(self):
        self.ask = None
        self.bid = None


    def add(self, ts, side, price):
        
        if not isinstance(ts, float):
            raise InputError("QuotePair needs float value for timestamp, "
                "not %s" % type(ts))

        if side != ":a" and side != ":b":
            raise InputError("QuotePair side must be :a or :b, not %s" 
                % str(side))
        
        if not isinstance(price, float):
            raise InputError("QuotePair needs float value for price, "
                "not %s" % type(price))

        # first, is this a new timestamp? 
        if self.current_ts is None:
            self.current_ts = ts
            new_time = 0
        else:
            new_time = ts - self.current_ts
        
        # if yes, make sure you were done with previous
        if new_time:
            if self.ask is None or self.bid is None:
                raise QuoteError("Received price for new timestamp before "
                    "I was done with the previous")
            self._clear_prices()

        # make sure it's not a duplicate record
        # (although duplicates wouldn't hurt anything)
        else:        
            if self.ask and self.bid:
                raise QuoteError("Received more than one pair of records "
                    "for a single time stamp")
        
        self._update_quote(side, price)

        self.current_ts = ts
        if self.ask and self.bid:
            spread = self.ask - self.bid
            #if spread < -0.000000001:
            #    raise QuoteError("Spread < 0: %.2f (a: %.8f, b: %.8f)" 
            #        % (spread, self.ask, self.bid))
            return spread
        
        return


class TimeCache(object):
    """ This class handles time weighted averaging of quote pairs.
    It's job is to store data (sparsely) at 1-second intervals,
    as well as any partial data about the current second.
    """
    
    def __init__(self):
        
        # will contain all whole-seconds in sorted order 
        # and weighted spreads
        self.archive = []

        # need to also store most recent given spread (not weighted)
        self.last_spread = None
        
        # will contain partial data for leading edge of data stream
        self.tmp_cache = []
    

    def _get_spreads_and_time_weights(self):
        """ Collect spreads and their durations (in fractions of a 
        second) for all elements in short term cache.  
        
        For first data record (cold medium term cache),
        no spread is given for the partial second between record 1
        timestamp and floor(record 1 timestamp) ... (the nearest 
        previous whole second).  Excludes that from time weighting
        of initial step.

        For all records: weight spread by fraction of second 
        during which spread was active.  A spread is 'active' 
        from the time of the record to which it's attached
        until the time of the next record.  If the next record is
        in a new whole second, compute duration from the current
        timestamp to the end of the current whole second.
        """

        # initialize arrays
        spreads = []
        time_weights = []
        
        # don't use first segment in computation for this second
        if self.last_spread is not None:

            # if any time gap between last archive and first
            # record in current cache, fill that in here
            first_spread = self.last_spread
            first_time = time_i = self.tmp_cache[0][0] - self.archive[-1][0]
            spreads = [first_spread]
            time_weights = [first_time]
        i = 1

        # fill out main part of arrays
        while i < len(self.tmp_cache):
            spread_i = self.tmp_cache[i-1][1]
            time_i = (
                self.tmp_cache[i][0] - 
                self.tmp_cache[i-1][0])
            spreads.append(spread_i)
            time_weights.append(time_i)
            i += 1
        
        # finally, handle any gaps between last record in cache
        # and the next full second
        spreads.append(self.tmp_cache[i-1][1])

        time_weights.append(
            self.archive[-1][0] + 
            float_multiplier - 
            self.tmp_cache[i-1][0])
        
        return spreads, time_weights


    def _weight_time(self, spreads, time_weights):

        twa = 0.0
        time_sum = 0.0
        for i in range(len(spreads)):
            twa += spreads[i] * time_weights[i]
            time_sum += time_weights[i]

        return round(twa / time_sum, 8) # normalize for short seconds


    def _get_last_archive_ts(self):
        """ Return timestamp of most recent archive record."""
        return self.archive[-1][0]


    def _cold_cache(self, ts, spread):
        """ Does special cache warming logic: We need one archive record
        containing the whole-second timestamp which is previous to the
        first record in our stream.  This will be used later in the 
        time weighting step.  We also append the first record to the 
        temporary store.
        Inputs:
            ts: (float) record timestamp
            spread: (float) spread at this timestamp
        Returns:
            (bool):  Yes if the cache was cold
        """
        
        # fill if empty
        if not len(self.tmp_cache):
            self.tmp_cache.append((ts, spread))

            # true for first ever record 
            if not len(self.archive):
                self.archive = [(floor(ts), None)]
                return 1
        else:
            return 0
   
    def _update_archive(self, ts, spread):
        """ The archive is maintained so that it's always up to 
        the same second of data as the current time, so compute
        the time weighted second of the second-span directly
        after the archive record, and then propagate forward to
        current ts.
        Inputs:
            ts: (float) record timestamp
            spread: (float) spread tied to 'ts'
        Returns:
            None -- updates archive and cache
        """

        spreads, times = self._get_spreads_and_time_weights()
        twa = self._weight_time(spreads, times)
        archive_floor = floor(ts)
        
        self.archive.append((archive_floor, twa))
        self.last_spread = self.tmp_cache[-1][1]

        # start a new current time data section
        self.tmp_cache = [(ts, spread)]

    
    def add(self, ts, spread):
        """ Add records to cache:  Maintains two ledgers -- one short
        term for the leading edge intra-second spreads, and oen medium 
        term for time-weighted spreads over whole seconds.  Both are 
        memory efficient in the sense that they are cleared when data
        has been promoted and can handle streams of infinite length.
        Inputs:
            ts: record timestamp
            spread: spread tied to 'ts'
        Returns:
            (bool) Yes if short term cache is full, as an indicator
            that there are new, whole-second records to log.
        """

        if not isinstance(ts, float):
            raise InputError("TimeCache needs timestamps as float, "
                "not %s" % type(ts))
        
        if not isinstance(spread, float):
            raise InputError("TimeCache needs spreads as float, "
                "not %s" % type(spread))

        if self._cold_cache(ts, spread) == 1:
            # first piece of data, load attributes only, 
            # nothing to log
            return

        duration = ts - self._get_last_archive_ts()
        if duration > 1.0:
            self._update_archive(ts, spread)
            return 1
        
        self.tmp_cache.append((ts, spread))
        return 0
            
    
    def log(self):
        """ Print a record for each whole-second between now and
        last logged record.  Make last second the new last logged
        record.
        """
        
        last_logged_ts = self.archive[0][0] + 1
        for i, data in enumerate(self.archive):
            if i == 0:
                # this was logged last time
                continue
            this_ts = self.archive[i][0]
            price = self.archive[i-1][1]
            while last_logged_ts < this_ts and price is not None:
                sys.stdout.write(OUTPUT_FORMAT % (
                    int(sec_to_microsec(last_logged_ts)), 
                    price))
                last_logged_ts += 1
            
        sys.stdout.write(OUTPUT_FORMAT % (
            int(sec_to_microsec(this_ts)), 
            self.archive[i][1]))

        self.archive = [self.archive[-1]]


def compute_twa(f, delimiter=","):
    """ Read records from stream, and log outputs on the fly.
    Inputs:
        f: object with iterator protocol (next method and 
            StopIteration error when exhausted).  Contains
            one record per line of the form:
                timestmap, quote side, price
    Returns:
        (stdout) one line for each whole second in input, with
            time-weighted prices per whole second.
    """
    
    pair_cache = QuotePair()
    time_cache = TimeCache()
    
    stream = stream_data.stream(f)
    for line in stream:
        ts, side, price = line.strip().split(delimiter)
        
        ts = microsec_to_sec(float(ts))
        price = float(price)

        ts *= float_multiplier
        price *= float_multiplier
        
        try:
            spread = pair_cache.add(ts, side, price)
        except QuoteError as e:
            logging.warning("input error: %s, %s" 
                % (line.strip(), str(e)))
            continue
        
        if spread is not None:
            log_ready = time_cache.add(ts, spread)
            if log_ready:
                time_cache.log()        
    
    if len(time_cache.tmp_cache):
        logging.info("dropped %i records for incomplete "
            "full-second at the end of the stream between "
            "timestamps %.2f and %.2f." % (len(time_cache.tmp_cache),
            time_cache.tmp_cache[0][0], time_cache.tmp_cache[-1][0]
        )) 
    
    #TODO we could have a concept of logging records at the end
    # of a stream that are for a partial second.


def main(options):
    
    # open file if given else default to stdin
    if options.fname:
        file_ = open(options.fname)
        
    else:
        file_ = sys.stdin
        
    # burn one line
    if options.header:
        file_.readline()

    # defaults to ,
    delimiter = options.delimiter
    
    compute_twa(file_, delimiter)


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)
    opts = getopt(sys.argv)
    main(opts)
