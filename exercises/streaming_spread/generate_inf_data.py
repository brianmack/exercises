""" Imitate a data stream of infinite length:

python generate_inf_data.py | python time_weight.py

"""

import random
import sys
import time

import time_weight

SEED = None

MIN_SPREAD = 0.0001
MAX_SPREAD = 0.0100
def start():
    """ Generates records in ts,side,price\n format."""
    
    if SEED:
        random.seed(SEED)

    while True:

        # sleep for multiple seconds sometimes
        if random.random() > 0.98:
            time.sleep(random.uniform(1., 3.))
        
        # a fractional second wait time, skewed 
        # toward small fractions
        time.sleep(random.paretovariate(alpha=5) / 10.)
        t = time_weight.sec_to_microsec(time.time())
        
        bid_p = 1 + random.random()
        ask_p = bid_p + random.uniform(MIN_SPREAD, MAX_SPREAD)
        
        ask_str = "%0.f,%s,%.5f\n" % (t, ":a", ask_p)
        bid_str = "%0.f,%s,%.5f\n" % (t, ":b", bid_p)
        
        sys.stdout.write(ask_str + bid_str)
        sys.stdout.flush()


if __name__ == "__main__":
    start()
