extern printf, atoi, itoa, len_concat
global main
section .data
fmt: db "%d", 10, 0
X: dq 0
X_type: dq 0
Y: dq 0
Y_type: dq 0

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

mov edi,8
extern malloc
call malloc
mov rcx,1
mov [X_type], rcx
mov [X],rax
mov edi,8
extern malloc
call malloc
mov rcx,1
mov [Y_type], rcx
mov [Y],rax
mov rax, [X]
push rax
mov rax, [Y]
pop rbx
mov rcx, [X_type]
mov rdx,[Y_type]
                cmp rcx, rdx
je eqadd32
jne neqadd32
eqadd32: cmp rcx, 0
je intadd32
cmp rcx, 1
je pointadd32
jne stradd32
stradd32: 
jmp fin32
pointadd32:
add rax,rbx
jmp fin32
intadd32:
 add rax, rbx
jmp fin32
                neqadd32: cmp rcx, 0
je i132
jne cp132
i132: cmp rdx, 1
je iaddp32
jne iadds32

                cp132: cmp rcx, 1
je p132
jne cs132
p132: cmp rdx, 0
je iaddp32
jne fin32

                cs132: cmp rdx, 0
je saddi32
jne fin32

                iaddp32: add rax,rbx
jmp fin32

                iadds32: 
   
                saddi32: 

                fin32:
mov rcx,[X_type]
mov rdx, [Y_type]
cmp rcx,2
je tstr33
cmp rdx, 2
je tstr33
cmp rcx,1
je tpnt33
cmp rdx, 1
je tpnt33
mov rcx,0
mov [X_type], rcx
jmp fin33
tstr33: mov rcx,1
mov [X_type], rcx
jmp fin33
tpnt33: mov rcx,0
mov [X_type], rcx
fin33:
mov [X],rax
mov rax, [X]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
