import lark

grammaire = lark.Lark("""
variables : IDENTIFIANT ("," IDENTIFIANT)*
expr : IDENTIFIANT -> variable | NUMBER -> nombre | expr OP expr ->binexpr| "(" expr ")" -> parenexpr|"*" expr -> pointer|"&" IDENTIFIANT -> adresse| "malloc" "(" NUMBER ")" -> malloc
cmd : IDENTIFIANT "=" expr ";" -> assignment | "while" "(" expr ")" "{" bloc "}" -> while | "if" "(" expr ")" "{" bloc "}" -> if | "printf" "(" expr ")" ";" -> printf| "*" IDENTIFIANT "=" expr ";"-> pointer |IDENTIFIANT "=" "malloc" "(" NUMBER ")" ";"-> malloc
bloc : (cmd)*
prog : "main" "(" variables ")" "{" bloc "return" "(" expr ")" ";" "}"
NUMBER : /[0-9]+/
OP : /[-+\*>]/
IDENTIFIANT : /[a-zA-Z][a-zA-Z0-9]*/
CHAR : /["][a-zA-Z0-9]*["]/
%import common.WS
%ignore WS
""", start = "prog")

cpt =iter(range(10000))

def pp_variables(vars):
    return ", ".join([t.value for t in vars.children])
def pp_expr(expr):
    if expr.data in {"variable","nombre"}:
        return expr.children[0].value
    elif expr.data == "binexpr":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[2])
        op = expr.children[1].value
        return f"{e1} {op} {e2}"
    elif expr.data == "parenexpr":
        return f"({pp_expr(expr.children[0])})"
    elif expr.data=="pointer":
        return f"*{pp_expr(expr.children[0])}"
    elif expr.data=="adresse":
        return f"&{pp_expr(expr.children[0])}"
    elif expr.data=="malloc":
        return f"malloc({pp_expr(expr.children[0])})"
    else :
        raise Exception("Not implemented")
def pp_cmd(cmd):
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        rhs = pp_expr(cmd.children[1])
        return f"{lhs}={rhs};"
    elif cmd.data == "printf":
        return f"printf({pp_expr(cmd.children[0])});"
    elif cmd.data in {"while","if"}:
        e = pp_expr(cmd.children[0])
        b = pp_bloc(cmd.children[1])
        return f"{cmd.data} ({e}) {{{b}}}"
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
    else :
        raise Exception("Not implemented")
def pp_bloc(bloc):
    return "\n".join([pp_cmd(t) for t in bloc.children])

def pp_prg(prog):
    vars = pp_variables(prog.children[0])
    bloc = pp_bloc(prog.children[1])
    ret = pp_expr(prog.children[2])
    return f"main ({vars}){{{bloc} return ({ret});}}"



def adresse(expr):
    if expr.data=="adresse":
        return f"*{compile_expr(expr.children[0])}"
    else:
        return compile_expr(expr) 

def type(expr):
    if expr.data =="variable":
        return f"[{expr.children[0].value}_type]"
    elif expr.data == "nombre":
        return "0"
    elif expr.data=="pointer":
        return "1"
    elif expr.data=="string":
        return "2"
    elif expr.data == "binexpr":
        t1=type(expr.children[0])
        t2=type(expr.children[2])
        if t1 == t2:
            return t1
        elif expr.children[1]=="+" or expr.children[1]=="*":
            if (t1 == "2" or t2 == "2"):
                return "2"
            else:
                return "1"
    elif expr.data == "parenexpr":
        return type(expr.chidlren[0])
    else :
        raise Exception("Not implemented")

def type_assign(expr,lhs):
    if expr.data == "variable":
        return f"mov [{lhs}_type] [{expr.children[0].value}_type]"
    elif expr.data == "nombre":
        return f"mov [{lhs}_type] 0"
    elif expr.data == "pointer":
        return f"mov [{lhs}_type] 1"
    elif expr.data =="string":
        return f"mov [{lhs}_type] 2"
    elif expr.data == "binexpr":
        t1 = type(expr.children[0])
        t2 = type(expr.children[2])
        if expr.children[1] == "+":
            if (t1=="2" or t2=="2"):
                return f"mov [{lhs}_type] 2"
            elif (t1=="1" or t2=="1"):
                return f"mov [{lhs}_type] 1"
            else :
                return f"mov [{lhs}_type] 0"
    elif expr.data == "parenexpr":
        return type_assign(expr.chidlren[0])
    else :
        raise Exception("Not implemented")



