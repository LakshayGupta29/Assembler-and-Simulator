addi x1, x0, 10
addi x2, x0, 20
add x3, x1, x2
sw x3, 0(x2)
lw x4, 0(x2)
beq x0, x0, 0