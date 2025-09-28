import sys

# mapping register names to their corresponding numbers
REGISTERS = {
    "zero": 0, "x0": 0,
    "ra": 1, "x1": 1,
    "sp": 2, "x2": 2,
    "gp": 3, "x3": 3,
    "tp": 4, "x4": 4,
    "t0": 5, "x5": 5,
    "t1": 6, "x6": 6,
    "t2": 7, "x7": 7,
    "s0": 8, "fp": 8, "x8": 8,
    "s1": 9, "x9": 9,
    "a0": 10, "x10": 10,
    "a1": 11, "x11": 11,
    "a2": 12, "x12": 12,
    "a3": 13, "x13": 13,
    "a4": 14, "x14": 14,
    "a5": 15, "x15": 15,
    "a6": 16, "x16": 16,
    "a7": 17, "x17": 17,
    "s2": 18, "x18": 18,
    "s3": 19, "x19": 19,
    "s4": 20, "x20": 20,
    "s5": 21, "x21": 21,
    "s6": 22, "x22": 22,
    "s7": 23, "x23": 23,
    "s8": 24, "x24": 24,
    "s9": 25, "x25": 25,
    "s10": 26, "x26": 26,
    "s11": 27, "x27": 27,
    "t3": 28, "x28": 28,
    "t4": 29, "x29": 29,
    "t5": 30, "x30": 30,
    "t6": 31, "x31": 31,
}

# R-Type Operators
R_TYPE = {
    "add": {"opcode": "0110011", "funct3": "000", "funct7": "0000000"},
    "sub": {"opcode": "0110011", "funct3": "000", "funct7": "0100000"},
    "slt": {"opcode": "0110011", "funct3": "010", "funct7": "0000000"},
    "srl": {"opcode": "0110011", "funct3": "101", "funct7": "0000000"},
    "or":  {"opcode": "0110011", "funct3": "110", "funct7": "0000000"},
    "and": {"opcode": "0110011", "funct3": "111", "funct7": "0000000"},
}
# I-Type Operators
I_TYPE = {
    "addi": {"opcode": "0010011", "funct3": "000"},
    "lw":   {"opcode": "0000011", "funct3": "010"},
    "jalr": {"opcode": "1100111", "funct3": "000"},
}
# S-Type Operators
S_TYPE = {
    "sw": {"opcode": "0100011", "funct3": "010"},
}
# B-Type Operators
B_TYPE = {
    "beq": {"opcode": "1100011", "funct3": "000"},
    "bne": {"opcode": "1100011", "funct3": "001"},
    "blt": {"opcode": "1100011", "funct3": "100"},
}
# J-Type Operators
J_TYPE = {
    "jal": {"opcode": "1101111"},
}

# Convert integer to binary (using two's complement for negatives)
def inbin(val, bits):
    n = val
    if val == 0:
        return '0' * bits
    if val < 0:
        max_val = 2**bits - 1
        n = max_val + n + 1
    s = ''
    while n > 0:
        s += str(n % 2)
        n //= 2
    s = s[::-1]
    if len(s) <= bits:
        return '0' * (bits - len(s)) + s
    return s[len(s) - bits:]

# To handle different formats.
def Immediate(literal):
    literal = literal.strip()
    sign = 1
    if literal.startswith('-'):
        sign = -1
        literal = literal[1:]
    if literal.startswith(('0x', '0X')):
        value = int(literal, 16)  # Hexadecimal
    elif literal.startswith(('0b', '0B')):
        value = int(literal, 2)   # Binary
    elif literal.startswith(('0o', '0O')):
        value = int(literal, 8)   # Octal
    else:
        value = int(literal, 10)  # Decimal
    return sign * value

# Function for getting immediate and register from memory operand.
def _address(tar_mem):
    front = tar_mem.find('(')
    back = tar_mem.find(')')
    assert not (front == -1 or back == -1 or back < front), "Malformed target memory: " + tar_mem
    imm_str = tar_mem[:front].strip()
    reg_str = tar_mem[front+1:back].strip()
    return imm_str, reg_str

# To encode R-Type Instructions.
def R_code(instr, rd, rs1, rs2):
    info = R_TYPE[instr]
    return (info["funct7"] + inbin(rs2, 5) + inbin(rs1, 5) + info["funct3"] + inbin(rd, 5) + info["opcode"])

# To encode I-Type Instructions.
def I_code(instr, rd, rs1, imm):
    info = I_TYPE[instr]
    return (inbin(imm, 12) + inbin(rs1, 5) + info["funct3"] + inbin(rd, 5) + info["opcode"])

# To encode S-Type Instructions.
def S_code(instr, rs1, rs2, imm):
    info = S_TYPE[instr]
    imm_bin = inbin(imm, 12)
    imm_high = imm_bin[:7]   
    imm_low  = imm_bin[7:]    
    return (imm_high + inbin(rs2, 5) + inbin(rs1, 5) + info["funct3"] + imm_low + info["opcode"])

