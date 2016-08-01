""" 
--------------
Exercise:
--------------

Write a program that can compute the number of unique and valid
phone numbers with the following constraints:

    1. A valid phone number is seven digits in length
    2. A valid phone number cannot begin with a 0 or 1
    3. A valid phone number can contain only digits
    4. A valid phone number must consist of a sequence of digits that
        can be traced by the movements of a chess piece on a normal
        telephone keypad

Implement for the knight chess piece. Compute the number of all unique, 
valid phone numbers.  Also be able to build correct phone numbers.


--------------
Documentation:
--------------

Depencies:  numpy

To run this module:
python compute_valid_phone_numbers.py


This module contains three main parts:
    1. Movements for different kinds of chess pieces, and special rules
        for creating them.
    2. A class 'ChessPiece' that translates the board (a phone key pad)
        and rules for chess piece movement into a graph (mapping of
        starting squares on the key pad to legal landing squares).
    3. A function 'compute_phone_numbers' for building valid phone numbers
        from this graph.

Rules for movement:
At the heart of this module is a syntax for defining piece movement.
Chess pieces may move some distance laterally or diagonally in any
direction.  Our rules specify movement by considering the matrix-like
indices of some starting position on a phone key pad.  To get to any
other position on the pad, we only need to increment our current indices
in the desired direction some variable number of times.  So we can
encode a rule with three parameters encoded in an iterable data structure
like:
    
    (
        <how many i indices to move at a time>,
        <how many j indices to move at a time>,
        <repeat i and j moves this many times> (iterable)
    ), ...

For the bishop, we would specify:
    
    (1, 1, (1, 2, 3))

The bishop moves diagonally by incrementing the i and j indices at the
same time, and may choose to take up to min(i, j) steps - in this case,
1, 2, or 3 steps.

When specifying a rule, we only need to consider positive increments to
indices.  This code automatically attempts to move in other directions by
reversing the signs e.g. (-1, -1), (-1, 1) ... see the function 'expand_rule'.  
Any movements that 'fall off the key pad' are invalid and will not be
included.

I implemented a few test cases below, and any piece can be specified by
changing the DO_PIECE module-level variable.

Brian Mack
"""

import numpy
import logging
import pprint


# Change to level=logging.DEBUG for verbose output
logging.basicConfig(level=logging.INFO)

# Example pieces
knight_movements = (
        (2, 1, (1,)),
        (1, 2, (1,))
    )
bishop_movements = (
        (1, 1, (1, 2, 3)),
    )
rook_movements = (
        (1, 0, (1, 2, 3, 4)),
        (0, 1, (1, 2, 3, 4))
    )
queen_movements = (
        (1, 1, (1, 2, 3)),
        (1, 0, (1, 2, 3, 4)),
        (0, 1, (1, 2, 3, 4))
    )
king_movements = (
        (1, 1, (1,)),
        (1, 0, (1,)),
        (0, 1, (1,))
    )
PIECES = {
    "knight" : knight_movements,
    "bishop" : bishop_movements,
    "rook" : rook_movements,
    "queen" : queen_movements,
    "king" : king_movements
}

# Matrix representation of a keypad.
keypad = numpy.reshape(list("123456789*0#"), (4,3))

def string_set_from_range(n1, n2=None):
    """ Acts like the 'range' function, but returns strings
    instead of integers, and puts them into a set instead of
    a list.
    Inputs:
        n1: first number in range.  If arg 'n2' is not provided,
            n1 will act as the upper limit on the range as in 
            0:n1
        n2: (optional) last number in range.  If provided, creates
            range as in n1:n2
    Returns:
        set of strings
    """
    if n2:
        range_ = range(n1, n2)
    else:
        range_ = range(n1)
    return set([str(x) for x in range_])


""" Encodes constraints that define a valid phone number as follows:

    length: A valid phone number is seven digits in length
    valid_keys: A valid phone number can contain only digits
    valid_start_keys: A valid phone number cannot begin with a 0 or 1
    
The constraint that a phone number must consist of digits that can
be traced by the movements of a chess piece is implicit in this program
itself.
"""
valid_phone_number = {
    "length" : 7,
    "valid_keys" : string_set_from_range(10),
    "valid_start_keys" : string_set_from_range(2, 10)
}

