
import hashlib
import time


""" 
A binary tree of fixed size with the following properties:
    - FIFO behavior:  pops oldest element when new element added that 
        makes it exceed maximum allowed size
    - Can return elements in sorted order by insert time OR by key
        (this isn't really that helpful for file handles)
    - Constant time membership checking, but log N data retrieval
    - Self-updating when a node is popped (all descendents updated)

On b-tree vs dict:
    - Could have implemented a hash table with similar temporal properties
    - May or may not be more memory efficient than a hash table (but it's
        likely to be small, anyway, if used for file handles), depending
        on size of meta data vs. sparsity of hash table.
"""


def hashkey(key):
    """ You want to hash the key to improve randomness of the tree, so
    otherwise if you insert data based on a sorted list of keys, you'd
    have a very imbalanced tree.  Could also use the built-in .__hash__()
    method for hashable types.
    
    Must be called external to HandleCache."""
    
    if not isinstance(key, collections.Hashable):
        key = str(key)
    return hashlib.md5(key).hexdigest()


class HandleMetaData(object):
    """ Holds meta data about HandleCache object.  Using a set to track
    items (in non-sorted order of course) gives a constant time membership
    test property, which is nice.  But may or may not be useful?"""

    def __init__(self, max_size=256):
        
        self.members = set()
        self.size = 0
        
        # size management attributes
        self.max_size = max_size
        
        # points to least-used (oldest) node
        self.oldest = None
        self.newest = None


class HandleCache(object):
    """ A b-tree that limits itself to max_size.  When it grows too large,
    it pops the oldest node and adds a new node.  It uses python dictionary
    syntax to get and set items.  It uses a metadata class to control its
    size."""

    def __init__(self, max_size=256, _metadata=None, _parent=None):
        """ _meta_data and _parent only supplied in recursive calls."""
        
        if _metadata is None:
            self.metadata = HandleMetaData(max_size=max_size)
        else:
            self.metadata = _metadata

        # data attributes
        self.key = None
        self.data = None
        self.timestamp = None

        # navigation attributes
        # by key -- how we set and fetch data
        if _parent:
            self.parent = _parent
        else:
            self.parent = None

        self.child_left = None
        self.child_right = None

        # by time -- how we manage which data is included
        
        self.later = None
        
    def __getitem__(self, key):
        """ Retrieve data, return None if not found."""
        
        item = self.fetch(key)
        if item:
            return item.data
        else:
            return None
        
    def fetch(self, key):
        """ Retrieve node matching given key.  Returns None if no such
        node exists."""

        if key not in self.metadata.members:
            return None

        if key == self.key:
            return self
        elif key < self.key:
            return self.child_left.fetch(key)
        else:
            return self.child_right.fetch(key)

    def __set_node(self, key, data):
        """ Sets data attribute to node, while managing tree metadata such
        as oldest and newest nodes, size, and membership set."""

        timestamp = time.time()
        
        # If true means it's the root node, also the newest and oldest node
        if self.metadata.oldest is None:
            self.metadata.oldest = self

        # If true, the tree got too big! make some room!
        if self.metadata.size == self.metadata.max_size:
            self.pop() 
        
        # Set the actual data attributes
        self.key = key
        self.data = data
        self.timestamp = timestamp

        # set a "next" reference from old newest to new newest
        if self.metadata.newest:
            self.metadata.newest.later = self
        self.metadata.newest = self
        
        self.metadata.members.add(key)
        self.metadata.size += 1

    def _initialize_children(self):
        """ Sometimes it's useful to have empty child nodes instead of just
        "None" values.  The lookup and set-item procedures will be unaffected
        whether or not the child nodes are set:  When child.data is None,
        the node will be treated as unset, and a final destination for each.
        """
        if not self.child_left:
            self.child_left = HandleCache(
                _metadata=self.metadata, 
                _parent=self)
        if not self.child_right:
            self.child_right = HandleCache(
                _metadata=self.metadata,
                _parent=self)

    def __check_children(self, key, data):
        """ Private method to the __setitem__ operation.  Compare key to 
        two children.  If this is the 'right' place in the tree for this key,
        return 1 (found no children set, all clear).  Otherwise proceed to set
        data, using the relevant child node as new root for a new setitem 
        operation.
        """

        # the conditions that tell me to set the current node to new key
        # ie, children are none, or they are set but key is in range here.
        left_val = self.child_left is None or key > self.child_left.key
        right_val = self.child_right is None or key < self.child_right.key
        if left_val and right_val or not left_val and not right_val:
            return 1

        # otherwise go ahead and set on one child path
        if self.child_left and self.child_left.key:
            if key < self.child_left.key:
                self.child_left[key] = data
        
        if self.child_right and self.child_right.key:
            if key > self.child_right.key:
                self.child_right[key] = data
        
        return 0


    def __setitem__(self, key, data):
        """ Uses dict syntax to set an item, but does so as a tree instead
        of a dict -- values are not hashed to an array, instead they are
        recursively compared against lower nodes until a suitable place in
        the b-tree is found.

        If this node is unset, it will be either treated as the root of a 
        brand new tree, or if it already has descendents, it will be treated
        as an 'error' (in our case, empty nodes were caused by the pop / clear
        tree operations), and the new value will either be set here as an
        interpolated key (midway between keys of two descendents), or propogated
        down one branch or the other (see the '__check_children' method).

        Inputs:
            key:  hashable object
            data: anything
        """
        
        # either you arrived at a fresh node, so augment, or...
        # this node was popped, so check the children nodes
        if self.data is None:
            
            if self.__check_children(key, data):
                self.__set_node(key, data)
                return

        # Already in tree:  For a tree managed by insert time, update data.
        # To manage by last-used time, clear current node and move
        # data to newest.  (Not implemented)
        elif key == self.key:
            self.data = data

        # or pass to child if this node is set
        elif key < self.key:
            if not self.child_left:
                self.child_left = HandleCache(
                    _metadata=self.metadata,
                    _parent=self)
            self.child_left[key] = data

        else:
            if not self.child_right:
                self.child_right = HandleCache(
                    _metadata=self.metadata,
                    _parent=self)
            self.child_right[key] = data
        return

    def clear(self):
        """ Set all data properties to NULL, and also pointer to next."""
        #TODO should this also set parent / children relations to NULL?

        self.key = None
        self.data = None
        self.timestamp = None
        self.later = None
        
    
    def _reset_nodes(self, root, branch):
        """ Set every node in branch from root position in original tree."""
        
        # base case
        if not branch.data:
            return

        root[branch.key] = branch.data

        if branch.child_left:
            self._reset_nodes(root, branch.child_left)
        if branch.child_right:
            self._reset_nodes(root, branch.child_right)
                    
    def _update_left_links(self, rhs, lhs, parent):

        if rhs.data:

            # move right child under current parent
            rhs.parent = parent
            parent.child_left = rhs

            self._reset_nodes(rhs, lhs)

        elif lhs.data:
            
            # move left child under current parent
            lhs.parent = parent
            parent.child_left = lhs


    def _update_right_links(self, rhs, lhs, parent):

        if lhs.data:

            # move left child under current parent
            lhs.parent = parent
            parent.child_right = lhs
            
            self._reset_nodes(lhs, rhs)

        elif rhs.data:
            
            # move right child under current parent
            rhs.parent = parent
            parent.child_right = rhs

    def repair(self):
        """ check for broken links one level above.
        Now the question is, which child node should be upgraded to
        be the new parent, and is the remaining node a left or right
        child node? 

        For the left side, you want to promote the right
        child, because it's between the left child and parent in value.
                
        On the right side, you want to promote the left child, because
        it's between the right child and parent in value.
        """

        if self.parent:

            
            # This whole thing will be easier if we initialize child nodes
            self._initialize_children()
            print "child left:", self.child_left.key, self.child_left.data
            print "child right:", self.child_right.key, self.child_right.data
            print "parent: %s" % str(self.parent.key)

            # case where it's the left hand side: 
            # e.g. parent "a" > child "00"
            if self.child_left and self.parent.key > self.child_right.key:
                
                self._update_left_links(self.child_right, self.child_left, 
                    self.parent)
            
            else: # it's on the right node path...
                print "left node path"

                self._update_right_links(self.child_right, self.child_left, 
                    self.parent)

    
    def pop(self):
        """ Clear and reset oldest node to second oldest node."""
        
        self.metadata.members.remove(
            self.metadata.oldest.key)
        
        tmp = self.metadata.oldest.later
        self.metadata.oldest.clear()
        self.metadata.oldest = tmp
        self.metadata.size -= 1

    def items(self):
        """ Callable from any node, collects all (key, data) pairs from 
        all nodes and returns them in temporal (not key) order."""
        
        if not self.metadata.oldest:
            yield None
        else:
            items = []
            tmp = self.metadata.oldest
            while True:
                yield tmp.key, tmp.data
                if tmp.key == self.metadata.newest.key:
                    break
                tmp = tmp.later
            
      

