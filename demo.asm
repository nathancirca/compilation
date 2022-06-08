extern printf, atoi,malloc
global main
section .data
fmt: db "%d", 10, 0
p : dq 0
next : dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi

mov rbx,[rbp-0x10]
mov rdi,[rbx-8]
call atoi 
mov [next],rax
mov rbx,[rbp-0x10]
mov rdi,[rbx-16]
call atoi 
mov [p],rax

mov edi,8
call malloc
mov [p],rax

mov rax,3
push rax
 
mov rax,[next]
pop rbx
add rax,rbx 
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
