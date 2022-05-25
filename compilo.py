import lark

grammaire = lark.Lark("""
variables : IDENTIFIANT ("," IDENTIFIANT)*
expr : IDENTIFIANT -> variable | NUMBER -> nombre | expr OP expr ->binexpr| "(" expr ")" -> parenexpr
cmd : IDENTIFIANT "=" expr ";" -> assignment | "while" "(" expr ")" "{" bloc "}" -> while | "if" "(" expr ")" "{" bloc "}" -> if | "printf" "(" expr ")" ";" -> printf
bloc : (cmd)*
prog : "main" "(" variables ")" "{" bloc "return" "(" expr ")" ";" "}"
NUMBER : /[0-9]+/
OP : /[-+\*>]/
IDENTIFIANT : /[a-zA-Z][a-zA-Z0-9]*/
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
    else :
        raise Exception("Not implemented")
def pp_bloc(bloc):
    return "\n".join([pp_cmd(t) for t in bloc.children])

def pp_prg(prog):
    vars = pp_variables(prog.children[0])
    bloc = pp_bloc(prog.children[1])
    ret = pp_expr(prog.children[2])
    return f"main ({vars}){{{bloc} return ({ret});}}"

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
        e1 = compile_expr(expr.children[0])
        e2 = compile_expr(expr.children[2])
        op = expr.children[1].value
        return f"{e2}\npush rax\n{e1}\npop rbx\nadd rax,rbx"
    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    else :
        raise Exception("Not implemented")

def compile_cmd(cmd):
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        rhs = compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    elif cmd.data == "while":
        e = compile_expr(cmd.children[0])
        b = compile_bloc(cmd.children[1])
        index=next(cpt)
        return f"debut{index}:{e}\ncmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    else :
        raise Exception("Not implemented")
def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])

def compile_vars(ast):
    s=""
    for i in range(len(ast)):
        s+= f"mov rbx, [rbp-0x10]\nmov rdi,[rbx-{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].value}],rax\n"
    return s

def compile(prg):
    with open("moule.asm") as f:
        code = f.read()
        var_decl = "\n".join([f"{x}: dq 0" for x in var_list(prg)])
        code = code.replace("VAR_DECL", var_decl)
        code = code.replace("RETURN",compile_expr(prg.children[2]))
        code = code.replace("BODY", compile_bloc(prg.children[1]))
        code = code.replace("INIT", compile_vars(prg.children[0]))
        return code

prg = grammaire.parse("main(X,Y) {while(X){X=X-1;Y=Y+1;}return(Y+1);}")
print(compile(prg))

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