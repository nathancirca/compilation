extern printf, atoi
global main
section .data
fmt: db "%d", 10, 0
X: dq 0
X_type: dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi

mov rbx, [rbp+0x10]
mov rdi,[rbx+8]
call atoi
mov [X],rax

mov rax,20
mov rcx,0
mov [X_type], rcx
mov [X],rax
mov rax, [X]
push rax
mov rax,12
push rbx
pop rax
pop rbx
mov rcx, [X_type]
mov rdx,0
                cmp rcx, rdx
je eqadd5
jne neqadd5
eqadd5: cmp rcx, 0
je intadd5
cmp rcx, 1
je pointadd5
jne stradd5
stradd5: 
jmp fin5
pointadd5: add rax,rbx
jmp fin5
intadd5: add rax, rbx
jmp fin5
                neqadd5: cmp rcx, 0
je i15
jne cp15
i15: cmp rdx, 1
je iaddp5
jne iadds5
                cp15: cmp rcx, 1
je p15
jne cs15
p15: cmp rdx, 0
je iaddp5
jne padds5
                cs15: cmp rdx, 0
je iadds5
jne padds5
                iaddp5: add rax,rbx
jmp fin5
                iadds5: 
jmp fin5
                padds5: 
jmp fin5
fin5:
mov rcx,0
mov [X_type], rcx
mov [X],rax
mov rax, [X]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
