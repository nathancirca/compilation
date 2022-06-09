extern printf, atoi,malloc
global main
section .data
fmt: db "%d", 10, 0
a : dq 0
q : dq 0
p : dq 0
var : dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi


mov rbx,[rbp-0x10]
mov rdi,[rbx+8]
call atoi 
mov [a],rax

mov edi,8
extern malloc
call malloc
mov [q],rax

mov rax,20
mov [var],rax

push rbp
mov rbp,rsp
mov QWORD [rbp], var
lea rax,[rbp]
mov QWORD [rbp],rax
pop rbp
mov [q],rax

push rbp
mov rbp,rsp
mov QWORD [rbp], q
lea rax,[rbp]
mov QWORD [rbp],rax
pop rbp
mov [p],rax

mov rax,[p]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
