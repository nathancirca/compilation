import lark
#pour nasmer: nasm -f elf64 "nom de fichier"
#pour compiler: gcc -o main -no-pie -fno-pie demo.o





grammaire=lark.Lark("""
variables: IDENTIFIANT ("," IDENTIFIANT)*
expr: IDENTIFIANT -> variable |NUMBER -> nombre |expr OP expr -> binexpr | "(" expr ")" -> parenexpr|"*" expr -> pointer|"&" IDENTIFIANT -> adresse| "malloc" "(" NUMBER ")" -> malloc
cmd: IDENTIFIANT "=" expr ";"-> assignment |"while" "(" expr ")" "{" bloc "}" -> while 
| "if" "(" expr")" "{" bloc "}" -> if | "printf" "(" expr ")" ";"->printf| "*" IDENTIFIANT "=" expr ";"-> pointer |IDENTIFIANT "=" "malloc" "(" NUMBER ")" ";"-> malloc
bloc: (cmd)*
prog:"main" "(" variables ")" "{" bloc "return" "(" expr ")" ";" "}"
NUMBER: /[0-9]+/
OP: /[-+\*><]/
IDENTIFIANT: /[a-zA-Z][a-zA-Z0-9]*/
%import common.WS
%ignore WS
""",start="prog")

cpt=iter(range(10000))


def read_file(file):
    f = open(file, "r")
    code = f.read()
    f.close()
    return code






def pp_variables(vars):
    return ", ".join([t.value for t in vars.children])

def pp_expr(expr):
    if expr.data in {"variable","nombre"}:
        return expr.children[0].value
    elif expr.data=="binexpr":
        e1=pp_expr(expr.children[0])
        e2=pp_expr(expr.children[2])
        op=expr.children[1].value
        return f"{e1} {op} {e2}"
    elif expr.data=="parenexpr":
        return f"({pp_expr(expr.children[0])})"
    elif expr.data=="pointer":
        return f"*{pp_expr(expr.children[0])}"
    elif expr.data=="adresse":
        return f"&{expr.children[0].value}"
    elif expr.data=="malloc":
        return f"malloc({expr.children[0].value})"
    else:
        raise Exception("Not implemented")

def pp_cmd(cmd):
    if cmd.data=="assignment":
        lhs= cmd.children[0].value
        rhs=pp_expr(cmd.children[1])
        return f"{lhs}={rhs};"
    elif cmd.data=="printf":
        return f"printf( {pp_expr(cmd.children[0])} );"
    elif cmd.data in {"while","if"}:
        e=pp_expr(cmd.children[0])
        b=pp_bloc(cmd.children[1])
        return f" {cmd.data} ({e}) {{ {b} }}"
    elif cmd.data=="pointer":
        lhs= cmd.children[0].value
        rhs=pp_expr(cmd.children[1])
        return f"*{lhs}={rhs};"
    elif cmd.data=="adresse":
        lhs= cmd.children[0].value
        rhs=pp_expr(cmd.children[1])
        return f"&{lhs}={rhs};"
    elif cmd.data=="malloc":
        lhs= cmd.children[0].value
        rhs=pp_expr(cmd.children[1])
        return f"{lhs}={rhs};"
    else: 
        raise Exception("Not implemented yet")

def pp_bloc(bloc):
    return "\n".join([pp_cmd(t) for t in bloc.children])

def pp_prg(prog):
    vars=pp_variables(prog.children[0])
    bloc=pp_bloc(prog.children[1])
    ret=pp_expr(prog.children[2])
    return f"main ({vars}){{ {bloc} return ({ret}); }}"

#expr=grammaire.parse("*P")
#print(pp_expr(expr))
# bloc=grammaire.parse("*X=Y;A=&B;")
# print(bloc)
# print(pp_bloc(bloc))
# prg=grammaire.parse("""
# main(first)
# {
#     *p=0;
#     first=0;
#     counter=0; 
#     second=1;
#     next=3;
#     return(next);
# }""")





