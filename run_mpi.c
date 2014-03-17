#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFSIZE 1000
#define MASTER 0

char *read_to_end(FILE *fp, unsigned int *size_out) {
    int size = 1;
    int capacity = BUFSIZE;
    char buf[BUFSIZE];
    char *string = malloc(BUFSIZE * sizeof(char));
    string[0] = '\0';

    while (fgets(buf, BUFSIZE, fp)) {
        if (size + BUFSIZE > capacity) {
            capacity *= 2;
            string = realloc(string, capacity);
        }
        strcat(string, buf);
        size += strlen(buf);
    }
    *size_out = size;
    return string;
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int proc_count;
    MPI_Comm_size(MPI_COMM_WORLD, &proc_count);

    FILE *fp = NULL;

    /* sync up the processes */
    MPI_Barrier(MPI_COMM_WORLD);
    fp = popen(argv[1], "r");
    if (!fp) {
        return 1;
    }

    unsigned int output_size;
    char *output = read_to_end(fp, &output_size);
    pclose(fp);

    /* master process will fetch all outputs from slaves */
    if (rank == MASTER) {
        char **outputs = malloc(proc_count * sizeof(char *));
        outputs[0] = output;

        unsigned int *sizes = malloc(proc_count * sizeof(unsigned int));
        MPI_Request *requests = malloc(proc_count * sizeof(MPI_Request));

        int i;
        unsigned int size;

        /* first get the sizes, async */
        for (i = 1; i < proc_count; ++i) {
            /* get size of string */
            MPI_Irecv(&size, 1, MPI_UNSIGNED, i, i, MPI_COMM_WORLD, &requests[i]);
        }
        for (i = 1; i < proc_count; ++i) {
            MPI_Wait(&requests[i], MPI_STATUS_IGNORE);
        }

        /* then get the actual outputs, async */
        for (i = 1; i < proc_count; ++i) {
            /* allocate and receive */
            outputs[i] = malloc(size * sizeof(char));
            MPI_Irecv(outputs[i], size, MPI_CHAR, i, i, MPI_COMM_WORLD, &requests[i]);
        }
        for (i = 1; i < proc_count; ++i) {
            MPI_Wait(&requests[i], MPI_STATUS_IGNORE);
        }

        /* master prints out outputs */
        for (i = 0; i < proc_count; ++i) {
            printf("<<< OUTPUT %d >>>\n", i);
            printf("%s\n", outputs[i]);

            free(outputs[i]);
        }

        free(outputs);
        free(sizes);
        free(requests);
    } else {
        /* send size of output to master */
        MPI_Send(&output_size, 1, MPI_UNSIGNED, MASTER, rank, MPI_COMM_WORLD);
        /* send the actual output to master */
        MPI_Send(output, output_size, MPI_CHAR, MASTER, rank, MPI_COMM_WORLD);

        free(output);
    }


    MPI_Finalize();
    return 0;
}

