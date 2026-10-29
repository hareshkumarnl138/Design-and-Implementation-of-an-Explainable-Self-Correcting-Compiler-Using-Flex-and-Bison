#ifndef IR_H
#define IR_H

#include "ast.h"

/* Emit a readable three-address-code listing for the supported AST subset. */
void ir_generate(const AstNode *root);

#endif
