import sys

memory_space = {}
cpu_registers = {}
program_counter = '0' * 32 

for i in range(0, 128, 4):
    addr = '0x' + format(0x10000 + i, '08X')
    memory_space[addr] = '0b' + '0' * 32

for i in range(32):
    reg_name = format(i, '05b')
    if reg_name == '00010':  
        cpu_registers[reg_name] = '0b' + format(380, '032b') 
    else:
        cpu_registers[reg_name] = '0b' + '0' * 32

def to_binary(value, bit_width):
    if value < 0:
        value = (1 << bit_width) + value
    return format(value, f'0{bit_width}b')

def to_decimal(binary_str):
    if binary_str[0] == '1':
        inverted = ''.join('1' if bit == '0' else '0' for bit in binary_str)
        return -1 * (int(inverted, 2) + 1)
    else:
        return int(binary_str, 2)

def bit_extend_signed(binary_val, target_width):

    sign_bit = binary_val[0]
    extension = sign_bit * (target_width - len(binary_val))
    return extension + binary_val

def add_binary_values(a, b):

    val_a = to_decimal(a)
    val_b = to_decimal(b)
    result = val_a + val_b
    return to_binary(result, 32)

def subtract_binary_values(a, b):

    val_a = to_decimal(a)
    val_b = to_decimal(b)
    result = val_a - val_b
    return to_binary(result, 32)

def execute_arithmetic(instr):

    global program_counter
    

    rd = instr[20:25]
    rs1 = instr[12:17]
    rs2 = instr[7:12]
    funct3 = instr[17:20]
    funct7 = instr[0:7]
    
    val1 = cpu_registers[rs1][2:]
    val2 = cpu_registers[rs2][2:]
    
    if funct3 == '000':
        if funct7 == '0000000':  # ADD
            result = add_binary_values(val1, val2)
            cpu_registers[rd] = '0b' + result
        elif funct7 == '0100000':  # SUB
            result = subtract_binary_values(val1, val2)
            cpu_registers[rd] = '0b' + result
    elif funct3 == '101':  # SRL (Shift Right Logical)
        shift_amount = int(val2[-5:], 2)
        value = int(val1, 2)
        result = value >> shift_amount
        cpu_registers[rd] = '0b' + format(result, '032b')
    elif funct3 == '010':  # SLT (Set Less Than)
        num1 = to_decimal(val1)
        num2 = to_decimal(val2)
        if num1 < num2:
            cpu_registers[rd] = '0b' + '0'*31 + '1'
        else:
            cpu_registers[rd] = '0b' + '0'*32
    elif funct3 == '110':  # OR
        result = int(val1, 2) | int(val2, 2)
        cpu_registers[rd] = '0b' + format(result, '032b')
    elif funct3 == '111':  # AND
        result = int(val1, 2) & int(val2, 2)
        cpu_registers[rd] = '0b' + format(result, '032b')
    
    program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')

def execute_immediate(instr):
    global program_counter
    
    rd = instr[-12:-7]
    rs1 = instr[-20:-15]
    funct3 = instr[-15:-12]
    imm = instr[-32:-20]
    opcode = instr[-7:]
    
    rs1_val = cpu_registers[rs1][2:]
    
    if funct3 == '010':  # LW (Load Word)
        imm_extended = bit_extend_signed(imm, 32)
        addr_binary = add_binary_values(rs1_val, imm_extended)
        addr_hex = '0x' + format(int(addr_binary, 2), '08X')
        
        cpu_registers[rd] = memory_space[addr_hex]
        program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')
    
    elif funct3 == '000' and opcode == '0010011':  # ADDI
        imm_extended = bit_extend_signed(imm, 32)
        result = add_binary_values(rs1_val, imm_extended)
        cpu_registers[rd] = '0b' + result
        program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')
    
    else:  # JALR
        next_pc = add_binary_values(program_counter, '00000000000000000000000000000100')
        cpu_registers[rd] = '0b' + next_pc
        
        imm_extended = bit_extend_signed(imm, 32)
        target = add_binary_values(rs1_val, imm_extended)
        program_counter = target[:-1] + '0'  # Set LSB to 0
        
        cpu_registers['00000'] = '0b' + '0'*32

