#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import sys
from pprint import pprint
from parsers.mdtest import MDTestOutputParser
from subprocess import Popen, PIPE

# make sure they are in ascending order
NUM_NODES = [1, 2, 4, 8, 16]


def run_command(command, nodes, node_count=len(NUM_NODES)):
    write_machinefile(nodes, node_count)
    output = run_cmd(['mpirun', '--machinefile', 'machinefile', '%s' % command])
    return output

def write_machinefile(nodes, node_count):
    with open('machinefile', 'w') as f:
        f.write('\n'.join(nodes[:node_count]))

def run_cmd(cmd_args):
    out, err = Popen(cmd_args, stdout=PIPE).communicate()
    return out


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Must run like %s './mdtest -i 10 -n 100 -S -d /some/path...'." % sys.argv[0],
              file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]

    # reserve all the nodes from the beginning
    run_cmd(['/bin/bash', 'reserve.sh', '%d' % NUM_NODES[-1]])

    # get reserved node names from the generated machinefile
    with open('machinefile') as f:
        nodes = [line.strip() for line in f.readlines() if line.strip()]


    # run the benchmark with increasing numbers of nodes
    results = {}
    for node_count in NUM_NODES:
        output = run_command(cmd['command'], nodes, node_count)
        parsed = MDTestOutputParser.parse(output)
        results[node_count] = {'total': parsed}

    with open('results.json', 'wb') as f:
        json.dump(results, f, indent=2)
    print("See results in results.json.")


