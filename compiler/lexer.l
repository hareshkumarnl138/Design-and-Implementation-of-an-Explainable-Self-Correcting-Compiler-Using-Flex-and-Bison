/* Flex lexer for a defined subset of C. */
%option noyywrap nounput noinput nodefault 8bit never-interactive
%{
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef PARSER_BUILD
#include "parser.tab.h"
#endif
#include "common.h"
#include "diag.h"
#include "lexer.h"
#ifdef PARSER_BUILD
#include "parser.tab.h"
#else
#include "tokens.h"
#endif
static char *copy_lexeme(const char *text, size_t len) { char *out = malloc(len + 1); if (out) { memcpy(out, text, len); out[len] = '\0'; } return out; }
#ifdef PARSER_BUILD
#define RETURN_TEXT(tok) do { yylval.text = copy_lexeme(yytext, (size_t)yyleng); return (tok); } while (0)
#else
#define RETURN_TEXT(tok) return (tok)
#endif
SrcLoc lex_tok_loc;
int lex_emit_comments = 0;
static int cur_line=1,cur_col=1,cur_off=0;
static SrcLoc comment_start;
static YY_BUFFER_STATE scan_buffer;
static void advance_location(const char *text,int len){
 lex_tok_loc.line=cur_line; lex_tok_loc.col=cur_col; lex_tok_loc.offset=cur_off; lex_tok_loc.length=len;
#ifdef PARSER_BUILD
 yylloc.first_line=cur_line; yylloc.first_column=cur_col;
#endif
 for(int i=0;i<len;i++){if(text[i]=='\n'){cur_line++;cur_col=1;}else cur_col++;}
 cur_off+=len;
#ifdef PARSER_BUILD
 yylloc.last_line=cur_line; yylloc.last_column=cur_col>1?cur_col-1:1;
#endif
}
#define YY_USER_ACTION advance_location(yytext,yyleng);
static void report_invalid_char(const char *text){unsigned char c=(unsigned char)text[0];if(c>=0x20&&c<0x7f)diag_add("LEX001",SEV_ERROR,lex_tok_loc,text,"Invalid character '%c'",c);else diag_add("LEX001",SEV_ERROR,lex_tok_loc,text,"Invalid character (byte 0x%02X)",c);}
static int scan_literal_body(const char *body,int len){int line=lex_tok_loc.line,col=lex_tok_loc.col+1,off=lex_tok_loc.offset+1,nchars=0;for(int i=0;i<len;){if(body[i]!='\\'){i++;col++;nchars++;continue;}char c=(i+1<len)?body[i+1]:'\0';int used=2,ok=1,counts=1;if(c&&strchr("ntrvabf\\'\"?",c)){}else if(c>='0'&&c<='7'){used=1;while(used<4&&i+used<len&&body[i+used]>='0'&&body[i+used]<='7')used++;}else if(c=='x'){int j=i+2;while(j<len&&isxdigit((unsigned char)body[j]))j++;if(j==i+2)ok=0;used=j-i;}else if(c=='\n')counts=0;else ok=0;if(!ok){SrcLoc here={line,col,off+i,used};char esc[8];snprintf(esc,sizeof esc,"%.*s",used<7?used:7,body+i);diag_add("LEX008",SEV_WARNING,here,esc,"Unknown escape sequence '%s'",esc);}if(c=='\n'){line++;col=1;}else col+=used;i+=used;nchars+=counts;}return nchars;}
%}
D [0-9]
HEXD [0-9a-fA-F]
EXP [eE][+-]?{D}+
ISUF [uUlL]*
FSUF [fFlL]?
ID [A-Za-z_][A-Za-z0-9_]*
CHARBODY ([^'\\\n]|\\[^\n])
STRBODY ([^"\\\n]|\\(.|\n))
%x COMMENT
%%
[ \t\r\f\v]+ ;
\n ;
^[ \t]*"#".* { return TOK_PREPROCESSOR; }
"//".* { if(lex_emit_comments)return TOK_COMMENT; }
"/*" { comment_start=lex_tok_loc;BEGIN(COMMENT); }
<COMMENT>"*/" { BEGIN(INITIAL);comment_start.length=cur_off-comment_start.offset;if(lex_emit_comments){lex_tok_loc=comment_start;return TOK_COMMENT;} }
<COMMENT>[^*\n]+ ;
<COMMENT>"*" ;
<COMMENT>\n ;
<COMMENT><<EOF>> { BEGIN(INITIAL);comment_start.length=cur_off-comment_start.offset;lex_tok_loc=comment_start;diag_add("LEX006",SEV_ERROR,comment_start,"/*","Unterminated block comment (opened here, never closed)");return TOK_ERROR; }
"int" {return TOK_KW_INT;}
"float" {return TOK_KW_FLOAT;}
"double" {return TOK_KW_DOUBLE;}
"char" {return TOK_KW_CHAR;}
"void" {return TOK_KW_VOID;}
"if" {return TOK_KW_IF;}
"else" {return TOK_KW_ELSE;}
"while" {return TOK_KW_WHILE;}
"for" {return TOK_KW_FOR;}
"do" {return TOK_KW_DO;}
"return" {return TOK_KW_RETURN;}
"break" {return TOK_KW_BREAK;}
"continue" {return TOK_KW_CONTINUE;}
{ID} {RETURN_TEXT(TOK_IDENTIFIER);}
0[xX]{HEXD}+{ISUF} {RETURN_TEXT(TOK_INT_LITERAL);}
0[0-7]+{ISUF} {RETURN_TEXT(TOK_INT_LITERAL);}
([1-9]{D}*|0){ISUF} {RETURN_TEXT(TOK_INT_LITERAL);}
{D}+\.{D}*({EXP})?{FSUF} {RETURN_TEXT(TOK_FLOAT_LITERAL);}
\.{D}+({EXP})?{FSUF} {RETURN_TEXT(TOK_FLOAT_LITERAL);}
{D}+{EXP}{FSUF} {RETURN_TEXT(TOK_FLOAT_LITERAL);}
({D}|\.{D})[A-Za-z0-9_.]* {diag_add("LEX007",SEV_ERROR,lex_tok_loc,yytext,"Malformed numeric literal '%s'",yytext);return TOK_ERROR;}
\"{STRBODY}*\" {scan_literal_body(yytext+1,yyleng-2);RETURN_TEXT(TOK_STRING_LITERAL);}
\"{STRBODY}* {diag_add("LEX002",SEV_ERROR,lex_tok_loc,yytext,"Unterminated string literal (missing closing quote)");return TOK_ERROR;}
'{CHARBODY}*' {int n=scan_literal_body(yytext+1,yyleng-2);if(n==0){diag_add("LEX004",SEV_ERROR,lex_tok_loc,yytext,"Empty character literal");return TOK_ERROR;}if(n>1){diag_add("LEX005",SEV_ERROR,lex_tok_loc,yytext,"Character literal contains %d characters; expected exactly one",n);return TOK_ERROR;}RETURN_TEXT(TOK_CHAR_LITERAL);}
'{CHARBODY}* {diag_add("LEX003",SEV_ERROR,lex_tok_loc,yytext,"Unterminated character literal (missing closing quote)");return TOK_ERROR;}
"<<=" {return TOK_SHL_ASSIGN;}
">>=" {return TOK_SHR_ASSIGN;}
"+=" {return TOK_PLUS_ASSIGN;}
"-=" {return TOK_MINUS_ASSIGN;}
"*=" {return TOK_STAR_ASSIGN;}
"/=" {return TOK_SLASH_ASSIGN;}
"%=" {return TOK_PERCENT_ASSIGN;}
"&=" {return TOK_AMP_ASSIGN;}
"|=" {return TOK_PIPE_ASSIGN;}
"^=" {return TOK_CARET_ASSIGN;}
"++" {return TOK_INC;}
"--" {return TOK_DEC;}
"==" {return TOK_EQ;}
"!=" {return TOK_NE;}
"<=" {return TOK_LE;}
">=" {return TOK_GE;}
"&&" {return TOK_AND_AND;}
"||" {return TOK_OR_OR;}
"<<" {return TOK_SHL;}
">>" {return TOK_SHR;}
"=" {return TOK_ASSIGN;}
"+" {return TOK_PLUS;}
"-" {return TOK_MINUS;}
"*" {return TOK_STAR;}
"/" {return TOK_SLASH;}
"%" {return TOK_PERCENT;}
"<" {return TOK_LT;}
">" {return TOK_GT;}
"!" {return TOK_NOT;}
"&" {return TOK_AMP;}
"|" {return TOK_PIPE;}
"^" {return TOK_CARET;}
"~" {return TOK_TILDE;}
"?" {return TOK_QUESTION;}
":" {return TOK_COLON;}
"(" {return TOK_LPAREN;}
")" {return TOK_RPAREN;}
"{" {return TOK_LBRACE;}
"}" {return TOK_RBRACE;}
"[" {return TOK_LBRACKET;}
"]" {return TOK_RBRACKET;}
";" {return TOK_SEMICOLON;}
"," {return TOK_COMMA;}
[\x80-\xff]+ {diag_add("LEX001",SEV_ERROR,lex_tok_loc,yytext,"Non-ASCII character(s) are only allowed inside strings, character literals and comments");return TOK_ERROR;}
. {report_invalid_char(yytext);return TOK_ERROR;}
%%
void lexer_init(const char *src,size_t len){cur_line=1;cur_col=1;cur_off=0;memset(&lex_tok_loc,0,sizeof lex_tok_loc);BEGIN(INITIAL);if(scan_buffer){yy_delete_buffer(scan_buffer);scan_buffer=NULL;}scan_buffer=yy_scan_bytes(src,(yy_size_t)len);}
int lexer_next(void){return yylex();}
void lexer_destroy(void){if(scan_buffer){yy_delete_buffer(scan_buffer);scan_buffer=NULL;}yylex_destroy();}
