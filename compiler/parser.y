%{
#include "common.h"
#include "diag.h"
int yylex(void);
void yyerror(const char *message);
%}
%define parse.error detailed
%locations
%token TOK_ERROR 257
%token TOK_KW_INT 258 TOK_KW_FLOAT 259 TOK_KW_DOUBLE 260 TOK_KW_CHAR 261 TOK_KW_VOID 262
%token TOK_KW_IF 263 TOK_KW_ELSE 264 TOK_KW_WHILE 265 TOK_KW_FOR 266 TOK_KW_DO 267 TOK_KW_RETURN 268 TOK_KW_BREAK 269 TOK_KW_CONTINUE 270
%token TOK_IDENTIFIER 271 TOK_INT_LITERAL 272 TOK_FLOAT_LITERAL 273 TOK_CHAR_LITERAL 274 TOK_STRING_LITERAL 275
%token TOK_ASSIGN 276 TOK_PLUS_ASSIGN 277 TOK_MINUS_ASSIGN 278 TOK_STAR_ASSIGN 279 TOK_SLASH_ASSIGN 280 TOK_PERCENT_ASSIGN 281 TOK_AMP_ASSIGN 282 TOK_PIPE_ASSIGN 283 TOK_CARET_ASSIGN 284 TOK_SHL_ASSIGN 285 TOK_SHR_ASSIGN 286
%token TOK_PLUS 287 TOK_MINUS 288 TOK_STAR 289 TOK_SLASH 290 TOK_PERCENT 291 TOK_INC 292 TOK_DEC 293 TOK_EQ 294 TOK_NE 295 TOK_LT 296 TOK_GT 297 TOK_LE 298 TOK_GE 299 TOK_AND_AND 300 TOK_OR_OR 301 TOK_NOT 302 TOK_AMP 303 TOK_PIPE 304 TOK_CARET 305 TOK_TILDE 306 TOK_SHL 307 TOK_SHR 308 TOK_QUESTION 309 TOK_COLON 310
%token TOK_LPAREN 311 TOK_RPAREN 312 TOK_LBRACE 313 TOK_RBRACE 314 TOK_LBRACKET 315 TOK_RBRACKET 316 TOK_SEMICOLON 317 TOK_COMMA 318 TOK_PREPROCESSOR 319 TOK_COMMENT 320
%start translation_unit
%%
translation_unit: external_list ;
external_list: %empty | external_list external ;
external: declaration | function_definition | TOK_PREPROCESSOR | TOK_COMMENT | error TOK_SEMICOLON { yyerrok; } ;
type_specifier: TOK_KW_INT | TOK_KW_FLOAT | TOK_KW_DOUBLE | TOK_KW_CHAR | TOK_KW_VOID ;
declaration: type_specifier init_declarator_list TOK_SEMICOLON ;
init_declarator_list: init_declarator | init_declarator_list TOK_COMMA init_declarator ;
init_declarator: declarator | declarator TOK_ASSIGN expression ;
declarator: TOK_IDENTIFIER | declarator TOK_LBRACKET optional_expression TOK_RBRACKET ;
optional_expression: %empty | expression ;
function_definition: type_specifier TOK_IDENTIFIER TOK_LPAREN parameter_list_opt TOK_RPAREN compound_statement ;
parameter_list_opt: %empty | TOK_KW_VOID | parameter_list ;
parameter_list: parameter | parameter_list TOK_COMMA parameter ;
parameter: type_specifier declarator ;
compound_statement: TOK_LBRACE block_item_list_opt TOK_RBRACE ;
block_item_list_opt: %empty | block_item_list ;
block_item_list: block_item | block_item_list block_item ;
block_item: declaration | statement | TOK_COMMENT ;
statement: compound_statement | expression_statement | selection_statement | iteration_statement | jump_statement ;
expression_statement: optional_expression TOK_SEMICOLON ;
selection_statement: TOK_KW_IF TOK_LPAREN expression TOK_RPAREN statement
 | TOK_KW_IF TOK_LPAREN expression TOK_RPAREN statement TOK_KW_ELSE statement ;
