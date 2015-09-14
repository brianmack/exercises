""" Function to compute max draw down.
To run:
python max_drawdown.py

Brian Mack
"""

import logging

# Change to level=logging.DEBUG for verbose output
logging.basicConfig(level=logging.INFO)

def max_drawdown(daily_returns):
    """ Calculates the maximum peak-to-trough drawdown,
    ignoring any potential compounding issues.
    Input:
        daily_returns: iterable (float):
            contains daily return values.
    Returns:
        max_drawdown: float:
            largest peak-to-trough in left-to-right order
    """

    err_msg = (
        "value for arg 'daily_returns' must be a list or tuple, not %s" 
        % str(type(daily_returns)))
    assert isinstance(daily_returns, (list, tuple)), err_msg

    # this cast to float ensures that all elements in daily_returns will
    # also be floats, since they are all mediated through the 'this_value'
    # var.
    current_peak = this_value = this_drawdown = max_drawdown = 0.
    logging.debug(
        "returns, daily_return, current_peak, this_drawdown, max_drawdown")
    
    for i in xrange(len(daily_returns)):
        this_value += daily_returns[i]
        logging.debug("%.2f, %.2f, %.2f, %.2f, %.2f" 
            % (this_value, daily_returns[i], current_peak, 
            this_drawdown, max_drawdown))
        # is it a new peak?
        if this_value > current_peak:
            current_peak = this_value
        
        # get current drawdown and compare to max
        else:
            this_drawdown = current_peak - this_value
            if this_drawdown > max_drawdown:
                max_drawdown = this_drawdown        
            
    
    logging.debug("%.2f, %.2f, %.2f, %.2f"
        % (this_value, current_peak, this_drawdown, max_drawdown))
    return -max_drawdown


if __name__=="__main__":
    print "running different daily return lists:"
    test_lists = [
        [1.0, 2.1, -3.0, 1.0, -1.5, 4.5, -2.0],
        [50, -60, 30, -40, 120],
        [1, -1],
        [1, 1, 1, 1, 1],
        3,
        [3]
    ]
    for i in range(len(test_lists)):
        list_returns = test_lists[i]
        try:
            max_dd = max_drawdown(list_returns)
            print "test list %i: max drawdown is %s" % (i, str(max_dd))
        except AssertionError as e:
            logging.error("test list %i: %s" % (i, str(e)))
