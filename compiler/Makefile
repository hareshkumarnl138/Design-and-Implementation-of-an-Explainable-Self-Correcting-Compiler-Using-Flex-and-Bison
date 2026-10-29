.DEFAULT_GOAL := all

# Build lexer and Bison parser. Usage: make; make test; make clean
CC ?= cc
FLEX ?= flex
BISON ?= bison
BUILD := build
CFLAGS ?= -D_POSIX_C_SOURCE=200809L -std=c11 -O2 -g -Wall -Wextra -Wpedantic

GENFLAGS ?= -std=gnu11 -O2 -Wall

ifeq ($(SANITIZE),1)
CFLAGS += -fsanitize=address,undefined -fno-omit-frame-pointer
GENFLAGS += -fsanitize=address,undefined -fno-omit-frame-pointer
LDFLAGS += -fsanitize=address,undefined
endif

COMMON_OBJS := $(BUILD)/diag.o
LEXER_OBJS := $(COMMON_OBJS) $(BUILD)/json.o $(BUILD)/tokens.o $(BUILD)/lexer_main.o $(BUILD)/lex.yy.o
PARSER_OBJS := $(COMMON_OBJS) $(BUILD)/ast.o $(BUILD)/semantic.o $(BUILD)/parser_main.o $(BUILD)/parser.tab.o $(BUILD)/lex.parser.o
LEXER := $(BUILD)/lexer
PARSER := $(BUILD)/parser

PHONY: all clean
all: $(LEXER) $(PARSER)

$(LEXER): $(LEXER_OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

$(PARSER): $(PARSER_OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -MMD -MP -I. -I$(BUILD) -c -o $@ $<

$(BUILD)/lex.yy.c: lexer.l | $(BUILD)
	$(FLEX) -o $@ $<

$(BUILD)/lex.yy.o: $(BUILD)/lex.yy.c
	$(CC) $(GENFLAGS) -MMD -MP -I. -I$(BUILD) -c -o $@ $<

$(BUILD)/lex.parser.o: $(BUILD)/lex.yy.c $(BUILD)/parser.tab.h
	$(CC) $(GENFLAGS) -DPARSER_BUILD -MMD -MP -I. -I$(BUILD) -c -o $@ $<

$(BUILD)/parser.tab.c: parser.y | $(BUILD)
	$(BISON) -d -Wall -o $@ $<

$(BUILD)/parser.tab.h: $(BUILD)/parser.tab.c
	@test -f $@

$(BUILD)/parser.tab.o: $(BUILD)/parser.tab.c $(BUILD)/parser.tab.h
	$(CC) $(CFLAGS) -MMD -MP -I. -I$(BUILD) -c -o $@ $<
.DELETE_ON_ERROR:

.PHONY: FORCE
FORCE:

.SECONDARY:

$(BUILD): FORCE
	mkdir -p $@

clean:
	rm -rf $(BUILD)

-include $(LEXER_OBJS:.o=.d) $(PARSER_OBJS:.o=.d)
