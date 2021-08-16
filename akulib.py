# LIBRARY (built-in to compiler to allow a onefile package)

# Generic lib
akulib = '''
// Aku std library
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef FILE *file;

char* readfile(char* path, char* mode) {
    file f;

    if(mode == NULL) {
        f = fopen(path, "rb");
    } else {
        f = fopen(path, mode);
    }

    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);

    char* buffer = malloc(fsize + 1);
    fread(buffer, 1, fsize, f);
    fclose(f);

    buffer[fsize] = 0;
    return buffer;
}

char* join(char delim, char** strs) {
    char* res = calloc(128, sizeof(char));
    char* c;
    char sep[2] = { delim, 0 };
    int i = 0;
    for (c = strs[i]; c; c = strs[++i]) {
        strcat(res, c);
        strcat(res, sep);
    }
    return res;
}
'''

# Bare-metal runtime library
metallib = '''
// MetalLib (Aku Self-Contained Runtime Library)
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>


'''