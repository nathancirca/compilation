extern printf
global main
section .data
hello :
    db "hello world %d", 10, 0; db = data byte, dw = word = 2 octets, dd = dword = 4 octets
    ; dq = quad word = 8 octets

section .text
main :
mov rsi, 12 ; rsi = 12
; mov 12,%rsi
mov rdi, hello
xor rax, rax
call printf
ret
