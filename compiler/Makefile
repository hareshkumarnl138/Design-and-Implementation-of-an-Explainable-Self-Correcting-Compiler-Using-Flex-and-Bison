# Build the compiler front-end. Usage: make; make SANITIZE=1; make clean
CC ?= cc
FLEX ?= flex
BUILD := build
CFLAGS ?= -std=c11 -O2 -g -Wall -Wextra -Wpedantic
GENFLAGS ?= -std=gnu11 -O2 -g -Wall
ifdef SANITIZE
CFLAGS += -fsanitize=address,undefined -fno-omit-frame-pointer
GENFLAGS += -fsanitize=address,undefined -fno-omit-frame-pointer
LDFLAGS += -fsanitize=address,undefined
endif
SRCS := diag.c json.c tokens.c lexer_main.c
OBJS := $(SRCS:%.c=$(BUILD)/%.o) $(BUILD)/lex.yy.o
LEXER := $(BUILD)/lexer
.PHONY: all clean
all: $(LEXER)
$(LEXER): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^
$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -MMD -MP -I. -c -o $@ $<
$(BUILD)/lex.yy.c: lexer.l | $(BUILD)
	$(FLEX) -o $@ $<
$(BUILD)/lex.yy.o: $(BUILD)/lex.yy.c
	$(CC) $(GENFLAGS) -MMD -MP -I. -c -o $@ $<
$(BUILD):
	mkdir -p $@
clean:
	rm -rf $(BUILD)
-include $(OBJS:.o=.d)
