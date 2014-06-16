#!/usr/bin/env python

from __future__ import print_function

import json
import prettyplotlib as ppl
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You need to pass in a dfs_bench.py output file. "\
              "Try it like ./dfs_bench.py path/to/file", file=sys.stderr)
        sys.exit(1)

    # read JSON data
    with open(sys.argv[1]) as f:
        data = json.load(f)

    # make a plot for every attribute
    try:
        os.mkdir('plots')
    except OSError:
        pass
    cores_list = [int(cores) for cores in data.keys()]
    cores_list.sort()
    # get the first dict as a sample so we know what attributes to look for
    sample = data[list(data)[0]]['total']
    for attr in sample.keys():
        xs = []
        ys = []
        for cores in cores_list:
            cores = str(cores) # for JSON indexing
            xs.append(int(cores))
            ys.append(int(data[cores]['total'][attr]))
        # convert to GBs
        ys = [y / (1024.0 * 1024.0) for y in ys]

        bottom = np.arange(len(cores_list))
        fig, ax = plt.subplots()
        ppl.bar(ax, bottom, ys, annotate=True, xticklabels=xs, grid='y')
        plt.xlabel('Number of Nodes')
        plt.ylabel('Aggregated Bandwidth (GB/s)')
        plt.title('%s' % attr[0].upper() + attr[1:])
        fig.savefig('plots/%s.png' % attr)
        plt.close(fig)