def execute_store(instr):
    global program_counter
    
    imm_low = instr[-12:-7]
    rs1 = instr[-20:-15]
    rs2 = instr[-25:-20]
    imm_high = instr[-32:-25]
    imm = imm_high + imm_low
    
    rs1_val = cpu_registers[rs1][2:]
    imm_extended = bit_extend_signed(imm, 32)
    addr_binary = add_binary_values(rs1_val, imm_extended)
    addr_hex = '0x' + format(int(addr_binary, 2), '08X')
    
    memory_space[addr_hex] = cpu_registers[rs2]
    
    program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')

def execute_branch(instr):
    global program_counter
    
    funct3 = instr[17:20]
    rs1 = instr[12:17]
    rs2 = instr[7:12]
    imm_parts = instr[0] + instr[24] + instr[1:7] + instr[20:24] + '0'
    
    rs1_val = cpu_registers[rs1]
    rs2_val = cpu_registers[rs2]
    
    imm_extended = bit_extend_signed(imm_parts, 32)
    imm_val = to_decimal(imm_extended) // 4
    current_pc = to_decimal(program_counter) // 4
    
    if rs1_val == '0b' + '0'*32 and rs2_val == '0b' + '0'*32 and imm_val == 0:
        return
    
    if imm_val == 0:
        program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')
        return
    
    target_pc = (current_pc + imm_val) * 4
    
    if funct3 == '000':  # BEQ
        if rs1_val == rs2_val and rs1 != '00000': 
            program_counter = to_binary(target_pc, 32)
            return
    elif funct3 == '001':  # BNE
        if rs1_val != rs2_val: 
            program_counter = to_binary(target_pc, 32)
            return
    
    program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')

def execute_jump(instr):
    global program_counter
    
    rd = instr[-12:-7]
    imm_parts = instr[0] + instr[12:20] + instr[11] + instr[1:11] + '0'
    
    next_pc = add_binary_values(program_counter, '00000000000000000000000000000100')
    cpu_registers[rd] = '0b' + next_pc
    
    imm_extended = bit_extend_signed(imm_parts, 32)
    imm_val = to_decimal(imm_extended) // 4
    current_pc = to_decimal(program_counter) // 4
    target_pc = (current_pc + imm_val) * 4
    
    program_counter = to_binary(target_pc, 32)
    program_counter = program_counter[:-1] + '0'  # Clear LSB

def exec_unknown(instr):
    global program_counter
    print(f"Error: Unknown instruction {instr}")
    program_counter = add_binary_values(program_counter, '00000000000000000000000000000100')

instruction_map = {
    '0110011': execute_arithmetic,  # R-type
    '0000011': execute_immediate,   # I-type (load)
    '0010011': execute_immediate,   # I-type (immediate)
    '1100111': execute_immediate,   # I-type (jalr)
    '0100011': execute_store,       # S-type
    '1100011': execute_branch,      # B-type
    '1101111': execute_jump,        # J-type
}

def run_simulation(program, output_file):
    with open(output_file, 'w') as output:
        while True:
            pc_decimal = to_decimal(program_counter) // 4
            instruction = program[pc_decimal]
            
            opcode = instruction[-7:]
            instruction_handler = instruction_map.get(opcode, exec_unknown)
            instruction_handler(instruction)
            
            cpu_registers['00000'] = '0b' + '0'*32
            
            output.write('0b' + program_counter + ' ')
            for reg_key in cpu_registers:
                output.write(cpu_registers[reg_key] + ' ')
            output.write('\n')
            
            if instruction == '00000000000000000000000001100011':
                break
        
        for addr in sorted(memory_space.keys()):
            if '0x00010000' <= addr <= '0x0001007C':
                output.write(f"{addr}:{memory_space[addr]}\n")

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r') as file:
        program = [line.strip() for line in file.readlines()]
    
    run_simulation(program, output_file)

main()