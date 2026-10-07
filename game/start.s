.syntax unified
.cpu arm7tdmi
.section .header,"ax"
.arm
.global _start
_start:
    b startup
    .space 188
.section .text.startup,"ax"
startup:
    mov r0, #0xdf
    msr cpsr_c, r0
    ldr sp, =0x03007e00
    ldr r0, =__data_load
    ldr r1, =__data_start
    ldr r2, =__data_end
1:  cmp r1, r2
    ldrlo r3, [r0], #4
    strlo r3, [r1], #4
    blo 1b
    ldr r1, =__bss_start
    ldr r2, =__bss_end
    mov r3, #0
2:  cmp r1, r2
    strlo r3, [r1], #4
    blo 2b
    ldr r0, =main
    bx r0
