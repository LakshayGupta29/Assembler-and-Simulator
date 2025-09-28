# RISC-V Assembler and Simulator

A comprehensive RISC-V assembler and processor simulator written in Python that translates RISC-V assembly code into binary machine code and executes it in a simulated RISC-V environment.

## 🚀 Features

- **Complete RISC-V Assembler**: Converts RISC-V assembly language to 32-bit binary machine code
- **Cycle-Accurate Simulator**: Simulates RISC-V processor execution with register and memory state tracking
- **Multiple Instruction Types**: Supports R-type, I-type, S-type, B-type, and J-type instructions
- **Error Handling**: Comprehensive error checking with detailed error logging
- **Register Support**: Full 32-register RISC-V register file with both numeric and ABI names
- **Memory Simulation**: 128-byte memory space simulation starting at address 0x10000
- **State Output**: Detailed execution trace showing register and memory states after each instruction

## 📋 Supported Instructions

### R-Type Instructions (Register-Register Operations)
- `add rd, rs1, rs2` - Addition
- `sub rd, rs1, rs2` - Subtraction  
- `slt rd, rs1, rs2` - Set less than
- `srl rd, rs1, rs2` - Shift right logical
- `or rd, rs1, rs2` - Bitwise OR
- `and rd, rs1, rs2` - Bitwise AND

### I-Type Instructions (Immediate Operations)
- `addi rd, rs1, imm` - Add immediate
- `lw rd, offset(rs1)` - Load word from memory
- `jalr rd, rs1, offset` - Jump and link register

### S-Type Instructions (Store Operations)
- `sw rs2, offset(rs1)` - Store word to memory

### B-Type Instructions (Branch Operations)
- `beq rs1, rs2, offset` - Branch if equal
- `bne rs1, rs2, offset` - Branch if not equal
- `blt rs1, rs2, offset` - Branch if less than

### J-Type Instructions (Jump Operations)
- `jal rd, offset` - Jump and link

## 🔧 Requirements

- Python 3.6 or higher
- No external dependencies required

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/LakshayGupta29/Assembler-and-Simulator.git
cd Assembler-and-Simulator
```

2. Ensure Python 3 is installed:
```bash
python3 --version
```

## 🎯 Usage

### Assembler

Convert RISC-V assembly code to binary machine code:

```bash
python3 Assembler.py <input_assembly_file> <output_binary_file>
```

**Example:**
```bash
python3 Assembler.py program.asm program.bin
```

### Simulator

Execute binary machine code and generate execution trace:

```bash
python3 Simulator.py <input_binary_file> <output_trace_file>
```

**Example:**
```bash
python3 Simulator.py program.bin execution_trace.txt
```

## 📝 Assembly Language Format

### Basic Syntax
- One instruction per line
- Labels are supported with colon syntax: `label:`
- Instructions can follow labels on the same line
- Comments are not supported in this version
- Case-sensitive instruction and register names

### Register Names
The assembler supports both numeric (`x0`, `x1`, ..., `x31`) and ABI register names:

| ABI Name | Numeric | Description |
|----------|---------|-------------|
| `zero` | `x0` | Hardwired zero |
| `ra` | `x1` | Return address |
| `sp` | `x2` | Stack pointer |
| `gp` | `x3` | Global pointer |
| `tp` | `x4` | Thread pointer |
| `t0-t2` | `x5-x7` | Temporary registers |
| `s0/fp` | `x8` | Saved register/Frame pointer |
| `s1` | `x9` | Saved register |
| `a0-a7` | `x10-x17` | Function arguments/return values |
| `s2-s11` | `x18-x27` | Saved registers |
| `t3-t6` | `x28-x31` | Temporary registers |

### Immediate Values
The assembler supports multiple number formats:
- **Decimal**: `42`, `-15`
- **Hexadecimal**: `0x2A`, `0xFF`  
- **Binary**: `0b101010`
- **Octal**: `0o52`

### Memory Addressing
Memory operations use the format `offset(register)`:
```assembly
lw x1, 4(x2)     # Load word from address (x2 + 4)
sw x3, 0(x4)     # Store word to address (x4 + 0)
```

## 💡 Example Programs

### Example 1: Basic Arithmetic (`examples/arithmetic.asm`)
```assembly
addi x1, x0, 10
addi x2, x0, 20  
add x3, x1, x2
sw x3, 0(x2)
lw x4, 0(x2)
beq x0, x0, 0
```
This program:
1. Loads 10 into x1 and 20 into x2
2. Adds them, storing result (30) in x3
3. Stores x3 to memory and loads it back into x4
4. Halts with an infinite loop

### Example 2: Loop with Labels (`examples/loop.asm`)
```assembly
addi x1, x0, 5
addi x2, x0, 0
loop:
add x2, x2, x1
addi x1, x1, -1
bne x1, x0, loop
beq x0, x0, 0
```
This program calculates the sum 5+4+3+2+1 = 15 using a loop.

### Example 3: Fibonacci Sequence (`examples/fibonacci.asm`)
```assembly
addi x1, x0, 0
addi x2, x0, 1
addi x3, x0, 8
addi x4, x0, 0
fib_loop:
add x5, x1, x2
or x1, x2, x0
or x2, x5, x0
addi x4, x4, 1
sw x1, 0(x4)
blt x4, x3, fib_loop
beq x0, x0, 0
```
This program generates the first 8 Fibonacci numbers and stores them in memory.

## 📊 Simulator Output Format

The simulator generates a detailed execution trace with the following format:

```
0b<program_counter> 0b<reg0> 0b<reg1> ... 0b<reg31>
```

Each line represents the processor state after executing one instruction:
- **Program Counter**: Current instruction address (in binary)
- **Registers**: All 32 register values (in binary with '0b' prefix)

After program completion, memory contents are dumped:
```
0x<address>:0b<32-bit_value>
```

## 🏗️ Architecture Details

### Memory Layout
- **Instruction Memory**: Program instructions loaded starting at address 0x00000000
- **Data Memory**: 128 bytes allocated from 0x00010000 to 0x0001007C
- **Register File**: 32 general-purpose registers, with x0 hardwired to zero
- **Special Initialization**: Register x2 (sp) initialized to 380 for stack operations

### Processor Features
- **32-bit Architecture**: All registers and memory locations are 32 bits wide
- **Word-Addressed Memory**: Memory operations work on 32-bit words
- **Two's Complement Arithmetic**: Signed integer operations use two's complement
- **Branch Target Calculation**: Relative addressing for branches and jumps
- **Cycle-by-Cycle Execution**: Each instruction updates processor state atomically

## 🚨 Error Handling

The assembler provides comprehensive error checking:

- **Syntax Errors**: Invalid instruction formats and operand counts
- **Register Errors**: Unknown or invalid register names
- **Label Errors**: Undefined labels and circular references  
- **Range Errors**: Immediate values outside valid ranges
- **Memory Errors**: Invalid memory addressing formats

Errors are logged to `error_log.txt` with line numbers for easy debugging.

## 🔍 Instruction Encoding

The assembler generates standard RISC-V 32-bit instruction encodings:

### R-Type Format
```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
funct7   rs2     rs1    funct3   rd   opcode
```

### I-Type Format  
```
[31:20] [19:15] [14:12] [11:7] [6:0]
 imm     rs1    funct3   rd   opcode
