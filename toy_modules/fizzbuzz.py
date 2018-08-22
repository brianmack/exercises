""" Two-liner fizzbuzz
Index by lazy interpretation of logicals
Probably is not that efficient depending on compiler optimizations.
Breaking my usual rules about line length for one-liner cred.
"""

def fizzbuzz():  
    for i in xrange(101):  print([i, "fizzbuzz", "fizz", "buzz"][not i % 15 or (not i % 3) * 2 or (not i % 5) * 3])


if __name__ == "__main__":
    fizzbuzz()
