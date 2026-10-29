#ifndef DIAG_H
#define DIAG_H
#include <stddef.h>
#include "common.h"
typedef enum { SEV_ERROR, SEV_WARNING } Severity;
typedef struct Diagnostic { char code[8]; Severity severity; SrcLoc loc; char lexeme[64]; char message[256]; } Diagnostic;
void diag_reset(void);
void diag_add(const char *code, Severity sev, SrcLoc loc, const char *lexeme, const char *fmt, ...)
    __attribute__((format(printf, 5, 6)));
size_t diag_count(void);
const Diagnostic *diag_get(size_t index);
int diag_error_count(void);
int diag_warning_count(void);
#endif
