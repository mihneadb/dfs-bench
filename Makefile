CC = mpicc

build: run_mpi

run_mpi: run_mpi.c
	$(CC) run_mpi.c -o run_mpi

.PHONY: clean
clean:
	rm -f run_mpi

