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