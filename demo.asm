extern printf, atoi, strlen, itoa
global main
section .data
fmt: db "%d", 10, 0
E: dq 0
E_type: dq 0
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
mov rbx, [rbp+0x10]
mov rdi,[rbx+16]
call atoi
mov [Y],rax
mov rbx, [rbp+0x10]
mov rdi,[rbx+24]
call atoi
mov [E],rax

mov rax, 979899100101102
mov rcx, 2
mov [X_type], rcx
mov [X],rax
mov rax, 979899100101102
mov rcx, 2
mov [Y_type], rcx
mov [Y],rax
mov rax, [X]
push rax
mov rax, [Y]
pop rbx
mov rcx, [X_type]
mov rdx,[Y_type]
cmp rcx, rdx
je eqadd30
jne neqadd30
eqadd30: cmp rcx, 0
je intadd30
cmp rcx, 1
je pointadd30
jne stradd30
stradd30: 
jmp fin30
pointadd30:
add rax,rbx
jmp fin30
intadd30:
 add rax, rbx
jmp fin30
neqadd30: cmp rcx, 0
je i130
jne cp130
i130: cmp rdx, 1
je iaddp30
jne iadds30

cp130: cmp rcx, 1
je p130
jne cs130
p130: cmp rdx, 0
je iaddp30
jne fin30

cs130: cmp rdx, 0
je saddi30
jne fin30

iaddp30: add rax,rbx
jmp fin30

iadds30: lea rax, X
mov rbx, X
mov edx, 8
mov rsi, rax
mov edi, rbx
mov ebx, 0
call itoa
mov edx, 1
mov ebx, 1
add edx, ebx
movsx rdx, ebx
sub rdx, 1
mov r11, rdx
movsx rdx, ebx
mov r10, rdx
mov r11d, 0
movsx rdx, ebx
mov r8, rdx
mov e9d, 0
cdqe
mov edx, 16
sub rdx, 1
add rbx, rdx
mov esi, 16
mov edx, 0
div rsi
imul rbx, rbx, 16
sub rsp, rbx
mov rbx, rsp
add rbx, 0
mov rax, rbx
mov r12d, 0
jmp debut_iadds26
debut_iadds29:
mov eax, r12d
cdqe
cmp rbx, 6
ja debut_iadds27
mov eax, r12d
cdqe
movzx ecx, [X+rbx]
mov rdx, rax
mov eax, r12d
cdqe
mov [rdx+rbx], cl
jmp debut_iadds28
fin_iadds29:
debut_iadds28:
add r12d, 1
fin_iadds28:
debut_iadds26:
mov ebx, rax
cmp eax, r11d
jl debut_iadds29
mov rsp, rsi
fin_iadds26:
debut_iadds27:
mov ebx, rax
cdqe
movzx ecx, [Y+rbx]
mov rdx, rax
mov eax, r12d
cdqe
mov [rdx+rbx], cl
fin_iadds27:   
saddi30: lea rax, X
mov rbx, X
mov edx, 8
mov rsi, rax
mov edi, rbx
mov ebx, 0
call itoa
mov edx, 1
mov ebx, 1
add edx, ebx
movsx rdx, ebx
sub rdx, 1
mov r11, rdx
movsx rdx, ebx
mov r10, rdx
mov r11d, 0
movsx rdx, ebx
mov r8, rdx
mov e9d, 0
cdqe
mov edx, 16
sub rdx, 1
add rbx, rdx
mov esi, 16
mov edx, 0
div rsi
imul rbx, rbx, 16
sub rsp, rbx
mov rbx, rsp
add rbx, 0
mov rax, rbx
mov r12, 0
jmp debut_saddi26
debut_saddu29:
mov eax, r12
cdqe
cmp rbx, 6
ja debut_saddi27
mov ebx, r12
cdqe
movzx ecx, [X+rbx]
mov rdx, rax
mov eax, r12
cdqe
mov [rdx+rbx], cl
jmp debut_saddi28
fin_saddi29:
debut_saddi28:
add r12, 1
fin_saddi28:
debut_saddi26:
mov ebx, rax
cmp eax, len_concat
jl debut_saddi29
mov rsp, rsi
fin_saddi26:
debut_saddi27:
mov ebx, rax
cdqe
movzx ecx, [Y+rbx]
mov rdx, rax
mov eax, r12
cdqe
mov [rdx+rbx], cl
fin_saddi27:
fin30:
mov rcx, 0
mov [E_type], rcx
mov [E],rax
mov rax, [E]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret