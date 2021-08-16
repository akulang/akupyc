# LIBRARY (built-in to compiler to allow a onefile package)

# Generic lib
akulib = '''
// Aku std library
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

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
'''

# Bare-metal runtime library
metallib = '''
// MetalLib (Aku Self-Contained Runtime Library)
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>


'''