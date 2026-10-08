/* Small host adapter to the pinned engine tool's LZ77 codec. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lz.h"

int main(int argc, char **argv)
{
    if (argc != 4 || (strcmp(argv[1], "encode") && strcmp(argv[1], "decode"))) return 2;
    FILE *input = fopen(argv[2], "rb");
    if (!input || fseek(input, 0, SEEK_END)) return 2;
    long length = ftell(input);
    if (length < 1 || length > 1048576) return 2;
    rewind(input);
    unsigned char *bytes = malloc(length);
    if (!bytes || fread(bytes, length, 1, input) != 1) return 2;
    fclose(input);
    int size = 0;
    unsigned char *result;
    if (!strcmp(argv[1], "encode"))
        result = LZCompress(bytes, length, &size, 2);
    else
    {
        if (length < 4 || bytes[0] != 0x10) return 2;
        unsigned declared = bytes[1] | bytes[2] << 8 | bytes[3] << 16;
        if (!declared || declared > 16384) return 2;
        result = LZDecompress(bytes, length, &size);
        if (size != (int) declared) return 2;
    }
    FILE *output = fopen(argv[3], "wbx");
    if (!output || !result || fwrite(result, size, 1, output) != 1) return 2;
    fclose(output);
    free(result);
    free(bytes);
    return 0;
}
