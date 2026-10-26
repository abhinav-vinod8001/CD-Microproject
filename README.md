# Malayalam Educational Compiler & Web IDE

A fully functional, online educational IDE and 8-stage compiler pipeline for a Malayalam-based programming language, built with **Python Flask** for the backend and **vanilla HTML5, CSS3, and modern JavaScript** for the frontend.

---

## 🌟 Highlights & Key Capabilities

1. **Natural Malayalam Keywords**: Uses clean Malayalam script (`കാണിക്കുക`, `വായിക്കുക`, `എങ്കിൽ`, `അല്ലെങ്കിൽ`, `ആവർത്തിക്കുക`, `അവസാനിപ്പിക്കുക`, `ശരി`, `തെറ്റ്`) without Manglish, slang, or transliteration.
2. **Real 8-Stage Compiler Pipeline**:
   - **Stage 1: Lexical Analysis**: Complete Malayalam Unicode tokenization (`\u0D00-\u0D7F`).
   - **Stage 2: Syntax Analysis**: Recursive-descent LL(1) style grammar parser.
   - **Stage 3: AST Generation**: Hierarchical abstract syntax tree with tree visualization and JSON export.
   - **Stage 4: Semantic Analysis & Symbol Table**: Static type inference, undeclared variable detection, and diagnostics.
   - **Stage 5: Three-Address Code (TAC)**: Intermediate code generation with temporary registers (`t0`, `t1`) and labels (`L0`, `L1`).
   - **Stage 6: Code Optimization**: Constant folding (e.g. `10 + 20 -> 30`), constant propagation, and algebraic simplifications (`x * 1 -> x`).
   - **Stage 7: Target Code Generation**: Illustrative RISC/MIPS-style Assembly with `.data` and `.text` segments.
   - **Stage 8: Custom Interpreter Execution**: Safe virtual machine execution tracking step limit protections, memory state, and output stream (**Never uses `eval()` or `exec()`**).
3. **Educational Multi-Language Studio (Groq AI & Transpiler)**:
   - Converts the Malayalam program into 3 real-world industrial languages: **Python 3**, **Java (Main.java)**, and **C (C99)**.
   - Uses **Groq API** with modern non-Llama models (**Alibaba Qwen 3.8 27B** and **OpenAI GPT-OSS 120B**) to contextually translate Malayalam keywords AND user-defined Malayalam variables (`തുക` ➔ `sum`, `സംഖ്യ` ➔ `number`, `ഘടകം` ➔ `factorial`, `എണ്ണം` ➔ `count`) into standard English conventions.
   - **Mother-Tongue Tutoring**: Generates comprehensive programming concept explanations written in fluent Malayalam.
   - **Dedicated Non-Destructive Studio**: Opens in a dedicated educational panel/modal so the active Malayalam program is never overwritten.
   - **Replaced Variables & Keywords Dictionary**: Interactive table showing every symbol translated, its classification, and its educational role.
   - **Offline Educational Fallback**: Works seamlessly out of the box even without an API key using the built-in deterministic transpiler.
4. **Malayalam ↔ English Translation**: Instant bidirectional translation preserving comments, variable names, literals, and indentation. Both versions compile and execute identically!
5. **Quick Keyword Insertion Ribbon**: Evaluators and students without a Malayalam keyboard can click chips to insert Malayalam keywords and operators at their exact editor cursor position.
6. **Native Terminal Input & Output**: Standard inline CLI behavior matching normal Python/C programming output (no popups or extra windows).
7. **Dark & Light Mode Support**: Instant theme toggle with localStorage persistence and clean, professional styling modeled after modern developer tools like VS Code and LeetCode.

---

## 📖 Keyword Reference Table

| Malayalam Keyword | English Equivalent | Purpose | Example |
|---|---|---|---|
| `കാണിക്കുക` | `print` | Display output / Standard output | `കാണിക്കുക z` |
| `വായിക്കുക` | `input` | Read input into variable | `വായിക്കുക സംഖ്യ` |
| `എങ്കിൽ` | `if` | Conditional branch | `എങ്കിൽ x > 10` |
| `അല്ലെങ്കിൽ` | `else` | Alternative branch | `അല്ലെങ്കിൽ` |
| `ആവർത്തിക്കുക` | `while` | Loop statement | `ആവർത്തിക്കുക i <= 5` |
| `അവസാനിപ്പിക്കുക` | `end` | End block (if / while) | `അവസാനിപ്പിക്കുക` |
| `ശരി` | `true` | Boolean True | `ഫ്ലാഗ് = ശരി` |
| `തെറ്റ്` | `false` | Boolean False | `ഫ്ലാഗ് = തെറ്റ്` |
| `ഒപ്പം` | `and` | Logical AND | `എങ്കിൽ a > 0 ഒപ്പം b > 0` |
| `അഥവാ` | `or` | Logical OR | `എങ്കിൽ a > 0 അഥവാ b > 0` |
| `അല്ല` | `not` | Logical NOT | `എങ്കിൽ അല്ല ശരി` |

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.9+ installed (`python3 --version`)
- Flask (`pip install -r requirements.txt`)

