#include "tokens.h"
static const struct { int id; const char *name; TokenCategory cat; } TABLE[] = {
#define X(id, name, cat) { id, name, cat },
TOKEN_LIST(X)
#undef X
};
#define TABLE_SIZE (sizeof TABLE / sizeof TABLE[0])
const char *token_name(int tok) { if(tok==TOK_EOF)return "EOF"; for(unsigned i=0;i<TABLE_SIZE;i++)if(TABLE[i].id==tok)return TABLE[i].name;return "UNKNOWN"; }
TokenCategory token_category(int tok) { for(unsigned i=0;i<TABLE_SIZE;i++)if(TABLE[i].id==tok)return TABLE[i].cat;return CAT_ERROR; }
const char *token_category_name(TokenCategory cat) { switch(cat){case CAT_KEYWORD:return "keyword";case CAT_IDENTIFIER:return "identifier";case CAT_LITERAL:return "literal";case CAT_OPERATOR:return "operator";case CAT_PUNCTUATOR:return "punctuator";case CAT_PREPROCESSOR:return "preprocessor";case CAT_COMMENT:return "comment";case CAT_ERROR:return "error";}return "unknown"; }
