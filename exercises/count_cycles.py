
import copy
import logging
import pprint
import sys


DEFAULT_CYCLE = -1
def _add_to_graph(g, n1, n2):
    """ Append new node to edges list if reference node
    already in graph, otherwise add both reference node
    and new node.
    
    Graph has metadata about each node in tuple form as:
        (<edges-list>, <discovered>, <prev-cycle>)

    Inputs:
        g: existing graph
        n1: reference node (edge beginning at this node)
        n2: new node (edge pointing to this node)
    Returns:
        nothing but modifies graph in place
    """
    
    if n1 in g:
        g[n1][0].append(n2)
    else:
        g[n1] = [[n2], 0, DEFAULT_CYCLE]


def read_input(f):
    """ Parse input file as graph.  Input should be one line
    for a directed edge, like:

    start_node,end_node
    """

    g = {}
    for line in f:
        
        n1, n2 = line.strip().split(",")
        _add_to_graph(g, n1, n2)

    return g



def depth_search(g, current_node, current_path, this_cycle):
    """ search graph until you get to an element you've seen before.
    Inputs:
        g: (dict) graph 
        current_node: name of node as a key in g
        current_path: set of all visited nodes on this path
        this_cycle: (int) tracks which DFS it was last part of
    Returns:
        ct: count of cycles discovered in this and all sub trees
    """

    ct = 0
    logging.debug("search node %s, path = %s" 
        % (str(current_node), str(current_path)))
    

    reachable_nodes = g[current_node][0] # edges index
    logging.debug("reachable nodes are %s" % str(reachable_nodes))
    for node in reachable_nodes:
        
        # unpack history data about this particular node
        _, discovered, prev_cycle = g[node]
        # check if this route was previously searched
        if this_cycle > prev_cycle and prev_cycle != DEFAULT_CYCLE:
            logging.debug("saw node %s in previous search" % str(node))
            continue
        
        g[node][2] = this_cycle
        g[node][1] = 1 # discovered = true

        if node in current_path:
            logging.debug("%s in current path %s, ct += 1" 
                % (str(node), str(current_path)))
            ct += 1
            continue
        
        current_path.add(node)
        ct += depth_search(
            g, node, current_path, this_cycle)

        # 'pop' current node , it's no longer part of any future cycle
        current_path.remove(node)

    return ct


def get_cycles(g):
    """ Search all (possibly disconnected) nodes in graph and count
    the unique cycles.
    Input:
        g: (dict) graph where nodes are keys, and values are lists of
            edges.
    Returns:
        num_cycles: (int) count of unique cycles
    """
    
    # initialize with starting node
    previous_roots = set()

    # if we didn't want to maintain a whole set of size O(n) of all the
    # graph's nodes, we could mark these in the graph g itself.
    num_cycles = 0
    cycle_counter = -1

    for node in g:
        
        if not g[node][1]: # 'discovered' index
            
            logging.debug("--- starting new node %s" % str(node))
            
            # initialize for new DFS
            cycle_counter += 1
            visited = set([node])
            
            tmp_cycles = depth_search(g, node, visited, cycle_counter)
            num_cycles += tmp_cycles

    return num_cycles


def main():

    fname = sys.argv[1]
    f = open(fname)

    graph = read_input(f)

    logging.debug("graph input\n%s" % pprint.pformat(graph))
    
    num_cycles = get_cycles(graph)
    
    return num_cycles


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG)
    num_cycles = main()
    print "num cycles in graph = %i" % int(num_cycles)