### 2. Installation
```bash
cd "/Users/apple/Desktop/CD Microproject"
pip install -r requirements.txt
```

### 3. Run the Web IDE
```bash
python3 app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5050
```

### 4. Run Compiler Unit Tests
```bash
python3 -m unittest discover tests -v
```

---

## 📁 Project Architecture

```
CD Microproject/
├── app.py                      # Flask REST API server and route handlers
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── compiler/                   # Modular Python Compiler Pipeline
│   ├── __init__.py             # Package exports
│   ├── tokens.py               # Token definitions & keyword dictionaries
│   ├── lexer.py                # Unicode Malayalam lexical analyzer
│   ├── ast_nodes.py            # AST node classes with tree serialization
│   ├── parser.py               # Recursive-descent syntax analyzer
│   ├── semantic.py             # Semantic analyzer, symbol table & diagnostics
│   ├── codegen_tac.py          # Three-Address Code (TAC) intermediate representation
│   ├── optimizer.py            # Constant folding & algebraic simplification
│   ├── codegen_target.py       # RISC/MIPS Assembly target code generator
│   ├── interpreter.py          # Custom sandboxed virtual machine interpreter
│   ├── translator.py           # Bidirectional Malayalam <-> English translator
│   └── pipeline.py             # 8-stage compiler orchestrator & inspector
├── sample_programs/            # Sample Malayalam programs
│   ├── 01_addition.mal         # Basic arithmetic & print
│   ├── 02_user_input.mal       # User input reading
│   ├── 03_if_else.mal          # Conditional branching
│   ├── 04_while_loop.mal       # While loop accumulation
│   ├── 05_factorial.mal        # Factorial computation
│   └── 06_fibonacci.mal        # Fibonacci series generation
├── static/
│   ├── css/
│   │   └── style.css           # Modern dark-mode styling & layout
│   └── js/
│       ├── editor.js           # Line numbers, caret tracking & shortcuts
│       ├── terminal.js         # Console I/O, execution status & timer
│       ├── inspector.js        # 8-stage pipeline visualization tabs
│       └── app.js              # Application coordinator & event bindings
├── templates/
│   └── index.html              # Modern IDE Single-Page Web UI
└── tests/
    ├── __init__.py
    └── test_compiler.py        # 14 comprehensive unit tests
```

---

## 🔬 The 8-Stage Compiler Pipeline

```
 Source Code (Malayalam / English)
                │
                ▼
 [Stage 1] Lexical Analysis (Tokens: Token Type, Value, Line, Column)
                │
                ▼
 [Stage 2] Syntax Analysis (Recursive-Descent Grammar Checking)
                │
                ▼
 [Stage 3] AST Generation (Hierarchical Node Tree & JSON Representation)
                │
                ▼
 [Stage 4] Semantic Analysis (Symbol Table, Type Inference, Undeclared Checks)
                │
                ▼
 [Stage 5] Intermediate Code Generation (Three-Address Code Quadruples)
                │
                ▼
 [Stage 6] Code Optimization (Constant Folding & Propagation, Identity Rules)
                │
                ▼
 [Stage 7] Target Code Generation (Assembly Listing: .data and .text)
                │
                ▼
 [Stage 8] Execution (Custom Interpreter VM with Step Safety Limits)
                │
                ▼
 Standard Output Console (ടെർമിനൽ)
```

---

## 📝 Example Malayalam Program & Pipeline Trace

### Source Code:
```text
x = 10
y = 20
z = x + y
കാണിക്കുക z
```

### Stage 5: Three-Address Code (TAC)
```text
001:  x = 10                        ; Assign to x
002:  y = 20                        ; Assign to y
003:  t0 = x + y                  
004:  z = t0                        ; Assign to z
005:  print z                       ; Output expression
```

### Stage 7: Target Assembly Code
```assembly
.data
    x           : .word 0
    y           : .word 0
    t0          : .word 0
    z           : .word 0

.text
.global main
main:
    LOAD_IMM  R0, 10
    STORE     R0, [x]
    LOAD_IMM  R0, 20
    STORE     R0, [y]
    LOAD      R0, [x]
    LOAD      R1, [y]
    ADD       R2, R0, R1
    STORE     R2, [t0]
    LOAD      R0, [t0]
    STORE     R0, [z]
    LOAD      R0, [z]
    OUT_VAL   R0              ; Syscall: Display output (കാണിക്കുക)
    HALT
```

### Stage 8: Output
```text
30
```

---

## ⌨️ Keyboard Shortcuts

- <kbd>Ctrl</kbd> + <kbd>Enter</kbd> or <kbd>⌘</kbd> + <kbd>Enter</kbd>: Run Program
- <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>E</kbd>: Translate to English
- <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>M</kbd>: Translate to Malayalam
- <kbd>Tab</kbd>: Insert 4 spaces indent
- Double click or click on AST nodes: Expand / Collapse subtree
