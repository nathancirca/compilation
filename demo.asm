extern printf, atoi
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

second : dq 0
counter : dq 0
next : dq 0
first : dq 0
p : dq 0
mov rax,0
mov [p],rax
mov rax,0
mov [first],rax
mov rax,0
mov [counter],rax
mov rax,1
mov [second],rax
mov rax,3
mov [next],rax
mov rax,[next]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
