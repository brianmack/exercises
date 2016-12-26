"""
Unit tests for compute phone numbers
"""
import unittest

import compute_valid_phone_numbers as ph

class TestAll(unittest.TestCase):
   
    def setUp(self):

        self.piece = ph.ChessPiece(
            ph.KEYPAD, ph.VALID_PHONE_NUMBER)
        
        self.bishop = self.piece.create_piece(
            ph.PIECES["bishop"])
        self.knight = self.piece.create_piece(
            ph.PIECES["knight"])

    def test_string_set(self):
        """ trivial string-ize all ints in range """
        range_open = ph.string_set_from_range(10)
        range_bounded = ph.string_set_from_range(5, 10)
        
        self.assertTrue("0" in range_open)
        self.assertTrue("9" in range_open)
        self.assertFalse("22" in range_open)
        
        self.assertFalse("0" in range_bounded)
        self.assertTrue("9" in range_bounded)
        self.assertFalse("22" in range_bounded)

    def test_keypad(self):
        """ right numbers in right spot?"""
        
        self.assertTrue(ph.KEYPAD[0,0] == "1")
        self.assertTrue(ph.KEYPAD[0,2] == "3")
        self.assertTrue(ph.KEYPAD[2,0] == "7")
        self.assertTrue(ph.KEYPAD[2,2] == "9")
        self.assertTrue(ph.KEYPAD[3,0] == "*")
        self.assertTrue(ph.KEYPAD[3,2] == "#")

    def test_rule_expansion(self):
        """ should cover all directions and replicate reps."""

        rule_reps = (2, )
        rule = (1, 3, rule_reps)
        expanded = self.piece.expand_rule(rule)
        
        self.assertTrue(len(expanded) == 4)
        self.assertTrue(expanded[0][2] == rule_reps)
        self.assertTrue(expanded[1][2] == rule_reps)
        self.assertTrue(expanded[2][2] == rule_reps)
        self.assertTrue(expanded[3][2] == rule_reps)

        # cartesian product of +/- on i,j
        self.assertTrue(expanded[1][0] == -1)
        self.assertTrue(expanded[2][0] == 1)
        self.assertTrue(expanded[0][1] == 3)
        self.assertTrue(expanded[3][1] == -3)
    
    
    def test_move(self):
        """ nothing happens on illegal moves."""
        

        self.assertFalse("*" in self.piece.phone_number["valid_keys"])
        self.assertFalse("#" in self.piece.phone_number["valid_keys"])

        # additions to this list should just be the value 
        # reached by indices on the phone keypad
        keys_moved_to = []
        
        self.piece.attempt_one_move(keys_moved_to, 5, 6)
        self.assertTrue(len(keys_moved_to) == 0) # nothing added

        self.piece.attempt_one_move(keys_moved_to, 0, 0)
        self.assertTrue(len(keys_moved_to) == 1)
        self.assertTrue(keys_moved_to[0] == "1")
        
        self.piece.attempt_one_move(keys_moved_to, 1, 1)
        self.assertTrue(len(keys_moved_to) == 2)
        self.assertTrue(keys_moved_to[1] == "5")
        
        self.piece.attempt_one_move(keys_moved_to, -3, 6)
        self.assertTrue(len(keys_moved_to) == 2) # nothing added
        
        # move lands on keypad but digit is invalid '*'
        self.piece.attempt_one_move(keys_moved_to, 3, 0)
        self.assertTrue(len(keys_moved_to) == 2) # nothing added
        
        # move lands on keypad but digit is invalid '#'
        self.piece.attempt_one_move(keys_moved_to, 3, 2)
        self.assertTrue(len(keys_moved_to) == 2) # nothing added

    def test_piece(self):
        """ all moves in piece are as expected."""

        # legal bishop moves from starting position 'key'
        self.assertTrue("5" in self.bishop["1"])
        self.assertTrue("9" in self.bishop["1"])
        
        self.assertFalse("2" in self.bishop["5"])
        self.assertFalse("2" in self.bishop["3"])
        
        # knight ...
        self.assertTrue("1" in self.knight["8"])
        self.assertTrue("4" in self.knight["0"])
        self.assertTrue("3" in self.knight["4"])
        
        self.assertFalse("2" in self.knight["5"])
        self.assertFalse("1" in self.knight["5"])
        self.assertFalse("*" in self.knight["5"])


    def test_compute_short_valid_number(self):
        """ alter valid params to get short, checkable strings."""
        
        valid_number_backup = ph.VALID_PHONE_NUMBER
        
        short_start_keys = ph.string_set_from_range(2,4) # 2, 3 ..
        ph.VALID_PHONE_NUMBER["length"] = 2
        ph.VALID_PHONE_NUMBER["valid_start_keys"] = short_start_keys

        king = self.piece.create_piece(ph.PIECES["king"])
        king_phone_numbers = ph.compute_phone_numbers(king)        
        
        # final keys are just adjacent and diagonal 
        # keys from 2 and 3 ...
        self.assertTrue(len(king_phone_numbers) == 8)
        self.assertTrue("24" in king_phone_numbers)
        self.assertTrue("21" in king_phone_numbers)
        self.assertTrue("36" in king_phone_numbers)
        self.assertFalse("22" in king_phone_numbers)
       
        knight = self.knight
        knight_phone_numbers = ph.compute_phone_numbers(knight)
        self.assertTrue(len(knight_phone_numbers) == 4)
        self.assertTrue("27" in knight_phone_numbers)
        self.assertTrue("29" in knight_phone_numbers)
        self.assertTrue("38" in knight_phone_numbers)
        self.assertTrue("34" in knight_phone_numbers)
        # doesn't wrap around ..
        self.assertFalse("37" in knight_phone_numbers)

        # reset injected global
        ph.VALID_PHONE_NUMBER = valid_number_backup 



if __name__ == "__main__":
    unittest.main()
