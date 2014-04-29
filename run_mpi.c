#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wordexp.h>

#define BUFSIZE 5000
#define MASTER 0
#define FILE_PREFIX "dfs_bench_tmp_file_"

/* http://stackoverflow.com/a/4375516 */
char *expand_words(char *str) {
    wordexp_t p;
    size_t i;
    char **w;
    char *str_expanded = calloc(BUFSIZE, sizeof(char));

    wordexp(str, &p, 0);
    w = p.we_wordv;
    for (i = 0; i < p.we_wordc; ++i) {
        strcat(str_expanded, " ");
        strcat(str_expanded, w[i]);
    }

    wordfree(&p);
    return str_expanded;
}

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
    if (argc != 2) {
        fprintf(stderr, "Usage: %s 'cmd to run'\n", argv[0]);
        return 1;
    }

    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int proc_count;
    MPI_Comm_size(MPI_COMM_WORLD, &proc_count);

    FILE *fp = NULL;

    /* prepare cmd */
    char *expanded_cmd = expand_words(argv[1]);
    char cmd[BUFSIZE];
    char file_path[BUFSIZE];
    sprintf(file_path, "%s%d", FILE_PREFIX, rank);
    sprintf(cmd, "%s > %s", expanded_cmd, file_path);

    /* sync up the processes */
    MPI_Barrier(MPI_COMM_WORLD);

    /* run the cmd */
    system(cmd);
    free(expanded_cmd);

    /* read the output */
    fp = fopen(file_path, "r");
    if (!fp) {
        return 1;
    }
    unsigned int output_size;
    char *output = read_to_end(fp, &output_size);
    fclose(fp);

    /* delete the temp file */
    unlink(file_path);

    /* master process will fetch all outputs from slaves */
    if (rank == MASTER) {
        char **outputs = malloc(proc_count * sizeof(char *));
        outputs[0] = output;

        unsigned int *sizes = malloc(proc_count * sizeof(unsigned int));
        MPI_Request *requests = malloc(proc_count * sizeof(MPI_Request));

        int i;
        /* first get the sizes, async */
        for (i = 1; i < proc_count; ++i) {
            /* get size of string */
            MPI_Irecv(&sizes[i], 1, MPI_UNSIGNED, i, i, MPI_COMM_WORLD, &requests[i]);
        }
        for (i = 1; i < proc_count; ++i) {
            MPI_Wait(&requests[i], MPI_STATUS_IGNORE);
        }

        /* then get the actual outputs, async */
        for (i = 1; i < proc_count; ++i) {
            /* allocate and receive */
            outputs[i] = malloc(sizes[i] * sizeof(char));
            MPI_Irecv(outputs[i], sizes[i], MPI_CHAR, i, i, MPI_COMM_WORLD, &requests[i]);
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

