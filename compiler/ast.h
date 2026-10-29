#ifndef AST_H
#define AST_H
#include "common.h"
typedef enum {
 AST_TRANSLATION_UNIT, AST_DECLARATION, AST_DECLARATOR, AST_FUNCTION,
 AST_PARAMETER_LIST, AST_PARAMETER, AST_BLOCK, AST_IF, AST_WHILE, AST_DO_WHILE,
 AST_FOR, AST_RETURN, AST_BREAK, AST_CONTINUE, AST_EXPRESSION_STATEMENT,
 AST_ASSIGNMENT, AST_CONDITIONAL, AST_BINARY, AST_UNARY, AST_CALL, AST_INDEX,
 AST_IDENTIFIER, AST_LITERAL, AST_EMPTY
} AstKind;
typedef struct AstNode {
 AstKind kind;
 char *text;
 char *type_name;
 SrcLoc loc;
 struct AstNode *child;
 struct AstNode *next;
} AstNode;
AstNode *ast_new(AstKind kind, const char *text, SrcLoc loc);
AstNode *ast_add(AstNode *parent, AstNode *child);
AstNode *ast_join(AstNode *first, AstNode *second);
void ast_free(AstNode *node);
const char *ast_kind_name(AstKind kind);
void ast_print_json(const AstNode *node, int indent);
#endif
