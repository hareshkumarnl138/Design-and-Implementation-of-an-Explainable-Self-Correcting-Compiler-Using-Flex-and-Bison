#ifndef LEXER_H
#define LEXER_H
#include <stddef.h>
#include "common.h"
extern SrcLoc lex_tok_loc;
extern int lex_emit_comments;
void lexer_init(const char *src, size_t len);
int lexer_next(void);
void lexer_destroy(void);
#endif