def var_list(ast):
    if isinstance(ast, lark.Token):
        if ast.type == "IDENTIFIANT":
            return {ast.value}
        else :
            return set()
    s=set()
    for c in ast.children:
        s.update(var_list(c))
    return s

def compile_expr(expr):
    if expr.data == "variable":
        return f"mov rax, [{expr.children[0].value}]"
    elif expr.data == "nombre":
        return f"mov rax,{expr.children[0].value}"
    elif expr.data == "binexpr":
        exp1=expr.children[0]
        exp2=expr.children[2]
        e1 = compile_expr(exp1)
        e2 = compile_expr(exp2)
        if expr.children[1] == "+":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje eq\njne neq\neq: cmp {type(exp1)} 0\nje int\ncmp {type(exp1)} 1\nje point\nstr: \njmp fin\npoint: add rax,rbx\njmp fin\nint: add rax, rbx\njmp fin\n\
                neq: cmp {type(exp1)} 0\nje i1\njne cp1\ni1: cmp {type(exp2)} 1\nje i+p\njne i+s\n\
                cp1: cmp {type(exp1)} 1\nje p1\njne cs1\np1: cmp {type(exp2)} 0\nje i+p\njne p+s\n\
                cs1: cmp {type(exp2)} 0\nje i+s\njne p+s\n\
                i+p: add rax,rbx\njmp fin\n\
                i+s: \njmp fin\n\
                p+s: \njmp fin\nfin:"
        elif expr.children[1] == "-":
                return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje eq\njne fin\neq: cmp {type(exp1)} 0\nje int\npointer\nint: sub rax, rbx\njmp fin\nfin:"
        elif expr.children[1] == "*":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje sol1\nsol1: cmp {type(exp1)} 0\n je int\nint: imul rax, rbx\njmp fin\n\
                cmp {type(exp1)} 0\nje i1\njne cp\ni1: cmp {type(exp2)} 1\nje i*p\njne i*s\n\
                cp: cmp {type(exp1)} 1\nje p1\njne cs\np1: cmp {type(exp2)} 0\nje i*p\n\
                cs: cmp {type(exp2)} 0\nje i*s\n\
                i*p: imul rax, rbx\njmp fin\n\
                i*s: \njmp fin\nfin:"
        elif expr.children[1] == "/":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje sol1\njne fin\nsol1: cmp {type(exp1)} 0\n je int\njne fin\nint: div rax, rbx\nfin:"
        else:
            raise Exception("Binexp Not implemented")
    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    elif expr.data=="pointer":
        return f" push rbp\nmov rbp,rsp\nmov rax,QWORD PTR [rbp-8]\nmov QWORD PTR [rax],{expr.children[1].value}\npop rbp"
    elif expr.data=="adresse":
        return f"push rbp\nmov rbp,rsp\nmov QWORD PTR [rbp], {expr.children[0].children[0]}\nlea rax,[rbp]\nmov QWORD PTR [rbp],rax\npop rbp"
    elif expr.data=="malloc":
        return f"mov edi,{expr.children[0].value}\nextern malloc\ncall malloc"
    else :
        raise Exception("Not implemented")

