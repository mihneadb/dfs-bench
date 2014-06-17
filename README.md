dfs-bench
=========

Benchmark distributed filesystems using MPI. Makes use of [iozone](http://www.iozone.org/)
and [mdtest](sourceforge.net/projects/mdtest/).

This is the code I'm writing for my bachelor's project at [VU Amsterdam](https://www.vu.nl/en/).

### Running it

This is documented for running on the [DAS4 cluster](http://www.cs.vu.nl/das4/).

```bash
# make sure you have iozone in cwd

make # build the binary

# run an iozone benchmark
./dfs_bench.py './iozone -f /var/scratch/mdr222/${NODENAME}_test -S 12000 -L 64 -c -e -s 1M -i0 -i1 -r 128 -R'

# or an mdtest benchmark
# ./run_mdtest.py './mdtest ...'

# plot the results
./make_bar_plots.py results.json

# or for mdtest results
# ./mdtest_make_bar_plots.py results.json

# see the plots in the plots/ directory
```

