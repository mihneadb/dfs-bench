#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BUFSIZE 1000

char *read_to_end(FILE *fp) {
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
    }
    return string;
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    FILE *fp = NULL;

    /* sync up the processes */
    MPI_Barrier(MPI_COMM_WORLD);
    fp = popen(argv[1], "r");
    if (!fp) {
        return 1;
    }

    char *output = read_to_end(fp);
    pclose(fp);

    printf("%s", output);
    free(output);

    MPI_Finalize();
    return 0;
}