```

### S-Type Format
```
[31:25] [24:20] [19:15] [14:12] [11:7] [6:0]
imm[11:5] rs2    rs1    funct3 imm[4:0] opcode
```

### B-Type Format
```
[31] [30:25] [24:20] [19:15] [14:12] [11:8] [7] [6:0]
imm[12] imm[10:5] rs2   rs1   funct3 imm[4:1] imm[11] opcode
```

### J-Type Format
```
[31] [30:21] [20] [19:12] [11:7] [6:0]
imm[20] imm[10:1] imm[11] imm[19:12] rd opcode
```

## 🧪 Testing

### Automated Testing
Use the provided test script to validate all examples:

```bash
python3 test_examples.py
```

This script will:
- Assemble all programs in the `examples/` directory
- Run simulations for each program
- Generate output files in the `test_output/` directory
- Report success/failure for each test

### Manual Testing
Test the tools with the provided examples:

1. Assemble one of the example programs:
```bash
python3 Assembler.py examples/arithmetic.asm arithmetic.bin
```

2. Simulate execution:
```bash
python3 Simulator.py arithmetic.bin output.txt
```

3. View the results:
```bash
cat output.txt
```

### Running All Examples
```bash
# Test arithmetic operations
python3 Assembler.py examples/arithmetic.asm arithmetic.bin
python3 Simulator.py arithmetic.bin arithmetic_trace.txt

# Test loop with branches  
python3 Assembler.py examples/loop.asm loop.bin
python3 Simulator.py loop.bin loop_trace.txt

# Test Fibonacci sequence
python3 Assembler.py examples/fibonacci.asm fibonacci.bin
python3 Simulator.py fibonacci.bin fibonacci_trace.txt

# Test comprehensive instruction set
python3 Assembler.py examples/test_all_instructions.asm test_all.bin
python3 Simulator.py test_all.bin test_all_trace.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- RISC-V Foundation for the instruction set architecture specification
- Computer architecture textbooks and resources that inspired this implementation

## 📞 Support

If you encounter any issues or have questions:
1. Check the error log file for assembly errors
2. Verify your assembly syntax matches the supported instruction formats
3. Ensure all labels are properly defined before use
4. Open an issue on GitHub for bugs or feature requests