def compile_cmd(cmd):
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        expr = cmd.children[1]
        rhs = compile_expr(expr)
        return f"{rhs}\n{type_assign(expr,lhs)}\nmov [{lhs}],rax"
    elif cmd.data == "while":
        e = compile_expr(cmd.children[0])
        te = type(cmd.children[0])
        b = compile_bloc(cmd.children[1])
        index=next(cpt)
        return f"debut{index}:{e}\ncmp {te}, 0\nje int\ncmp {te} 1\nje point\njne str\npoint: mov eax, [rax]\ntest eax, eax\njz fin{index}\n{b}\njmp debut{index}\nstr: \nint :cmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "printf":
        e1 = compile_cmd(cmd.children[0])
        return f"{e1}\nmov rdi, fmt\nmov rsi, rax\nxor rax, rax\ncall printf"
    elif cmd.data =="if":
        e1 = compile_expr(cmd.children[0])
        te1=type(cmd.children[0])
        e2 = compile_cmd(cmd.children[1])
        index=next(cpt)
        return f"{e1}\ncmp {te}, 0\nje int\ncmp {te} 1\nje point\njne str\npoint: mov eax, [rax]\ntest eax, eax\njz fin{index}\n{b}\njmp debut{index}\nstr: \nint :cmp rax,0\njz fin{index}\n{b}\nfin{index}:\n"
    elif cmd.data=="pointer":
        lhs= cmd.children[0].value
        rhs=compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    else :
        raise Exception("Not implemented")

def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])

def compile_vars(ast):
    s=""
    for i in range(len(ast.children)):
        s+= f"mov rbx, [rbp-0x10]\nmov rdi,[rbx-{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].value}],rax\n"
    return s

def compile(prg):
    with open("moule.asm") as f:
        code = f.read()
        var_decl = "\n".join([f"{x}: dq 0\n{x}_type: dq 0" for x in var_list(prg)])
        code = code.replace("VAR_DECL", var_decl)
        code = code.replace("RETURN",compile_expr(prg.children[2]))
        code = code.replace("BODY", compile_bloc(prg.children[1]))
        code = code.replace("INIT", compile_vars(prg.children[0]))
        return code

prg = grammaire.parse("main(X,Y) {while(X){X=X-1;Y=Y+1;}return(Y+1);}")
print(compile(prg))

def pointer(expr):
    if expr.data=="pointer":
        return f"*{compile_expr(expr.children[0])}"
    else:
        return compile_expr(expr)





def gamma_expr(expr):
    if expr.data == "nombre":
        return "mov rax,"+str(expr.children[0].value)
    elif expr.data == "variable":
        return "mov rax, ["+expr.children[0].value+"]"
    elif expr.data == "binexpr":
        if expr.children[1].value=="+":
            expr1=gamma_expr(expr.children[0])
            expr2=gamma_expr(expr.children[2])
            return expr1+"\npush rax\n"+expr2+"\npop rbx\nadd rax,rbx"
        elif expr.children[1].value=="-":
            expr1=gamma_expr(expr.children[0])
            expr2=gamma_expr(expr.children[2])
            return expr1+"\npush rax\n"+expr2+"\npop rbx\nsub rax,rbx"
        elif expr.children[1].value=="*":
            expr1=gamma_expr(expr.children[0])
            expr2=gamma_expr(expr.children[2])
            return expr1+"\npush rax\n"+expr2+"\npop rbx\nmul rax,rbx"
        elif expr.children[1].value=="/":
            expr1=gamma_expr(expr.children[0])
            expr2=gamma_expr(expr.children[2])
            return expr1+"\npush rax\n"+expr2+"\npop rbx\ndiv rax,rbx"
        elif expr.children[1].value==">":
            expr1=gamma_expr(expr.children[0])
            expr2=gamma_expr(expr.children[2])
            return expr1+"\npush rax\n"+expr2+"\npop rbx\ncmp rax,rbx"
    elif expr.data=="parenexpr":
        return gamma_expr(expr.children[0])


def gamma_cmd(cmd):
    if cmd.data == "assignment":
        expr=gamma_expr(cmd.children[1])
        return f"{expr}\nmov [{cmd.children[0].value}],rax"
    elif cmd.data == "printf":
        expr=gamma_expr(cmd.children[1])
        return f"{expr}\nmov rdi,fmt\nmov rsi,rax\nxor rax,rax\ncall printf"
    elif cmd.data in "while":
        expr=gamma_expr(cmd.children[0])
        cmd=gamma_cmd(cmd.children[1])
        return f"debut:{expr}\ncmp rax,0\njz fin\n{cmd}\njmp debut\nfin:"
    elif cmd.data in "if":
        expr=gamma_expr(cmd.children[0])
        cmd=gamma_cmd(cmd.children[1])
        return f"{expr}\ncmp rax,0\njz fin1\n{cmd}\nfin1:"
    else :
        raise Exception("Not implemented")