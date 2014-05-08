#!/usr/bin/env python

from __future__ import print_function

import json
import sys
from pprint import pprint
from parsers.iozone import IOZoneOutputParser
from subprocess import Popen, PIPE

# make sure they are in ascending order
NUM_NODES = [1, 2, 4, 8, 16]


def write_machinefile(nodes, node_count):
    with open('machinefile', 'w') as f:
        f.write('\n'.join(nodes[:node_count]))

def run_cmd(cmd):
    out, err = Popen([cmd], stdout=PIPE).communicate()
    return out


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You need to pass in a command. "\
              "Try it like ./dfs_bench.py 'some_command'", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]

    # reserve all the nodes from the beginning
    run_cmd('./reserve.sh %d' % NUM_NODES[-1])

    # get reserved node names from the generated machinefile
    with open('machinefile') as f:
        nodes = [line.strip() for line in f.readlines() if line.strip()]

    # run the benchmark with increasing numbers of nodes
    results = {}
    for node_count in NUM_NODES:
        write_machinefile(nodes, node_count)
        output = run_cmd('mpirun --machinefile machinefile ./run_mpi \'%s\'' % cmd)
        try:
            if 'iozone' in cmd:
                results[node_count] = IOZoneOutputParser.parse(output)
            else:
                print("Unsupported command.", file=sys.stderr)
                sys.exit(1)
        except:
            print("Something bad happened with the command. "\
                  "Here is the output:", file=sys.stderr)
            print(output, file=sys.stderr)

    print(json.dumps(results, indent=2))

