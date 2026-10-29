/* Shared source-location type. */
#ifndef COMMON_H
#define COMMON_H
typedef struct SrcLoc { int line; int col; int offset; int length; } SrcLoc;
#endif
