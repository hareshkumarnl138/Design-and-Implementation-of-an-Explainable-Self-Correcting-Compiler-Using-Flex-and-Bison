%{
#define _POSIX_C_SOURCE 200809L
#include <stdlib.h>
#include <string.h>
#include "common.h"
#include "diag.h"
#include "ast.h"
AstNode *compiler_ast_root;
int yylex(void);
void yyerror(const char *message);
#define LOC ((SrcLoc){ yylloc.first_line, yylloc.first_column, 0, 1 })
#define NODE(k,t) ast_new((k),(t),LOC)
#define ADD(p,c) ast_add((p),(c))
%}
%define parse.error detailed
%locations
%code requires { #include "ast.h" }
%union { char *text; AstNode *node; }
%token TOK_ERROR 257
%token TOK_KW_INT 258 TOK_KW_FLOAT 259 TOK_KW_DOUBLE 260 TOK_KW_CHAR 261 TOK_KW_VOID 262
%token TOK_KW_IF 263 TOK_KW_ELSE 264 TOK_KW_WHILE 265 TOK_KW_FOR 266 TOK_KW_DO 267 TOK_KW_RETURN 268 TOK_KW_BREAK 269 TOK_KW_CONTINUE 270
%token <text> TOK_IDENTIFIER 271 TOK_INT_LITERAL 272 TOK_FLOAT_LITERAL 273 TOK_CHAR_LITERAL 274 TOK_STRING_LITERAL 275
%token TOK_ASSIGN 276 TOK_PLUS_ASSIGN 277 TOK_MINUS_ASSIGN 278 TOK_STAR_ASSIGN 279 TOK_SLASH_ASSIGN 280 TOK_PERCENT_ASSIGN 281 TOK_AMP_ASSIGN 282 TOK_PIPE_ASSIGN 283 TOK_CARET_ASSIGN 284 TOK_SHL_ASSIGN 285 TOK_SHR_ASSIGN 286
%token TOK_PLUS 287 TOK_MINUS 288 TOK_STAR 289 TOK_SLASH 290 TOK_PERCENT 291 TOK_INC 292 TOK_DEC 293 TOK_EQ 294 TOK_NE 295 TOK_LT 296 TOK_GT 297 TOK_LE 298 TOK_GE 299 TOK_AND_AND 300 TOK_OR_OR 301 TOK_NOT 302 TOK_AMP 303 TOK_PIPE 304 TOK_CARET 305 TOK_TILDE 306 TOK_SHL 307 TOK_SHR 308 TOK_QUESTION 309 TOK_COLON 310
%token TOK_LPAREN 311 TOK_RPAREN 312 TOK_LBRACE 313 TOK_RBRACE 314 TOK_LBRACKET 315 TOK_RBRACKET 316 TOK_SEMICOLON 317 TOK_COMMA 318 TOK_PREPROCESSOR 319 TOK_COMMENT 320
%type <node> translation_unit external_list external type_specifier declaration init_declarator_list init_declarator declarator optional_expression function_definition parameter_list_opt parameter_list parameter compound_statement block_item_list_opt block_item_list block_item statement expression_statement selection_statement iteration_statement for_init_opt jump_statement expression assignment_expression assignment_operator conditional_expression logical_or_expression logical_and_expression bitwise_or_expression bitwise_xor_expression bitwise_and_expression equality_expression relational_expression shift_expression additive_expression multiplicative_expression unary_expression postfix_expression argument_expression_list_opt argument_expression_list primary_expression
%precedence IF_WITHOUT_ELSE
%precedence TOK_KW_ELSE
%start translation_unit
%%
translation_unit : external_list { compiler_ast_root = NODE(AST_TRANSLATION_UNIT, NULL); ADD(compiler_ast_root, $1); $$ = compiler_ast_root; } ;
external_list : %empty { $$ = NULL; } | external_list external { $$ = ast_join($1, $2); } ;
external : declaration { $$=$1; } | function_definition { $$=$1; } | TOK_PREPROCESSOR { $$=NODE(AST_EMPTY,"preprocessor"); } | TOK_COMMENT { $$=NULL; } | error TOK_SEMICOLON { yyerrok; $$=NULL; } ;
type_specifier : TOK_KW_INT { $$=NODE(AST_EMPTY,"int"); } | TOK_KW_FLOAT { $$=NODE(AST_EMPTY,"float"); } | TOK_KW_DOUBLE { $$=NODE(AST_EMPTY,"double"); } | TOK_KW_CHAR { $$=NODE(AST_EMPTY,"char"); } | TOK_KW_VOID { $$=NODE(AST_EMPTY,"void"); } ;
declaration : type_specifier init_declarator_list TOK_SEMICOLON { $$=NODE(AST_DECLARATION,$1->text); ADD($$,$2); ast_free($1); } ;
init_declarator_list : init_declarator { $$=$1; } | init_declarator_list TOK_COMMA init_declarator { $$=ast_join($1,$3); } ;
init_declarator : declarator { $$=$1; } | declarator TOK_ASSIGN expression { $$=$1; ADD($$,$3); } ;
declarator : TOK_IDENTIFIER { $$=NODE(AST_DECLARATOR,$1); free($1); } | declarator TOK_LBRACKET optional_expression TOK_RBRACKET { $$=$1; if($3) ADD($$,$3); } ;
optional_expression : %empty { $$=NULL; } | expression { $$=$1; } ;
function_definition : type_specifier TOK_IDENTIFIER TOK_LPAREN parameter_list_opt TOK_RPAREN compound_statement { $$=NODE(AST_FUNCTION,$2); $$->type_name=$1->text?strdup($1->text):NULL; ADD($$,$4); ADD($$,$6); free($2); ast_free($1); } ;
parameter_list_opt : %empty { $$=NODE(AST_PARAMETER_LIST,NULL); } | TOK_KW_VOID { $$=NODE(AST_PARAMETER_LIST,NULL); } | parameter_list { $$=NODE(AST_PARAMETER_LIST,NULL); ADD($$,$1); } ;
parameter_list : parameter { $$=$1; } | parameter_list TOK_COMMA parameter { $$=ast_join($1,$3); } ;
parameter : type_specifier declarator { $$=NODE(AST_PARAMETER,$2->text); $$->type_name=$1->text?strdup($1->text):NULL; $$->loc=$2->loc; ast_free($1); ast_free($2); } ;
compound_statement : TOK_LBRACE block_item_list_opt TOK_RBRACE { $$=NODE(AST_BLOCK,NULL); ADD($$,$2); } ;
block_item_list_opt : %empty { $$=NULL; } | block_item_list { $$=$1; } ;
block_item_list : block_item { $$=$1; } | block_item_list block_item { $$=ast_join($1,$2); } ;
block_item : declaration { $$=$1; } | statement { $$=$1; } | TOK_COMMENT { $$=NULL; } ;
statement : compound_statement { $$=$1; } | expression_statement { $$=$1; } | selection_statement { $$=$1; } | iteration_statement { $$=$1; } | jump_statement { $$=$1; } ;
expression_statement : optional_expression TOK_SEMICOLON { $$=NODE(AST_EXPRESSION_STATEMENT,NULL); ADD($$,$1); } ;
selection_statement : TOK_KW_IF TOK_LPAREN expression TOK_RPAREN statement %prec IF_WITHOUT_ELSE { $$=NODE(AST_IF,NULL); ADD($$,$3); ADD($$,$5); } | TOK_KW_IF TOK_LPAREN expression TOK_RPAREN statement TOK_KW_ELSE statement { $$=NODE(AST_IF,NULL); ADD($$,$3); ADD($$,$5); ADD($$,$7); } ;
iteration_statement : TOK_KW_WHILE TOK_LPAREN expression TOK_RPAREN statement { $$=NODE(AST_WHILE,NULL); ADD($$,$3); ADD($$,$5); } | TOK_KW_DO statement TOK_KW_WHILE TOK_LPAREN expression TOK_RPAREN TOK_SEMICOLON { $$=NODE(AST_DO_WHILE,NULL); ADD($$,$2); ADD($$,$5); } | TOK_KW_FOR TOK_LPAREN for_init_opt TOK_SEMICOLON optional_expression TOK_SEMICOLON optional_expression TOK_RPAREN statement { $$=NODE(AST_FOR,NULL); ADD($$,$3); ADD($$,$5); ADD($$,$7); ADD($$,$9); } ;
for_init_opt : %empty { $$=NULL; } | expression { $$=$1; } | type_specifier init_declarator_list { $$=NODE(AST_DECLARATION,$1->text); ADD($$,$2); ast_free($1); } ;
jump_statement : TOK_KW_RETURN optional_expression TOK_SEMICOLON { $$=NODE(AST_RETURN,NULL); ADD($$,$2); } | TOK_KW_BREAK TOK_SEMICOLON { $$=NODE(AST_BREAK,NULL); } | TOK_KW_CONTINUE TOK_SEMICOLON { $$=NODE(AST_CONTINUE,NULL); } ;
expression : assignment_expression { $$=$1; } ;
assignment_expression : conditional_expression { $$=$1; } | unary_expression assignment_operator assignment_expression { $$=NODE(AST_ASSIGNMENT,$2->text); ADD($$,$1); ADD($$,$3); ast_free($2); } ;
assignment_operator : TOK_ASSIGN { $$=NODE(AST_EMPTY,"="); } | TOK_PLUS_ASSIGN { $$=NODE(AST_EMPTY,"+="); } | TOK_MINUS_ASSIGN { $$=NODE(AST_EMPTY,"-="); } | TOK_STAR_ASSIGN { $$=NODE(AST_EMPTY,"*="); } | TOK_SLASH_ASSIGN { $$=NODE(AST_EMPTY,"/="); } | TOK_PERCENT_ASSIGN { $$=NODE(AST_EMPTY,"%="); } | TOK_AMP_ASSIGN { $$=NODE(AST_EMPTY,"&="); } | TOK_PIPE_ASSIGN { $$=NODE(AST_EMPTY,"|="); } | TOK_CARET_ASSIGN { $$=NODE(AST_EMPTY,"^="); } | TOK_SHL_ASSIGN { $$=NODE(AST_EMPTY,"<<="); } | TOK_SHR_ASSIGN { $$=NODE(AST_EMPTY,">>="); } ;
conditional_expression : logical_or_expression { $$=$1; } | logical_or_expression TOK_QUESTION expression TOK_COLON conditional_expression { $$=NODE(AST_CONDITIONAL,"?:"); ADD($$,$1); ADD($$,$3); ADD($$,$5); } ;
logical_or_expression : logical_and_expression { $$=$1; } | logical_or_expression TOK_OR_OR logical_and_expression { $$=NODE(AST_BINARY,"||"); ADD($$,$1); ADD($$,$3); } ;
logical_and_expression : bitwise_or_expression { $$=$1; } | logical_and_expression TOK_AND_AND bitwise_or_expression { $$=NODE(AST_BINARY,"&&"); ADD($$,$1); ADD($$,$3); } ;
bitwise_or_expression : bitwise_xor_expression { $$=$1; } | bitwise_or_expression TOK_PIPE bitwise_xor_expression { $$=NODE(AST_BINARY,"|"); ADD($$,$1); ADD($$,$3); } ;
bitwise_xor_expression : bitwise_and_expression { $$=$1; } | bitwise_xor_expression TOK_CARET bitwise_and_expression { $$=NODE(AST_BINARY,"^"); ADD($$,$1); ADD($$,$3); } ;
bitwise_and_expression : equality_expression { $$=$1; } | bitwise_and_expression TOK_AMP equality_expression { $$=NODE(AST_BINARY,"&"); ADD($$,$1); ADD($$,$3); } ;
equality_expression : relational_expression { $$=$1; } | equality_expression TOK_EQ relational_expression { $$=NODE(AST_BINARY,"=="); ADD($$,$1); ADD($$,$3); } | equality_expression TOK_NE relational_expression { $$=NODE(AST_BINARY,"!="); ADD($$,$1); ADD($$,$3); } ;
relational_expression : shift_expression { $$=$1; } | relational_expression TOK_LT shift_expression { $$=NODE(AST_BINARY,"<"); ADD($$,$1); ADD($$,$3); } | relational_expression TOK_GT shift_expression { $$=NODE(AST_BINARY,">"); ADD($$,$1); ADD($$,$3); } | relational_expression TOK_LE shift_expression { $$=NODE(AST_BINARY,"<="); ADD($$,$1); ADD($$,$3); } | relational_expression TOK_GE shift_expression { $$=NODE(AST_BINARY,">="); ADD($$,$1); ADD($$,$3); } ;
shift_expression : additive_expression { $$=$1; } | shift_expression TOK_SHL additive_expression { $$=NODE(AST_BINARY,"<<"); ADD($$,$1); ADD($$,$3); } | shift_expression TOK_SHR additive_expression { $$=NODE(AST_BINARY,">>"); ADD($$,$1); ADD($$,$3); } ;
additive_expression : multiplicative_expression { $$=$1; } | additive_expression TOK_PLUS multiplicative_expression { $$=NODE(AST_BINARY,"+"); ADD($$,$1); ADD($$,$3); } | additive_expression TOK_MINUS multiplicative_expression { $$=NODE(AST_BINARY,"-"); ADD($$,$1); ADD($$,$3); } ;
multiplicative_expression : unary_expression { $$=$1; } | multiplicative_expression TOK_STAR unary_expression { $$=NODE(AST_BINARY,"*"); ADD($$,$1); ADD($$,$3); } | multiplicative_expression TOK_SLASH unary_expression { $$=NODE(AST_BINARY,"/"); ADD($$,$1); ADD($$,$3); } | multiplicative_expression TOK_PERCENT unary_expression { $$=NODE(AST_BINARY,"%"); ADD($$,$1); ADD($$,$3); } ;
unary_expression : postfix_expression { $$=$1; } | TOK_PLUS unary_expression { $$=NODE(AST_UNARY,"+"); ADD($$,$2); } | TOK_MINUS unary_expression { $$=NODE(AST_UNARY,"-"); ADD($$,$2); } | TOK_NOT unary_expression { $$=NODE(AST_UNARY,"!"); ADD($$,$2); } | TOK_TILDE unary_expression { $$=NODE(AST_UNARY,"~"); ADD($$,$2); } | TOK_AMP unary_expression { $$=NODE(AST_UNARY,"&"); ADD($$,$2); } | TOK_STAR unary_expression { $$=NODE(AST_UNARY,"*"); ADD($$,$2); } | TOK_INC unary_expression { $$=NODE(AST_UNARY,"++"); ADD($$,$2); } | TOK_DEC unary_expression { $$=NODE(AST_UNARY,"--"); ADD($$,$2); } ;
postfix_expression : primary_expression { $$=$1; } | postfix_expression TOK_LBRACKET expression TOK_RBRACKET { $$=NODE(AST_INDEX,NULL); ADD($$,$1); ADD($$,$3); } | postfix_expression TOK_LPAREN argument_expression_list_opt TOK_RPAREN { $$=NODE(AST_CALL,NULL); ADD($$,$1); ADD($$,$3); } | postfix_expression TOK_INC { $$=NODE(AST_UNARY,"post++"); ADD($$,$1); } | postfix_expression TOK_DEC { $$=NODE(AST_UNARY,"post--"); ADD($$,$1); } ;
argument_expression_list_opt : %empty { $$=NULL; } | argument_expression_list { $$=$1; } ;
argument_expression_list : assignment_expression { $$=$1; } | argument_expression_list TOK_COMMA assignment_expression { $$=ast_join($1,$3); } ;
primary_expression : TOK_IDENTIFIER { $$=NODE(AST_IDENTIFIER,$1); free($1); } | TOK_INT_LITERAL { $$=NODE(AST_LITERAL,$1); free($1); } | TOK_FLOAT_LITERAL { $$=NODE(AST_LITERAL,$1); free($1); } | TOK_CHAR_LITERAL { $$=NODE(AST_LITERAL,$1); free($1); } | TOK_STRING_LITERAL { $$=NODE(AST_LITERAL,$1); free($1); } | TOK_LPAREN expression TOK_RPAREN { $$=$2; } ;
%%
void yyerror(const char *message) { SrcLoc loc = { yylloc.first_line, yylloc.first_column, 0, 1 }; diag_add("SYN100", SEV_ERROR, loc, NULL, "%s", message); }
