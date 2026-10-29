#include "ast.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
AstNode *ast_new(AstKind kind,const char *text,SrcLoc loc){AstNode*n=calloc(1,sizeof*n);if(!n){fputs("out of memory\n",stderr);exit(2);}n->kind=kind;n->loc=loc;if(text){n->text=strdup(text);if(!n->text){free(n);fputs("out of memory\n",stderr);exit(2);}}return n;}
AstNode *ast_add(AstNode*p,AstNode*c){if(!p)return c;if(!c)return p;if(!p->child)p->child=c;else{AstNode*t=p->child;while(t->next)t=t->next;t->next=c;}return p;}
AstNode *ast_join(AstNode*a,AstNode*b){if(!a)return b;if(!b)return a;AstNode*t=a;while(t->next)t=t->next;t->next=b;return a;}
void ast_free(AstNode*n){while(n){AstNode*next=n->next;ast_free(n->child);free(n->text);free(n->type_name);free(n);n=next;}}
const char*ast_kind_name(AstKind k){static const char*names[]={"translation_unit","declaration","declarator","function","parameter_list","parameter","block","if","while","do_while","for","return","break","continue","expression_statement","assignment","conditional","binary","unary","call","index","identifier","literal","empty"};return (unsigned)k<sizeof names/sizeof names[0]?names[k]:"unknown";}
static void spaces(int n){while(n-->0)putchar(' ');}
static void quoted(const char*s){putchar('"');if(s)for(;*s;s++){unsigned char c=(unsigned char)*s;if(c=='"'||c=='\\'){putchar('\\');putchar(c);}else if(c=='\n')fputs("\\n",stdout);else if(c=='\r')fputs("\\r",stdout);else if(c=='\t')fputs("\\t",stdout);else if(c<0x20)printf("\\u%04x",c);else putchar(c);}putchar('"');}
void ast_print_json(const AstNode*n,int indent){if(!n){fputs("null",stdout);return;}putchar('{');fputs("\n",stdout);spaces(indent+2);fputs("\"kind\": ",stdout);quoted(ast_kind_name(n->kind));if(n->text){fputs(",\n",stdout);spaces(indent+2);fputs("\"text\": ",stdout);quoted(n->text);}if(n->type_name){fputs(",\n",stdout);spaces(indent+2);fputs("\"type\": ",stdout);quoted(n->type_name);}fputs(",\n",stdout);spaces(indent+2);printf("\"loc\": {\"line\": %d, \"column\": %d},\n",n->loc.line,n->loc.col);spaces(indent+2);fputs("\"children\": [",stdout);if(n->child)putchar('\n');for(const AstNode*c=n->child;c;c=c->next){spaces(indent+4);ast_print_json(c,indent+4);if(c->next)putchar(',');putchar('\n');}if(n->child)spaces(indent+2);fputs("]\n",stdout);spaces(indent);putchar('}');}
