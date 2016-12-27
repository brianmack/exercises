
import cStringIO
import datetime
import logging
import pprint
import sys
import time
import unittest
from multiprocessing import Process

import generate_inf_data
import stream_data
import time_weight


TEST_DATA_FNAME = "test_data.csv"

class TestTimestamp(unittest.TestCase):
    """ Tests for working with microsecond timestamps."""

    TIME_TS = 1471706838.952891 # time.time()
    TS_HEAD = 1469404799897461
    TS_TAIL = 1469405999873655

    # time.ctime() of start / end timestamp shows:
    # 'Sun Jul 24 19:59:59 2016'
    # 'Sun Jul 24 20:19:59 2016'
    MINUTES_OF_DATA = 20.

    def test_second_conversion(self):

        ts_head = time_weight.microsec_to_sec(self.TS_HEAD)
        ts_tail = time_weight.microsec_to_sec(self.TS_TAIL)
        
        #print ts_head, ts_tail

        d_head = datetime.datetime.utcfromtimestamp(ts_head)
        d_tail = datetime.datetime.utcfromtimestamp(ts_tail)

        #print d_head, d_tail
        # conversion ratio is correct if year is reasonable
        # looking ...
        self.assertTrue(d_head.year == 2016)          
        self.assertTrue(d_tail.year == 2016)
        self.assertTrue(
            round((d_tail - d_head).seconds / 60.) == self.MINUTES_OF_DATA)
        
        self.assertTrue(
            round(ts_tail - ts_head) == (self.MINUTES_OF_DATA * 60))

    

class TestQuotePair(unittest.TestCase):
    
    def test_update_quote(self):
        """ Ensure proper pairing of matched a/b records."""

        pair_cache = time_weight.QuotePair()
        pair_cache._update_quote(":b", 42.)
        self.assertTrue(pair_cache.bid == 42.)
        
        pair_cache._update_quote(":a", 58.)
        self.assertTrue(pair_cache.ask == 58.)

        pair_cache._clear_prices()
        self.assertTrue(pair_cache.bid is None)
        self.assertTrue(pair_cache.ask is None)


    def test_add(self):
        """ Test all corner cases of a/b pairing."""

        pair_cache = time_weight.QuotePair()
        
        # does not accept timestamps as str type
        self.assertRaises(time_weight.InputError,
            pair_cache.add, "1469404799897461", ":b", 42.)

        # does not accept price as str type
        self.assertRaises(time_weight.InputError,
            pair_cache.add, 1469404799.897461, ":b", "42.")
        
        # returns None if a pair isn't made yet
        value = pair_cache.add(1469404799.897461, ":b", 42.)
        self.assertTrue(value is None)

        # throws error if new time value is added before previous
        # is paired
        self.assertRaises(time_weight.QuoteError,
            pair_cache.add, 1469404799.898461, ":a", 43.)
        
        # throws error if duplicate price side is set
        self.assertRaises(time_weight.QuoteError,
            pair_cache.add, 1469404799.897461, ":b", 42.)
        
        # returns the spread if bid and ask records are paired 
        value = pair_cache.add(1469404799.897461, ":a", 43.)
        self.assertTrue(value == 1.0)
        self.assertTrue(pair_cache.current_ts == 1469404799.897461)
        
        self.assertRaises(time_weight.QuoteError,
            pair_cache.add, 1469404799.897461, ":a", 43.)


class TestTimeCache(unittest.TestCase):
    
    def test_init(self):
        """ Does this test suite agree about the initialization
        state of the TimeCache class?
        """
        tc = time_weight.TimeCache()
        self.assertTrue(tc.archive == [])
        self.assertTrue(tc.last_spread is None)
        self.assertTrue(tc.tmp_cache == [])

    def test_initial_conditions(self):
        """ Test cold cache."""

        tc = time_weight.TimeCache()
        # first, see that it loads an initial archive state
        # correctly
        tc._cold_cache(1469404800.100000, 10.)
        self.assertTrue(tc.tmp_cache == [(1469404800.100000, 10.)])
        self.assertTrue(tc.archive == [
            (1469404800.000000, None),
            ])
        self.assertTrue(tc.last_spread is None)

    
    def test_weight_time(self):

        # First Case:  time weight of incomplete second
        tc = time_weight.TimeCache()
        tc.archive = [(1469404800.000000, None)]
        tc.tmp_cache = [
            (1469404800.200000, 0.000010), # first record in data
            (1469404800.600000, 0.000020), # second...
            ]
        tc.last_spread = None

        spreads, times = tc._get_spreads_and_time_weights()
        twa = tc._weight_time(spreads, times)
        self.assertTrue(round(twa, 8) == 0.000015)


    def test_add_and_log(self):
        
        tc = time_weight.TimeCache()
        qc = time_weight.QuotePair()

        data = [
            (800.200000, ":b", 1.50),
            (800.200000, ":a", 1.60), # 10
            (800.600000, ":b", 1.75),
            (800.600000, ":a", 1.95), # 20
            (801.500000, ":b", 1.80),
            (801.500000, ":a", 1.90), # 10
            (803.300000, ":b", 1.13),
            (803.300000, ":a", 1.28), # 15
            (804.200000, ":b", 1.01),
            (804.200000, ":a", 1.11), # 10
            ]
        
        for ts, side, price in data:
            ts *= time_weight.float_multiplier
            price *= time_weight.float_multiplier
            spread = qc.add(ts, side, price)
            if spread is not None:
                tc.add(ts, spread)

        # archive contains correctly computed time weighted
        # averages
        self.assertTrue(tc.archive == [
            (800.000000, None),
            (801.000000, 0.15),
            (803.000000, 0.15),
            (804.000000, 0.135),  # 10 * .3 + 15 * .7
            ])
        
        # buffer stdout momentarily
        sys.stdout = cStringIO.StringIO()
        tc.log()
        
        s = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        
        # logger should have oen record for each second, 
        # including the gap second between inputs
        # note -- will fail if you change the precision
        # of the output in time_weight.py
        self.assertEqual(s,
            "801000000,0.15000000\n"
            "802000000,0.15000000\n"
            "803000000,0.15000000\n"
            "804000000,0.13500000\n")


    #TODO Test for safety against other implementations -- what if 
    # records are not written at each new whole second?



class TestStreamData(unittest.TestCase):

    
    def test_readlines(self):
        """ Does it wrap a file correctly and stop when done?
        """
        file_ = open("test_lines.txt")
        f = stream_data.stream(file_)
        line_ct = 0
        for line in f:
            line_ct += 1
        self.assertTrue(line_ct == 3)

    
    def test_generator(self):
        """ Run generator for a time period and count output.
        """
        
        tmp_fname = "test_gen_dump.tmp"
        generate_inf_data.SEED = "123"
        generate_inf_data.sys.stdout = open(tmp_fname, "w")
        
        logging.info("running data generator")
        proc = Process(target=generate_inf_data.start)
        
        proc.start()
        time.sleep(0.5)
        proc.terminate()
        
        generate_inf_data.sys.stdout.close()
        generate_inf_data.sys.stdout = sys.__stdout__

        tmp_f = open(tmp_fname)
        lines = tmp_f.readlines()
        tmp_f.close()

        self.assertTrue(len(lines) == 8)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(buffer=False)
