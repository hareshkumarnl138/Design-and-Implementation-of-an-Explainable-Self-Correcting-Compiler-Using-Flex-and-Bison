#include "diag.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static Diagnostic *items; static size_t count,capacity; static int errors,warnings;
void diag_reset(void){free(items);items=NULL;count=capacity=0;errors=warnings=0;}
void diag_add(const char *code,Severity sev,SrcLoc loc,const char *lexeme,const char *fmt,...){if(count==capacity){size_t ncap=capacity?capacity*2:16;Diagnostic*n=realloc(items,ncap*sizeof*n);if(!n){fputs("out of memory\n",stderr);exit(2);}items=n;capacity=ncap;}Diagnostic*d=&items[count++];memset(d,0,sizeof*d);snprintf(d->code,sizeof d->code,"%s",code);d->severity=sev;d->loc=loc;if(lexeme){size_t n=strlen(lexeme);if(n>=sizeof d->lexeme){memcpy(d->lexeme,lexeme,sizeof d->lexeme-4);memcpy(d->lexeme+sizeof d->lexeme-4,"...",4);}else memcpy(d->lexeme,lexeme,n+1);}va_list ap;va_start(ap,fmt);vsnprintf(d->message,sizeof d->message,fmt,ap);va_end(ap);if(sev==SEV_ERROR)errors++;else warnings++;}
size_t diag_count(void){return count;} const Diagnostic*diag_get(size_t i){return i<count?&items[i]:NULL;} int diag_error_count(void){return errors;} int diag_warning_count(void){return warnings;}
