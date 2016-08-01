
import copy
import pprint
import Queue
import sys


def _add_to_g(g, n1, n2):
    g[n1].append(n2)


def check_graph(g, n_nodes):
    """ Make sure every node is in the graph assuming that 1:n node
    names are all in there."""

    for i in range(1, n_nodes + 1):
        if i not in g:
            g[i] = []


def _get_case(f, cases=[]):

    case = {
        "n_nodes" : 0,
        "n_edges" : 0,
        "graph" : {},
        "start_pos" : None
    }

    line = f.next().strip().split()
    case["n_nodes"], case["n_edges"] = int(line[0]), int(line[1])
    check_graph(case["graph"], case["n_nodes"])

    for line in f:
        line = line.strip().split()
        if len(line) == 1:
            case["start_pos"] = int(line[0])
            break
        n1, n2 = int(line[0]), int(line[1])
        _add_to_g(case["graph"], n1, n2)
        _add_to_g(case["graph"], n2, n1)
    cases.append(case)

    try:
        _get_case(f, cases)
    except StopIteration:
        return



def parse_input(f):

    ncases = int(f.next())
    cases = []
    _get_case(f, cases)
    sys.stderr.write(pprint.pformat(cases))

    return cases



EDGE_LEN = 6
def get_paths(case):

    dists = {}
    for k in case["graph"]:
        dists[k] = {
            "seen" : 0,
            "d" : -1
        }


    start_node = case["start_pos"]
    dists[start_node]["seen"] = 1
    dists[start_node]["d"] = 0
    
    g = case["graph"]
    q = Queue.Queue()
    
    q.put(start_node)
    while not q.empty():
        
        current = q.get()
        
        for c_node in g[current]:
            
            if dists[c_node]["seen"] == 1:
                continue
            
            dists[c_node]["d"] = dists[current]["d"] + EDGE_LEN
            dists[c_node]["seen"] = 1
            q.put(c_node)

    return dists


if __name__ == "__main__":

    cases = parse_input(sys.stdin)
    for case in cases:
        
        d = get_paths(case)
        dk = sorted(d.keys())
        
        
        for k in dk:
            if k == case["start_pos"]:
                continue
            sys.stderr.write("%s, %s, %s\n" 
                % (str(k), str(d[k]["d"]), str(d[k]["seen"])))
        
        
        s = " ".join(str(d[k]["d"]) for k in dk 
            if k != case["start_pos"])
        
        print s