# To encode B-Type Instructions.
def B_code(instr, rs1, rs2, offset):
    info = B_TYPE[instr]
    assert offset % 2 == 0, "Branch offset must be even"
    imm_str = inbin(offset, 13)
    return (imm_str[0] + imm_str[2:8] + inbin(rs2, 5) + inbin(rs1, 5) +
            info["funct3"] + imm_str[8:12] + imm_str[1] + info["opcode"])

# To encode J-Type Instructions.
def J_code(rd, offset):
    info = J_TYPE["jal"]
    assert offset % 2 == 0, "JAL offset must be even"
    imm_str = inbin(offset, 21)
    return (imm_str[0] + imm_str[10:20] + imm_str[9] +
            imm_str[1:9] + inbin(rd, 5) + info["opcode"])

# For getting register number.
def reg_mem(reg_str):
    reg_str = reg_str.strip()
    assert reg_str in REGISTERS, "Unknown register: " + reg_str
    return REGISTERS[reg_str]

# To check if value is a number.
def is_numeric(s):
    s = s.strip()
    return s and (s[0] == '-' or s[0].isdigit())

# The main function that reads and translates assembly code to the final binary output.
def assemble(input_file, output_file):
    errors = []  # To collect error messages

    # Read lines and keep track of the original line numbers.
    with open(input_file, 'r') as f:
        raw_lines = f.readlines()
    lines = [(i+1, line.strip()) for i, line in enumerate(raw_lines) if line.strip() != ""]

    label_addresses = {}
    address = 0
    processed_lines = []  

    # Labeling with their address. For lines with a label and an instruction on the same line,
    # we keep the original line number.
    for lineno, line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            label = parts[0].strip()
            label_addresses[label] = address
            if parts[1].strip() != "":
                instr_line = parts[1].strip()
                processed_lines.append((address, instr_line, lineno))
                address += 4
        else:
            processed_lines.append((address, line, lineno))
            address += 4

    binary_lines = []
    # Process each line and catch errors with the corresponding line number.
    for addr, line, lineno in processed_lines:
        tok = line.replace(',', ' ').split()
        if not tok:
            continue
        operator = tok[0]
        try:
            if operator in S_TYPE:
                assert len(tok) == 3, "Incorrect number of operands for sw"
                rs2 = reg_mem(tok[1])
                imm_str, reg_str = _address(tok[2])
                imm = Immediate(imm_str)
                rs1 = reg_mem(reg_str)
                binary_line = S_code(operator, rs1, rs2, imm)
            elif operator in I_TYPE:
                if operator == "lw":
                    assert len(tok) == 3, "Incorrect number of operands for lw"
                    rd = reg_mem(tok[1])
                    imm_str, reg_str = _address(tok[2])
                    imm = Immediate(imm_str)
                    rs1 = reg_mem(reg_str)
                    binary_line = I_code(operator, rd, rs1, imm)
                else:
                    assert len(tok) == 4, "Incorrect number of operands for I-type"
                    rd = reg_mem(tok[1])
                    rs1 = reg_mem(tok[2])
                    imm = Immediate(tok[3])
                    binary_line = I_code(operator, rd, rs1, imm)
            elif operator in B_TYPE:
                assert len(tok) == 4, "Incorrect number of operands for B-type"
                rs1 = reg_mem(tok[1])
                rs2 = reg_mem(tok[2])
                target = tok[3]
                if is_numeric(target):
                    offset = Immediate(target)
                else:
                    assert target in label_addresses, "Undefined label: " + target
                    target_addr = label_addresses[target]
                    offset = target_addr - addr
                binary_line = B_code(operator, rs1, rs2, offset)
            elif operator in J_TYPE:
                assert len(tok) == 3, "Incorrect number of operands for J-type"
                rd = reg_mem(tok[1])
                target = tok[2]
                if is_numeric(target):
                    offset = Immediate(target)
                else:
                    assert target in label_addresses, "Undefined label: " + target
                    target_addr = label_addresses[target]
                    offset = target_addr - addr
                binary_line = J_code(rd, offset)
            elif operator in R_TYPE:
                assert len(tok) == 4, "Incorrect number of operands for R-type"
                rd = reg_mem(tok[1])
                rs1 = reg_mem(tok[2])
                rs2 = reg_mem(tok[3])
                binary_line = R_code(operator, rd, rs1, rs2)
            else:
                raise ValueError("Unknown instruction: " + operator)
            binary_lines.append(binary_line)
        except Exception as e:
            errors.append("Error on line {}: {}".format(lineno, e))
            # Continue processing remaining lines
            continue

    # Write binary lines to the output file.
    with open(output_file, 'w') as f:
        for bline in binary_lines:
            f.write(bline + "\n")

    # If errors occurred, write them to an error log file.
    if errors:
        with open("error_log.txt", "w") as ef:
            for error in errors:
                ef.write(error + "\n")
        print("Assembly completed with errors. See error_log.txt for details.")
    else:
        print("Assembly completed. Output goes to", output_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: assembler.py <input_asm_file> <output_bin_file>")
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2])
