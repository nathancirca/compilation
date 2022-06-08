extern printf, atoi
global main
section .data
fmt: db "%d", 10, 0
Y: dq 0
Y_type: dq 0
X: dq 0
X_type: dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi

mov rbx, [rbp-0x10]
mov rdi,[rbx-8]
call atoi
mov [X],rax
mov rbx, [rbp-0x10]
mov rdi,[rbx-16]
call atoi
mov [Y],rax

debut11:mov rax, [X]
cmp [X_type], 0
je int
cmp [X_type], 1
je point
jne str
point: mov eax, [rax]
test eax, eax
jz fin11
mov rax, [X]
push rax
mov rax,1
push rbx
pop rax
pop rbx
                cmp [X_type], 0
je eq7
jne fin7
eq7: cmp [X_type], 2
je fin7
sub rax, rbx
jmp fin7
fin7:
None
mov [X],rax
mov rax, [Y]
push rax
mov rax,1
push rbx
pop rax
pop rbx
                cmp [Y_type], 0
je eqadd10
jne neqadd10
eqadd10: cmp [Y_type], 0
je intadd10
cmp [Y_type], 1
je pointadd10
jne stradd10
stradd10: 
jmp fin
pointadd10: add rax,rbx
jmp fin10
intadd10: add rax, rbx
jmp fin10
                neqadd10: cmp [Y_type], 0
je i110
jne cp110
i110: cmp 0, 1
je iaddp10
jne iadds10
                cp110: cmp [Y_type], 1
je p110
jne cs110
p110: cmp 0, 0
je iaddp10
jne padds10
                cs110: cmp 0, 0
je iadds10
jne padds10
                iaddp10: add rax,rbx
jmp fin10
                iadds10: 
jmp fin10
                padds10: 
jmp fin10
fin10:
mov [Y_type], 0
mov [Y],rax
jmp debut11
str: 
int :cmp rax,0
jz fin11
mov rax, [X]
push rax
mov rax,1
push rbx
pop rax
pop rbx
                cmp [X_type], 0
je eq7
jne fin7
eq7: cmp [X_type], 2
je fin7
sub rax, rbx
jmp fin7
fin7:
None
mov [X],rax
mov rax, [Y]
push rax
mov rax,1
push rbx
pop rax
pop rbx
                cmp [Y_type], 0
je eqadd10
jne neqadd10
eqadd10: cmp [Y_type], 0
je intadd10
cmp [Y_type], 1
je pointadd10
jne stradd10
stradd10: 
jmp fin
pointadd10: add rax,rbx
jmp fin10
intadd10: add rax, rbx
jmp fin10
                neqadd10: cmp [Y_type], 0
je i110
jne cp110
i110: cmp 0, 1
je iaddp10
jne iadds10
                cp110: cmp [Y_type], 1
je p110
jne cs110
p110: cmp 0, 0
je iaddp10
jne padds10
                cs110: cmp 0, 0
je iadds10
jne padds10
                iaddp10: add rax,rbx
jmp fin10
                iadds10: 
jmp fin10
                padds10: 
jmp fin10
fin10:
mov [Y_type], 0
mov [Y],rax
jmp debut11
fin11:

mov rax, [Y]
push rax
mov rax,1
push rbx
pop rax
pop rbx
                cmp [Y_type], 0
je eqadd3
jne neqadd3
eqadd3: cmp [Y_type], 0
je intadd3
cmp [Y_type], 1
je pointadd3
jne stradd3
stradd3: 
jmp fin
pointadd3: add rax,rbx
jmp fin3
intadd3: add rax, rbx
jmp fin3
                neqadd3: cmp [Y_type], 0
je i13
jne cp13
i13: cmp 0, 1
je iaddp3
jne iadds3
                cp13: cmp [Y_type], 1
je p13
jne cs13
p13: cmp 0, 0
je iaddp3
jne padds3
                cs13: cmp 0, 0
je iadds3
jne padds3
                iaddp3: add rax,rbx
jmp fin3
                iadds3: 
jmp fin3
                padds3: 
jmp fin3
fin3:

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