class ChessPiece(object):
    """ Takes a set of rules as defined by one piece, and applies
    those rules to a Keypad to create a graph data structure with
    edges between nodes indicating which way squares are accessible
    to the piece from any given starting key on the pad."""

    def __init__(self, Keypad, phone_number):
        self.keypad=Keypad
        self.phone_number=phone_number

    def attempt_one_move(self, end_keys, i, j):
        """ Try to do move on key pad.  If move is legal, add the 
        name of the landing square (indicated by indices on keypad i,j)
        to a list 'end_keys'.  If indices i and j are not on the
        keypad, do nothing.
        """
        try:
            k = self.keypad[i, j]
        except IndexError:
            return
        if k in self.phone_number["valid_keys"]:
            end_keys.append(k)

    def expand_rule(self, rule):
        """ Interpret a single rule to apply in any of four directions
        (make four rules out of one rule).
        Input:
            rule: iterable in form like (i, j, rep)
        Returns:
            list of rules.
        """
        i, j, reps = rule
        return [
            (i, j, reps), 
            (-i, j, reps), 
            (i, -j, reps),
            (-i, -j, reps)
        ]

    def attempt_moves(self, rule, i, j):
        """ Attempt as many moves as possible in one direction, subject
        to constraints defined in the provided rule.  The direction of 
        the move is pre-determined by the signs in the particular rule 
        provided.
        Input:
            rule: rule object of the form:
                (
                    <how many i indices to move at a time>,
                    <how many j indices to move at a time>,
                    <repeat i and j moves this many times> (iterable)
                ), ...
            i, j: current indices in self.keypad
        Returns;
            end_keys: list: keys to which it is legal to move.
        """
        end_keys = []
        inc_i, inc_j, nreps_list = rule
        for rep in nreps_list:
            tmp_i = i + (inc_i * rep)
            tmp_j = j + (inc_j * rep)

            # negative indices don't 'fall off' the matrix in python
            if tmp_i < 0 or tmp_j < 0:
                continue
            self.attempt_one_move(end_keys, i+(inc_i * rep), j+(inc_j * rep))
        
        logging.debug("%s, %s, %s, %i, %i" %
            (str(self.keypad[i,j]), str(end_keys), str(rule), i, j))
        return end_keys 

    def create_piece(self, rules):
        """ In this program, a chess piece is actually just a graph of
        possible movements given a key pad matrix and some constraints.
        This function creates that graph.
        Input:
            rules: 'list of lists'-type object containing rules
                (See note on rule definition above for more info.)
        Returns:
            piece: dict: graph of form:
                {
                    '1' : set([2, 3, 4, 7]), ...
                }
        """
        
        # walk the array (keypad) defining edges for each key according
        # to phone number constraints and movement rules
        rules = [self.expand_rule(rule) for rule in rules]
        piece = {}
        for i in range(self.keypad.shape[0]):
            for j in range(self.keypad.shape[1]):
                key = self.keypad[i, j]
                if key not in self.phone_number["valid_keys"]:
                    continue
                piece[key] = []
                for rule in rules:
                    for subrule in rule:
                        piece[key].extend(
                            self.attempt_moves(subrule, i, j))
                piece[key] = set(piece[key])
        return piece
                
def _move_piece(piece, partial_phone_number, this_level, max_level):
    """ Recursive function to create valid phone numbers.
    Input:
        piece: dict: mapping of current keys to valid next keys
        partial_phone_number: current concatenation of digits encountered
            during walk of chess-moves over keypad up to this_level
        this_level: current depth
        max_level: max length of phone number allowed (max depth)
    Returns:
        phone_numbers: list of valid phone numbers
    """

    # base case
    if this_level > max_level:
        # make list because we extend a list in this recursion
        return [partial_phone_number] 
    
    # recursion case
    phone_numbers = []
    last_key = partial_phone_number[-1]
    for key in piece[last_key]:
        phone_numbers.extend(
            _move_piece(piece, partial_phone_number + key,
                this_level + 1, max_level))
    
    return phone_numbers

def compute_phone_numbers(piece, phone_number_rules):
    """ Move chess piece over graph to create all combinations of
    possible phone numbers.
    Input:
        piece: dict: mapping of current keys to valid squares to move to
        phone_number_rules: movement constraints for piece, including
            valid start keys.
    Returns:
        list of valid phone numbers
    """
    phone_numbers = []
    
    for key in piece:
        if key not in phone_number_rules["valid_start_keys"]:
            continue
        partial_phone_number = key
        new_phone_numbers = _move_piece(
            piece, partial_phone_number, 1, phone_number_rules["length"] - 1)
        phone_numbers.extend(new_phone_numbers)

    return phone_numbers


def main():
    """ Instantiate chess "piece" and do all possibly movements with it
    on a keypad up to some desired length."""

    logging.debug("the key pad:\n%s" % str(keypad))
    logging.debug("valid_phone_number: %s" % str(valid_phone_number))

    for piece_type in PIECES:
        piece = ChessPiece(keypad, valid_phone_number).create_piece(
            PIECES[piece_type])
        logging.debug("chess piece %s:\n%s" 
            % (piece_type, pprint.pformat(piece)))

        valid_numbers = compute_phone_numbers(piece, valid_phone_number)
        logging.debug("sample of phone numbers:\n%s" 
            % pprint.pformat(valid_numbers[:10]))
        print piece_type + " -- {:,} valid phone numbers".format( 
            len(valid_numbers))

if __name__ == "__main__":
    main()