def print_tree(root, level=0, lr="root"):
    """ Pretty print all key, data pairs from each level using depth-first
    descent."""

    s = "-" * level
    if level == 0:
        print "tree:"
    print "%s%s: %s, %s" % (s, str(lr), str(root.key), str(root.data))
    level += 1
    if root.child_left:
        print_tree(root.child_left, level, "l")
    if root.child_right:
        print_tree(root.child_right, level, "r")


if __name__ == "__main__":
    
    hc = HandleCache(max_size=3)

    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
    
    print "\n-- setting a to 1"
    hc["a"] = 1
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
    
    print "\n-- setting b to 2"
    hc["b"] = 2
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
    
    print "\n-- setting b to 22"
    hc["b"] = 22
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
    
    print "\n-- setting c to 3"
    hc["c"] = 3
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
    
    print_tree(hc)
    
    print "\n-- setting d to 4"
    hc["d"] = 4
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
   
    print_tree(hc)
    print "\n-- setting e to 5"
    hc["e"] = 5
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
   
    print_tree(hc)
    print "\n-- setting '0' to 0"
    hc["0"] = 0
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())

    print_tree(hc)
    print "\n-- setting 'f' to 42"
    hc["f"] = 42
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())

    print "\n-- setting 'aa' to 99"
    hc["aa"] = 99
    print hc.metadata.size, hc.metadata.members
    print hc.data, list(hc.items())
  
    
    hc["aca"] = 34
    hc["brian"] = 35
    hc["ana"] = 37
    hc["booger"] = 38

    print list(list(hc.items()))
    print_tree(hc)


    root = HandleCache()
    root["5"] = 1
    root["4"] = 2
    root["45"] = 3
    root["6"] = 4
    root["65"] = 5
    root["7"] = 6
    root["8"] = 7
    root["9"] = 8
    root["3"] = 9
    root["2"] = 10
    root["25"] = 11
    print_tree(root)

    tmp_node1 = root.fetch("7")
    tmp_node1.clear()
    tmp_node2 = root.fetch("4")
    tmp_node2.clear()
    print_tree(root)

    print "\nrepairing link"
    tmp_node1.repair()
    print_tree(root)

    print "\nrepairing link"
    tmp_node2.repair()
    print_tree(root)

    
    tmp_node = root.fetch("5")
    tmp_node.clear()
    tmp_node.repair()
    print_tree(root)

    root["1"] = 12
    print_tree(root)

    root["51"] = 13
    print_tree(root)
