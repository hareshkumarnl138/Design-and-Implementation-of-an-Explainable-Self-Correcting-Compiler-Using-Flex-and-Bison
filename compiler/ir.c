#define _POSIX_C_SOURCE 200809L
#include "ir.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    unsigned temp;
    unsigned label;
} IrState;

static void emit(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    putchar('\n');
    va_end(args);
}

static char *new_temp(IrState *state) {
    char buffer[32];
    snprintf(buffer, sizeof buffer, "t%u", ++state->temp);
    return strdup(buffer);
}

static char *new_label(IrState *state, const char *prefix) {
    char buffer[48];
    snprintf(buffer, sizeof buffer, "%s%u", prefix, ++state->label);
    return strdup(buffer);
}

static const AstNode *child_at(const AstNode *node, unsigned index) {
    const AstNode *child = node ? node->child : NULL;
    while (child && index--) child = child->next;
    return child;
}

static char *gen_expr(const AstNode *node, IrState *state);
static void gen_stmt(const AstNode *node, IrState *state);

static char *gen_expr(const AstNode *node, IrState *state) {
    if (!node) return strdup("0");

    switch (node->kind) {
    case AST_IDENTIFIER:
    case AST_LITERAL:
        return strdup(node->text ? node->text : "0");

    case AST_ASSIGNMENT: {
        const AstNode *lhs = child_at(node, 0);
        const AstNode *rhs = child_at(node, 1);
        char *right = gen_expr(rhs, state);
        const char *op = node->text ? node->text : "=";
        if (lhs && lhs->kind == AST_IDENTIFIER && lhs->text) {
            if (strcmp(op, "=") != 0) {
                char *temp = new_temp(state);
                emit("%s = %s %.*s %s", temp, lhs->text,
                     (int)(strlen(op) - 1), op, right);
                emit("%s = %s", lhs->text, temp);
                free(temp);
            } else {
                emit("%s = %s", lhs->text, right);
            }
            free(right);
            return strdup(lhs->text);
        }
        if (lhs && lhs->kind == AST_INDEX) {
            char *index = gen_expr(child_at(lhs, 1), state);
            char *base = gen_expr(child_at(lhs, 0), state);
            emit("%s[%s] = %s", base, index, right);
            free(index);
            free(base);
            free(right);
            return strdup("0");
        }
        emit("# unsupported assignment target");
        free(right);
        return strdup("0");
    }

    case AST_BINARY: {
        char *left = gen_expr(child_at(node, 0), state);
        char *right = gen_expr(child_at(node, 1), state);
        char *result = new_temp(state);
        emit("%s = %s %s %s", result, left,
             node->text ? node->text : "?", right);
        free(left);
        free(right);
        return result;
    }

    case AST_UNARY: {
        const char *op = node->text ? node->text : "";
        const AstNode *operand_node = child_at(node, 0);
        char *operand = gen_expr(operand_node, state);
        if ((strcmp(op, "++") == 0 || strcmp(op, "--") == 0 ||
             strcmp(op, "post++") == 0 || strcmp(op, "post--") == 0) &&
            operand_node && operand_node->kind == AST_IDENTIFIER) {
            char *old_value = NULL;
            int post = strncmp(op, "post", 4) == 0;
            int decrement = strstr(op, "--") != NULL;
            if (post) {
                old_value = new_temp(state);
                emit("%s = %s", old_value, operand);
            }
            emit("%s = %s %c 1", operand, operand, decrement ? '-' : '+');
            free(operand);
            return old_value ? old_value : strdup(operand_node->text);
        }
        char *result = new_temp(state);
        emit("%s = %s%s", result, op, operand);
        free(operand);
        return result;
    }

    case AST_CALL: {
        const AstNode *callee = child_at(node, 0);
        const AstNode *arg = callee ? callee->next : NULL;
        unsigned count = 0;
        for (const AstNode *it = arg; it; it = it->next) {
            char *value = gen_expr(it, state);
            emit("param %s", value);
            free(value);
            count++;
        }
        const char *name = callee && callee->text ? callee->text : "<indirect>";
        char *result = new_temp(state);
        emit("%s = call %s, %u", result, name, count);
        return result;
    }

    case AST_INDEX: {
        char *base = gen_expr(child_at(node, 0), state);
        char *index = gen_expr(child_at(node, 1), state);
        char *result = new_temp(state);
        emit("%s = %s[%s]", result, base, index);
        free(base);
        free(index);
        return result;
    }

    case AST_CONDITIONAL: {
        char *condition = gen_expr(child_at(node, 0), state);
        char *yes_label = new_label(state, "L");
        char *no_label = new_label(state, "L");
        char *end_label = new_label(state, "L");
        char *result = new_temp(state);
        emit("if %s goto %s", condition, yes_label);
        emit("goto %s", no_label);
        emit("%s:", yes_label);
        char *yes_value = gen_expr(child_at(node, 1), state);
        emit("%s = %s", result, yes_value);
        emit("goto %s", end_label);
        emit("%s:", no_label);
        char *no_value = gen_expr(child_at(node, 2), state);
        emit("%s = %s", result, no_value);
        emit("%s:", end_label);
        free(condition);
        free(yes_label);
        free(no_label);
        free(end_label);
        free(yes_value);
        free(no_value);
        return result;
    }

    default:
        return strdup("0");
    }
}