# expr=grammaire.parse("malloc(8)")
# print(expr)
# print(pp_expr(expr))

# cmd=grammaire.parse("P=malloc(8);")
# print(cmd)
# print(pp_cmd(cmd))

#bloc=grammaire.parse("X=3;Y=3;")
#print(pp_bloc(bloc))
#print(grammaire.parse("printf(X);"))
#print(pp_variables(prg.children[0]))
#print(prg)
#print(prg.children[0].children[0].value)

#prg2=grammaire.parse(pp_prg(prg))
#print(prg2==prg)

def var_list(ast):
    if isinstance(ast,lark.Token):
        if ast.type=='IDENTIFIANT':
            return {ast.value}
        else:
            return set()
    s = set()
    for c in ast.children:
        s.update(var_list(c))
    return s

def compile(prg):
    with open("moule.asm",) as f:
        code = f.read()
        var_decl="\n".join([f"{v} : dq 0" for v in var_list(prg)])
        code = code.replace("VAR_DECL", var_decl)
        #code=code.replace("VAR_INIT",var_decl)
        code=code.replace("RETURN",compile_expr(prg.children[2]))
        code=code.replace("BODY",compile_bloc(prg.children[1]))
        code=code.replace("VAR_INIT",compile_variables(prg.children[0]))
        g = open("demo.asm", "w")
        g.write(code)
        g.close()
        return code


    
        
    
#transform code into assembly code

def compile_variables(ast):
    s=""
    for i in range(len(ast.children)):
        s+= f"\nmov rbx,[rbp-0x10]\nmov rdi,[rbx+{8*(i+1)}]\ncall atoi \nmov [{ast.children[i].value}],rax\n"
    return s

def compile_cmd(cmd):
    if cmd.data=="assignment":
        lhs= cmd.children[0].value
        rhs=compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    elif cmd.data=="pointer":
        lhs= cmd.children[0].value
        rhs=compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    elif cmd.data =="while":
        e=compile_expr(cmd.children[0])
        b=compile_bloc(cmd.children[1])
        index=next(cpt)
        return f" debut{index}:{e}\ncmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    else: 
        raise Exception("Not implemented yet")

def compile_prg(prg):
    return ""

def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])
    

def compile_expr(expr):
    if expr.data == "variable":
        return f"\nmov rax,[{expr.children[0].value}]"
    elif expr.data=="nombre":
        return f"\nmov rax,{expr.children[0].value}"
    elif expr.data=="binexpr":
        e1=compile_expr(expr.children[0])
        e2=compile_expr(expr.children[2])
        op=expr.children[1].value
        return f"{e2}\npush rax\n {e1}\npop rbx\nadd rax,rbx {e2}"
    elif expr.data=="parenexpr":
        return compile_expr(expr.children[0])
    elif expr.data=="pointer":
        return f" push rbp\nmov rbp,rsp\nmov rax,QWORD [rbp-8]\nmov QWORD [rax],{expr.children[1].value}\npop rbp"
    elif expr.data=="adresse":
        return f"push rbp\nmov rbp,rsp\nmov QWORD [rbp], {expr.children[0]}\nlea rax,[rbp]\nmov QWORD [rbp],rax\npop rbp"
    elif expr.data=="malloc":
        return f"mov edi,{expr.children[0].value}\nextern malloc\ncall malloc"
    else:
        raise Exception("Not implemented")
    



def pointer(expr):
    if expr.data=="pointer":
        return f"*{compile_expr(expr.children[0])}"
    else:
        return compile_expr(expr)

def adresse(expr):
    if expr.data=="adresse":
        return f"*{compile_expr(expr.children[0])}"
    else:
        return compile_expr(expr) 



prg=grammaire.parse(read_file("test.txt"))
print(pp_prg(prg))
compile(prg)