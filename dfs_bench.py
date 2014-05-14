#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import sys
from pprint import pprint
from parsers.iozone import IOZoneOutputParser
from subprocess import Popen, PIPE

# make sure they are in ascending order
NUM_NODES = [1, 2, 4, 8, 16]


def run_command(command, nodes, node_count=len(NUM_NODES)):
    write_machinefile(nodes, node_count)
    output = run_cmd(['mpirun', '--machinefile', 'machinefile', './run_mpi', '%s' % command])
    return output

def parse_output(output, kind):
    try:
        if kind == 'iozone':
            return IOZoneOutputParser.parse(output)
        else:
            return {}
    except:
        print("Something bad happened with the command. "\
              "Here is the output:", file=sys.stderr)
        print(output, file=sys.stderr)

def write_machinefile(nodes, node_count):
    with open('machinefile', 'w') as f:
        f.write('\n'.join(nodes[:node_count]))

def run_cmd(cmd_args):
    out, err = Popen(cmd_args, stdout=PIPE).communicate()
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DFS bench")
    parser.add_argument('command', help="A single command to run on all nodes." \
            " Be sure to quote it so it is just one arg.")
    parser.add_argument('-f', '--file',
            help="A file that contains the list of commands to run.")
    args= parser.parse_args()

    cmd = args.command

    # reserve all the nodes from the beginning
    run_cmd(['/bin/bash', 'reserve.sh', '%d' % NUM_NODES[-1]])

    # get reserved node names from the generated machinefile
    with open('machinefile') as f:
        nodes = [line.strip() for line in f.readlines() if line.strip()]

    if args.file:
        with open(args.file) as f:
            data = json.load(f)
            cmd_list = data['commands']
    else:
        # make a bogus cmd list with just one command
        cmd_list = [
            {
                'type': 'all',
                'command': cmd,
                'parse': True
            }
        ]

    # run the benchmark with increasing numbers of nodes
    results = {}
    for node_count in NUM_NODES:
        for cmd in cmd_list:
            if cmd['type'] == 'all':
                output = run_command(cmd['command'], nodes, node_count)
            elif cmd['type'] == 'single':
                output = run_command(cmd['command'], nodes, 1)
            else:
                # skip unknown cmd type
                print("Skipping unknown command of type %s." % cmd['type'],
                    file=sys.stderr)
                continue

            if cmd.get('parse', False):
                kind = None
                if 'iozone' in cmd['command']:
                    kind = 'iozone'
                parsed = parse_output(output, kind)
                results[node_count] = parsed

    with open('results.json', 'wb') as f:
        json.dump(results, f, indent=2)
    print("See results in results.json.")

