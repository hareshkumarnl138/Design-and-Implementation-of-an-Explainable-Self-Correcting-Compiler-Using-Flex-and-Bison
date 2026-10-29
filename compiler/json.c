#include "json.h"
#include <stdint.h>
static size_t utf8_seq_len(const unsigned char *s, size_t n) {
 if (s[0] < 0x80) return 1; size_t need; unsigned cp;
 if ((s[0]&0xE0)==0xC0) {need=2;cp=s[0]&0x1F;} else if ((s[0]&0xF0)==0xE0) {need=3;cp=s[0]&0x0F;} else if ((s[0]&0xF8)==0xF0) {need=4;cp=s[0]&7;} else return 0;
 if(n<need)return 0; for(size_t i=1;i<need;i++){if((s[i]&0xC0)!=0x80)return 0;cp=(cp<<6)|(s[i]&0x3F);}
 if((need==2&&cp<0x80)||(need==3&&cp<0x800)||(need==4&&(cp<0x10000||cp>0x10FFFF))||(cp>=0xD800&&cp<=0xDFFF))return 0; return need;
}
void json_write_string(FILE *out,const char *str,size_t len){const unsigned char*s=(const unsigned char*)str;fputc('"',out);for(size_t i=0;i<len;){unsigned char c=s[i];if(c=='"'){fputs("\\\"",out);i++;}else if(c=='\\'){fputs("\\\\",out);i++;}else if(c=='\n'){fputs("\\n",out);i++;}else if(c=='\r'){fputs("\\r",out);i++;}else if(c=='\t'){fputs("\\t",out);i++;}else if(c<0x20||c==0x7F){fprintf(out,"\\u%04x",c);i++;}else if(c<0x80){fputc(c,out);i++;}else{size_t n=utf8_seq_len(s+i,len-i);if(!n){fputs("\\ufffd",out);i++;}else{fwrite(s+i,1,n,out);i+=n;}}}fputc('"',out);}
