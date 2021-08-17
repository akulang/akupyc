# LIBRARY (built-in to compiler to allow a onefile package)

# Generic lib
akulib = '''
// Aku std library
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

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

int print(char* str) {
    int written = 0;
    written = printf("%s", str);
    return written;
}

int println(char* str) {
    int written = 0;
    written = printf("%s\\n", str);
    return written;
}

char* input(char* prompt, int size) {
    char* res = malloc(size);
    printf("%s", prompt);
    fgets(res, size, stdin);
    return res;
}
'''

# Bare-metal runtime library
metallib = '''
// MetalLib (Aku Self-Contained Runtime Library)
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

int strlen(char* str) {
    int len = 0;
    while(str[len])
        len++;
    return len;
}

void* memmove(void* dstptr,  void* srcptr, uint64_t size) {
    uint8_t* dst = (uint8_t*) dstptr;
	uint8_t* src = (uint8_t*) srcptr;
	if (dst < src) {
		for (uint64_t i = 0; i < size; i++)
			dst[i] = src[i];
	} else {
		for (uint64_t i = size; i != 0; i--)
			dst[i-1] = src[i-1];
	}
	return dstptr;
}

int memcmp(void* aptr, void* bptr, uint64_t size) {
	uint8_t* a = (uint8_t*) aptr;
	uint8_t* b = (uint8_t*) bptr;
	for (uint64_t i = 0; i < size; i++) {
		if (a[i] < b[i])
			return -1;
		else if (b[i] < a[i])
			return 1;
	}
	return 0;
}

void* memset(void* bufptr, int value, uint64_t size) {
	uint8_t* buf = (uint8_t*) bufptr;
	for (uint64_t i = 0; i < size; i++)
		buf[i] = (uint8_t) value;
	return bufptr;
}

void* memcpy(void* dstptr, void* restrict srcptr, uint64_t size) {
	uint8_t* dst = (uint8_t*) dstptr;
	uint64_t* src = (uint64_t*) srcptr;
	for (uint64_t i = 0; i < size; i++)
		dst[i] = src[i];
	return dstptr;
}

static inline void outb(uint16_t port, uint8_t val) {
    asm volatile ( "outb %0, %1" : : "a"(val), "Nd"(port) );
}

static inline uint8_t inb(uint64_t port) {
    uint8_t ret;
    asm volatile ( "inb %1, %0"
                   : "=a"(ret)
                   : "Nd"(port) );
    return ret;
}

static inline void outw(uint16_t port, uint16_t val) {
    asm volatile ( "outw %0, %1" : : "a"(val), "Nd"(port) );
}

static inline uint16_t inw(uint16_t port) {
    uint16_t ret;
    asm volatile ( "inw %1, %0"
                   : "=a"(ret)
                   : "Nd"(port) );
    return ret;
}

static inline void outl(uint16_t port, uint32_t val) {
    asm volatile ( "outl %0, %1" : : "a"(val), "Nd"(port) );
}

static inline uint32_t inl(uint16_t port) {
    uint32_t ret;
    asm volatile ( "inl %1, %0"
                   : "=a"(ret)
                   : "Nd"(port) );
    return ret;
}
'''