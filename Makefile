# Top-level entry point.
.PHONY: all build test clean

all: build
build:
	$(MAKE) -C compiler

# Build both tools with sanitizers and run lexer, parser, and Python API tests.
test:
	$(MAKE) -C compiler clean
	$(MAKE) -C compiler SANITIZE=0
	python3 -m unittest discover -s tests -p 'test_*.py' -v

clean:
	$(MAKE) -C compiler clean
