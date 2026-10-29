#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "diag.h"
#include "lexer.h"

int yyparse(void);

static char *read_source(FILE *file, size_t *length) {
    size_t capacity = 4096, used = 0;
    char *buffer = malloc(capacity);
    if (!buffer) return NULL;
    for (;;) {
        if (used == capacity) {
            if (capacity > (size_t)-1 / 2) { free(buffer); return NULL; }
            capacity *= 2;
            char *grown = realloc(buffer, capacity);
            if (!grown) { free(buffer); return NULL; }
            buffer = grown;
        }
        size_t count = fread(buffer + used, 1, capacity - used, file);
        used += count;
        if (count == 0) break;
    }
    if (ferror(file)) { free(buffer); return NULL; }
    *length = used;
    return buffer;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "-";
    if (argc > 2) {
        fprintf(stderr, "Usage: %s [FILE|-]\n", argv[0]);
        return 2;
    }
    FILE *input = strcmp(path, "-") == 0 ? stdin : fopen(path, "rb");
    if (!input) { perror(path); return 2; }
    size_t length = 0;
    char *source = read_source(input, &length);
    if (input != stdin) fclose(input);
    if (!source) { fprintf(stderr, "Could not read input.\n"); return 2; }

    diag_reset();
    lexer_init(source, length);
    int result = yyparse();
    lexer_destroy();

    for (size_t i = 0; i < diag_count(); ++i) {
        const Diagnostic *d = diag_get(i);
        fprintf(stderr, "%s:%d:%d: %s[%s]: %s\n",
            path, d->loc.line, d->loc.col,
            d->severity == SEV_ERROR ? "error" : "warning",
            d->code, d->message);
    }
    if (result == 0 && diag_error_count() == 0) {
        printf("Syntax analysis successful: %s\n", path);
    } else {
        printf("Syntax analysis failed: %d error(s), %d warning(s)\n",
            diag_error_count(), diag_warning_count());
    }
    int exit_code = (result == 0 && diag_error_count() == 0) ? 0 : 1;
    diag_reset();
    free(source);
    return exit_code;
}
