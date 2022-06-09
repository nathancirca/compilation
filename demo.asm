extern printf, atoi, itoa, len_concat
global main
section .data
fmt: db "%d", 10, 0
X: dq 0
X_type: dq 0
var: dq 0
var_type: dq 0

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

mov rax,2
mov rcx,0
mov [var_type], rcx
mov [var],rax
mov rax, [var]
push rax
mov rax,3
pop rbx
mov rcx, [var_type]
mov rdx,0
                cmp rcx, rdx
je eqadd26
jne neqadd26
eqadd26: cmp rcx, 0
je intadd26
cmp rcx, 1
je pointadd26
jne stradd26
stradd26: 
pointadd26:
add rax,rbx
jmp fin26
intadd26:
 add rax, rbx
jmp fin26
                neqadd26: cmp rcx, 0
je i126
jne cp126
i126: cmp rdx, 1
je iaddp26
jne iadds26

                cp126: cmp rcx, 1
je p126
jne cs126
p126: cmp rdx, 0
je iaddp26
jne fin26

                cs126: cmp rdx, 0
je saddi26
jne fin26

                iaddp26: add rax,rbx
jmp fin26

                iadds26: 
   
                saddi26: 

                fin26:
mov rcx,[var_type]
mov rdx, 0
cmp rcx,2
je tstr27
cmp rdx, 2
je tstr27
cmp rcx,1
je tpnt27
cmp rdx, 1
je tpnt27
mov rcx,0
mov [var_type], rcx
jmp fin27
tstr27: mov rcx,1
mov [var_type], rcx
jmp fin27
tpnt27: mov rcx,0
mov [var_type], rcx
fin27:
mov [var],rax
mov rax, [var]
push rax
mov rax,2
pop rbx
mov rcx, [var_type]
mov rdx,0
                cmp rcx, rdx
je eqmul42
jne neq42
eqmul42: cmp rcx, 0
 je intmul42
intmul42: imul rax, rbx
jmp fin42
                neq42: cmp rcx, 0
je i1mul42
jne cp42
i1mul42: cmp rdx, 1
je imulp42
jne imuls42
                cp42: cmp rcx, 1
je p1mul42
jne cs42
p1mul42: cmp rdx, 0
je imulp42
                cs42: cmp rdx, 0
je smuli42
                imulp42: imul rax, rbx
jmp fin42
                imuls42: 

                smuli42: 

                fin42:
mov rcx,[var_type]
mov rdx, 0
cmp rcx,0
je suite43
cmp rdx,0
jne fin43
suite43: cmp rcx,2
je tstr43
cmp rdx, 2
je tstr43
cmp rcx,1
je tpnt43
cmp rdx, 1
je tpnt43
mov rcx,0
mov [var_type], rcx
jmp fin43
tstr43: mov rcx,1
mov [var_type], rcx
jmp fin43
tpnt43: mov rcx,0
mov [var_type], rcx
fin43:
mov [var],rax
mov rax,2
push rax
mov rax, [var]
pop rbx
mov rcx, [var_type]
mov rdx,0
                cmp rcx, rdx
je eqdiv58
jne fin58
eqdiv58: cmp rcx, 0
 je intdiv58
jne fin58
intdiv58: div rbx
fin58:
mov rcx,[var_type]
mov rdx, 0
cmp rcx,rdx
jne fin59
cmp rcx,0
jne fin59
mov rcx,0
mov [var_type], rcx
fin59:
mov [var],rax
mov rax,1
push rax
mov rax, [var]
pop rbx
mov rcx, [var_type]
mov rdx,0
                cmp rcx, rdx
je eq74
jne fin74
eq74: cmp rcx, 2
je fin74
sub rax, rbx
jmp fin74
fin74:
mov rcx,[var_type]
mov rdx, 0
cmp rcx,rdx
jne fin75
cmp rcx,0
je tint75
mov rcx,1
mov [var_type], rcx
tint75: mov rcx,0
mov [var_type], rcx
fin75:
mov [var],rax
mov rax, [var]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
