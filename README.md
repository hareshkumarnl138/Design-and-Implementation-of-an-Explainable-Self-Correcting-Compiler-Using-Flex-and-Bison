# Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair

## Overview

This project aims to build an explainable self-correcting compiler for a defined subset of the C programming language. It combines traditional compiler construction with error diagnosis, correction suggestions, and validation of proposed repairs.

The compiler's core lexical and syntax analysis will use **Flex** and **GNU Bison**. Supporting modules are planned for semantic checks, error explanations, candidate code repairs, and a user interface for exploring compiler phases.

> **Project status:** Initial setup. Features described below are planned and should not be considered implemented until their code and tests are added.

## Objectives

- Tokenize source code using Flex.
- Parse supported C constructs using Bison.
- Report lexical and syntax errors with useful source locations.
- Add semantic checks for selected declarations, scopes, and types.
- Explain diagnosed errors in understandable language.
- Suggest grammar-aware repairs for supported error patterns.
- Let users review proposed changes before applying them.
- Re-analyze corrected source code to verify whether errors are resolved.
- Visualize selected compiler phases and intermediate representations.

## Planned Architecture

1. **Source input** — accept C source code.
2. **Lexical analysis** — recognize tokens with Flex.
3. **Syntax analysis** — validate grammar and build supported syntax structures with Bison.
4. **Semantic analysis** — check declarations, scopes, and selected type rules.
5. **Error diagnosis** — classify errors and explain likely causes.
6. **Code repair** — propose rule-based fixes and optional AI-assisted suggestions.
7. **Validation** — re-run analysis and compilation checks after a fix is applied.
8. **Visualization** — display diagnostic details and compiler-phase output.

## Technology Stack

- **C** — compiler components
- **Flex** — lexical analyzer generator
- **GNU Bison** — parser generator
- **Python / Flask** — planned backend for the web interface
- **HTML, CSS, JavaScript** — planned frontend
- **Graphviz** — optional syntax-tree visualization
- **Optional language-model API** — AI-assisted explanations or candidate suggestions

## Planned Repository Structure

```text
.
├── README.md
├── compiler/
│   ├── lexer.l
│   └── parser.y
├── diagnosis/
├── backend/
├── frontend/
├── tests/
└── docs/
```

The structure may evolve as modules are implemented.

## Getting Started

### Install tools

Install a C compiler, Flex, GNU Bison, and Make using your operating system's package manager.

For Debian/Ubuntu:

```bash
sudo apt update
sudo apt install build-essential flex bison make
```

### Build status

The source files and build configuration have not yet been added. Build and run commands will be documented here once the initial lexer and parser are implemented.

## Testing Plan

The project will use test programs containing:

- Valid C statements and expressions supported by the grammar
- Missing semicolons and unmatched delimiters
- Invalid tokens
- Undeclared or duplicate variables, once semantic analysis is implemented
- Candidate repairs that should succeed, fail, or require user review

Evaluation will measure error detection rate, correction accuracy, successful repair rate, and false or unnecessary correction rate. Results will be reported from actual tests rather than assumed in advance.

## Safety and Repair Policy

Proposed changes should be shown for review before being applied. Ambiguous fixes should be presented as suggestions rather than silently modifying source code. AI-generated suggestions, if enabled, must be validated independently and must not be treated as correct merely because a model produced them.

## Contribution and Development

Development will proceed incrementally: implement and test the lexer, add the parser, introduce semantic checks, build diagnosis and repair rules, and then integrate the interface.

## Project Title

**Design and Implementation of an Explainable Self-Correcting Compiler Using Flex and Bison with Intelligent Error Diagnosis and Automated Code Repair**
