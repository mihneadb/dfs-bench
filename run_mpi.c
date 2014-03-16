#include <stdio.h>
#include <stdlib.h>

#define BUFSIZE 1000

int main(int argc, char **argv) {

    FILE *fp = NULL;
    char buf[BUFSIZE];

    fp = popen(argv[1], "r");
    if (!fp) {
        return 1;
    }

    while (fgets(buf, BUFSIZE, fp)) {
        printf("%s", buf);
    }
    pclose(fp);

    return 0;
}

