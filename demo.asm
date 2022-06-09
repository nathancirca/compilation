extern printf, atoi
global main
section .data
fmt: db "%d", 10, 0
var: dq 0
var_type: dq 0
a: dq 0
a_type: dq 0
q: dq 0
q_type: dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi


mov rbx, [rbp+0x10]
mov rdi,[rbx+8]
call atoi
mov [a],rax

mov edi,8
extern malloc
call malloc
mov rcx,1
mov [q_type], rcx
mov [q],rax
mov rax,2
mov rcx,0
mov [var_type], rcx
mov [var],rax

push rbp
mov rbp,rsp
mov QWORD [rbp], var
lea rax,[rbp]
mov QWORD [rbp],rax
pop rbp
mov rcx,0
mov [q_type], rcx
mov [q],rax
mov rax, [q]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
