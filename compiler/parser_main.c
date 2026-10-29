#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "diag.h"
#include "lexer.h"
#include "semantic.h"

int yyparse(void);
extern AstNode *compiler_ast_root;

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
    int show_ast = 0, arg = 1;
    if (arg < argc && strcmp(argv[arg], "--ast") == 0) { show_ast = 1; arg++; }
    const char *path = arg < argc ? argv[arg] : "-";
    if (arg + 1 < argc) {
        fprintf(stderr, "Usage: %s [--ast] [FILE|-]\n", argv[0]);
        return 2;
    }
    FILE *input = strcmp(path, "-") == 0 ? stdin : fopen(path, "rb");
    if (!input) { perror(path); return 2; }
    size_t length = 0;
    char *source = read_source(input, &length);
    if (input != stdin) fclose(input);
    if (!source) { fprintf(stderr, "Could not read input.\n"); return 2; }

    diag_reset();
    compiler_ast_root = NULL;
    lexer_init(source, length);
    int result = yyparse();
    lexer_destroy();
    if (result == 0 && diag_error_count() == 0 && compiler_ast_root)
        (void)semantic_analyze(compiler_ast_root);

    for (size_t i = 0; i < diag_count(); ++i) {
        const Diagnostic *d = diag_get(i);
        fprintf(stderr, "%s:%d:%d: %s[%s]: %s\n",
            path, d->loc.line, d->loc.col,
            d->severity == SEV_ERROR ? "error" : "warning",
            d->code, d->message);
    }
    int ok = result == 0 && diag_error_count() == 0;
    if (show_ast && compiler_ast_root && result == 0) {
        ast_print_json(compiler_ast_root, 0);
        putchar('\n');
    } else if (ok) {
        printf("Syntax and semantic analysis successful: %s\n", path);
    } else {
        printf("Analysis failed: %d error(s), %d warning(s)\n",
            diag_error_count(), diag_warning_count());
    }
    ast_free(compiler_ast_root);
    compiler_ast_root = NULL;
    diag_reset();
    free(source);
    return ok ? 0 : 1;
}
