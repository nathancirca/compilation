extern printf, atoi, strlen
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

X: dq 0
X_type: dq 0

mov rbx, [rbp+0x10]
mov rdi,[rbx+8]
call atoi
mov [X],rax

mov rax,20
mov [X_type], 0
mov [X],rax
mov rax, [X]
push rax
mov rax,12
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
pointadd5:
add rax,rbx
jmp fin5
intadd5:
 add rax, rbx
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
jne fin5

                cs15: cmp rdx, 0
je saddi5
jne fin5

                iaddp5: add rax,rbx
jmp fin5

                iadds5: lea rax, X
mov rbx, X
mov edx, 8
mov rsi, rax
mov edi, rbx
mov ebx, 0
call itoa
mov edx, 1
mov ebx, 2
add edx, ebx
movsx rdx, ebx
sub rdx, 1
mov len_concat, rdx
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
mov i, 0
jmp debut1
debut4:
mov eax, i
cdqe
cmp rbx, 6
ja debut2
mov ebx, i
cdqe
movzx ecx, [X+rbx]
mov rdx, rax
mov eax, i
cdqe
mov [rdx+rbx], cl
jmp debut3
fin4:
debut3:
add i, 1
fin3:
debut1:
mov ebx, rax
cmp eax, len_concat
jl debut4
mov rsp rsi
fin1:
debut2:
mov ebx, rax
cdqe
movzx ecx, [12+rbx]
mov rdx, rax
mov eax, i
cdqe
mov [rdx+rbx], cl
fin2:   
                saddi5: lea rax, X
mov rbx, X
mov edx, 8
mov rsi, rax
mov edi, rbx
mov ebx, 0
call itoa
mov edx, 1
mov ebx, 2
add edx, ebx
movsx rdx, ebx
sub rdx, 1
mov len_concat, rdx
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
mov i, 0
jmp debut1
debut4:
mov eax, i
cdqe
cmp rbx, 6
ja debut2
mov ebx, i
cdqe
movzx ecx, [X+rbx]
mov rdx, rax
mov eax, i
cdqe
mov [rdx+rbx], cl
jmp debut3
fin4:
debut3:
add i, 1
fin3:
debut1:
mov ebx, rax
cmp eax, len_concat
jl debut4
mov rsp rsi
fin1:
debut2:
mov ebx, rax
cdqe
movzx ecx, [12+rbx]
mov rdx, rax
mov eax, i
cdqe
mov [rdx+rbx], cl
fin2:
                fin5:
mov [X_type], 0
mov [X],rax
mov rax, [X]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret