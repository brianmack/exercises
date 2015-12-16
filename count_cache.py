""" A dictionary that automatically adds and increments keys for you.
Primarily useful when ripping through log files to tally up how many
records had some attribute, when you don't know ahead of time what the
attributes will be.  Threadsafe."""


import threading

class CountCache(dict):
   
    def __init__(self):
        self._lock = threading.Lock()
    
    def __getitem__(self, key):
        """ Overload method of dict to do increment automatically
        when set."""
        with self._lock:
            if self.has_key(key):
                self.__setitem__(
                    key, 
                    super(CountCache, self).__getitem__(key) + 1)
                return super(CountCache, self).__getitem__(key)
            else:
                self.__setitem__(key, 1)
                return 1

    def clear(self):
        """ Remove all key, value pairs."""
        with self._lock:
            super(CountCache, self).clear()

    def lookup(self, key):
        """ Needs a safe lookup method since calling getitem will
        increment haha."""
        return self.get(key)

    def items(self):
        """ Return list of key, value tuples to play with."""        
        items = []
        for k in sorted(self.keys()):
            items.append((k, self.lookup(k)))
        return items
