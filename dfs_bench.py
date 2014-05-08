import sys
from pprint import pprint
from parsers.iozone import IOZoneOutputParser
from subprocess import check_output

NUM_NODES = [1, 2, 4, 8, 16, 32, 64]


def write_machinefile(nodes, node_count):
    with open('machinefile', 'w') as f:
        f.write('\n'.join(nodes[:node_count]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You need to pass in a command. "\
              "Try it like ./dfs_bench.py 'some_command'", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]

    # reserve all the nodes from the beginning
    check_output('./reserve.sh %d' % count)

    # get reserved node names from the generated machinefile
    with open('machinefile') as f:
        nodes = [line.strip() for line in f.readlines() if line.strip()]

    # run the benchmark with increasing numbers of nodes
    results = {}
    for node_count in NUM_NODES:
        write_machinefile(nodes, node_count)
        output = check_cmd('mpirun --machinefile machinefile ./run_mpi \'%s\'' % cmd)
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

