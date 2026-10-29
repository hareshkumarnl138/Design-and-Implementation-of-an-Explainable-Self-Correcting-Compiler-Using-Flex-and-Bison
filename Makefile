# Top-level entry point.  Delegates to the sub-projects.
.PHONY: all build test clean

all: build

build:
	$(MAKE) -C compiler

# Tests run against a sanitizer build so memory errors fail the suite.
test:
	$(MAKE) -C compiler clean
	$(MAKE) -C compiler SANITIZE=1
	python3 -m unittest discover -s tests -p 'test_*.py' -v

clean:
	$(MAKE) -C compiler clean