static void gen_stmt_one(const AstNode *item, IrState *state) {
    if (!item) return;
    switch (item->kind) {
    case AST_TRANSLATION_UNIT:
    case AST_BLOCK:
        gen_stmt(item->child, state);
        break;

    case AST_FUNCTION: {
        const char *name = item->text ? item->text : "<anonymous>";
        emit("");
        emit("function %s:", name);
        const AstNode *body = item->child;
        while (body && body->kind != AST_BLOCK) body = body->next;
        gen_stmt_one(body, state);
        emit("end function %s", name);
        break;
    }

    case AST_DECLARATION:
        for (const AstNode *decl = item->child; decl; decl = decl->next) {
            if (decl->kind != AST_DECLARATOR || !decl->text) continue;
            emit("# declare %s %s", item->text ? item->text : "int", decl->text);
            if (decl->child) {
                char *value = gen_expr(decl->child, state);
                emit("%s = %s", decl->text, value);
                free(value);
            }
        }
        break;

    case AST_EXPRESSION_STATEMENT:
        if (item->child) {
            char *value = gen_expr(item->child, state);
            free(value);
        }
        break;

    case AST_RETURN:
        if (item->child) {
            char *value = gen_expr(item->child, state);
            emit("return %s", value);
            free(value);
        } else {
            emit("return");
        }
        break;

    case AST_IF: {
        char *condition = gen_expr(child_at(item, 0), state);
        char *else_label = new_label(state, "L_else_");
        char *end_label = new_label(state, "L_end_");
        emit("ifFalse %s goto %s", condition, else_label);
        gen_stmt_one(child_at(item, 1), state);
        if (child_at(item, 2)) {
            emit("goto %s", end_label);
            emit("%s:", else_label);
            gen_stmt_one(child_at(item, 2), state);
            emit("%s:", end_label);
        } else {
            emit("%s:", else_label);
        }
        free(condition);
        free(else_label);
        free(end_label);
        break;
    }

    case AST_WHILE: {
        char *start = new_label(state, "L_while_");
        char *end = new_label(state, "L_end_while_");
        emit("%s:", start);
        char *condition = gen_expr(child_at(item, 0), state);
        emit("ifFalse %s goto %s", condition, end);
        gen_stmt_one(child_at(item, 1), state);
        emit("goto %s", start);
        emit("%s:", end);
        free(condition);
        free(start);
        free(end);
        break;
    }

    case AST_DO_WHILE: {
        char *start = new_label(state, "L_do_");
        emit("%s:", start);
        gen_stmt_one(child_at(item, 0), state);
        char *condition = gen_expr(child_at(item, 1), state);
        emit("if %s goto %s", condition, start);
        free(condition);
        free(start);
        break;
    }

    case AST_FOR: {
        const AstNode *init = child_at(item, 0);
        const AstNode *condition_node = child_at(item, 1);
        const AstNode *step = child_at(item, 2);
        const AstNode *body = child_at(item, 3);
        gen_stmt_one(init, state);
        char *start = new_label(state, "L_for_");
        char *step_label = new_label(state, "L_for_step_");
        char *end = new_label(state, "L_end_for_");
        emit("%s:", start);
        if (condition_node) {
            char *condition = gen_expr(condition_node, state);
            emit("ifFalse %s goto %s", condition, end);
            free(condition);
        }
        gen_stmt_one(body, state);
        emit("%s:", step_label);
        if (step) {
            char *value = gen_expr(step, state);
            free(value);
        }
        emit("goto %s", start);
        emit("%s:", end);
        free(start);
        free(step_label);
        free(end);
        break;
    }

    case AST_BREAK:
        emit("# break (loop target resolution pending)");
        break;

    case AST_CONTINUE:
        emit("# continue (loop target resolution pending)");
        break;

    case AST_EMPTY:
        break;

    default:
        if (item->kind == AST_ASSIGNMENT || item->kind == AST_BINARY ||
            item->kind == AST_UNARY || item->kind == AST_CALL ||
            item->kind == AST_CONDITIONAL || item->kind == AST_INDEX ||
            item->kind == AST_IDENTIFIER || item->kind == AST_LITERAL) {
            char *value = gen_expr(item, state);
            free(value);
        } else {
            gen_stmt(item->child, state);
        }
        break;
    }
}

static void gen_stmt(const AstNode *node, IrState *state) {
    for (const AstNode *item = node; item; item = item->next)
        gen_stmt_one(item, state);
}

void ir_generate(const AstNode *root) {
    IrState state = {0, 0};
    puts("# Three-address code (TAC); temporaries are named t1, t2, ...");
    gen_stmt(root, &state);
}
