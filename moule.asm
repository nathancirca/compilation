extern printf, atoi, strlen, itoa
global main
section .data
fmt: db "%d", 10, 0
VAR_DECL

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi
  push r15
  push r14
  push r13
  push r12


VAR_INIT
BODY
RETURN

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