iteration_statement: TOK_KW_WHILE TOK_LPAREN expression TOK_RPAREN statement
 | TOK_KW_DO statement TOK_KW_WHILE TOK_LPAREN expression TOK_RPAREN TOK_SEMICOLON
 | TOK_KW_FOR TOK_LPAREN for_init_opt TOK_SEMICOLON optional_expression TOK_SEMICOLON optional_expression TOK_RPAREN statement ;
for_init_opt: %empty | expression | type_specifier init_declarator_list ;
jump_statement: TOK_KW_RETURN optional_expression TOK_SEMICOLON | TOK_KW_BREAK TOK_SEMICOLON | TOK_KW_CONTINUE TOK_SEMICOLON ;
expression: assignment_expression ;
assignment_expression: conditional_expression | unary_expression assignment_operator assignment_expression ;
assignment_operator: TOK_ASSIGN | TOK_PLUS_ASSIGN | TOK_MINUS_ASSIGN | TOK_STAR_ASSIGN | TOK_SLASH_ASSIGN | TOK_PERCENT_ASSIGN | TOK_AMP_ASSIGN | TOK_PIPE_ASSIGN | TOK_CARET_ASSIGN | TOK_SHL_ASSIGN | TOK_SHR_ASSIGN ;
conditional_expression: logical_or_expression | logical_or_expression TOK_QUESTION expression TOK_COLON conditional_expression ;
logical_or_expression: logical_and_expression | logical_or_expression TOK_OR_OR logical_and_expression ;
logical_and_expression: bitwise_or_expression | logical_and_expression TOK_AND_AND bitwise_or_expression ;
bitwise_or_expression: bitwise_xor_expression | bitwise_or_expression TOK_PIPE bitwise_xor_expression ;
bitwise_xor_expression: bitwise_and_expression | bitwise_and_expression TOK_CARET bitwise_and_expression ;
bitwise_and_expression: equality_expression | bitwise_and_expression TOK_AMP equality_expression ;
equality_expression: relational_expression | equality_expression TOK_EQ relational_expression | equality_expression TOK_NE relational_expression ;
relational_expression: shift_expression | relational_expression TOK_LT shift_expression | relational_expression TOK_GT shift_expression | relational_expression TOK_LE shift_expression | relational_expression TOK_GE shift_expression ;
shift_expression: additive_expression | shift_expression TOK_SHL additive_expression | shift_expression TOK_SHR additive_expression ;
additive_expression: multiplicative_expression | additive_expression TOK_PLUS multiplicative_expression | additive_expression TOK_MINUS multiplicative_expression ;
multiplicative_expression: unary_expression | multiplicative_expression TOK_STAR unary_expression | multiplicative_expression TOK_SLASH unary_expression | multiplicative_expression TOK_PERCENT unary_expression ;
unary_expression: postfix_expression | TOK_PLUS unary_expression | TOK_MINUS unary_expression | TOK_NOT unary_expression | TOK_TILDE unary_expression | TOK_AMP unary_expression | TOK_STAR unary_expression | TOK_INC unary_expression | TOK_DEC unary_expression ;
postfix_expression: primary_expression | postfix_expression TOK_LBRACKET expression TOK_RBRACKET | postfix_expression TOK_LPAREN argument_expression_list_opt TOK_RPAREN | postfix_expression TOK_INC | postfix_expression TOK_DEC ;
argument_expression_list_opt: %empty | argument_expression_list ;
argument_expression_list: assignment_expression | argument_expression_list TOK_COMMA assignment_expression ;
primary_expression: TOK_IDENTIFIER | TOK_INT_LITERAL | TOK_FLOAT_LITERAL | TOK_CHAR_LITERAL | TOK_STRING_LITERAL | TOK_LPAREN expression TOK_RPAREN ;
%%
void yyerror(const char *message) {
    SrcLoc loc = { yylloc.first_line, yylloc.first_column, 0, 1 };
    diag_add("SYN100", SEV_ERROR, loc, NULL, "%s", message);
}
