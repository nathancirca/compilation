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
CHAR : /["][a-zA-Z0-9]*["]/
%import common.WS
%ignore WS
""", start = "prog")

cpt =iter(range(10000))
compteur=0

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

def compile_expr(expr):
    global compteur
    if expr.data == "variable":
        return f"mov rax, [{expr.children[0].value}]"
    elif expr.data == "nombre":
        return f"mov rax,{expr.children[0].value}"
    elif expr.data == "chaine":
        print(expr.children[0].value)
        e = '0x'
        for i in expr.children[0].value:
            if ord(i) != 34:
                e+=f"{ord(i)}"
        return f"movabs rax, [{e}]"
    elif expr.data == "binexpr":
        exp1=expr.children[0]
        exp2=expr.children[2]
        e1 = compile_expr(exp1)
        e2 = compile_expr(exp2)
        if expr.children[1] == "+":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje sol1\nsol1: cmp {type(exp1)} 0\nje int\ncmp {type(exp1)} 1\nje point\nstr\npoint: \nint: add rax, rbx\njmp fin\n\
                cmp {type(exp1)} 0\nje i1\ni1: cmp {type(exp2)} 1\nje i+p\njne i+s\n\
                cmp {type(exp1)} 1\nje p1\np1: cmp {type(exp2)} 0\nje i+p\njne p+s\n\
                cmp {type(exp1)} 2\nje s1\ns1: cmp {type(exp2)} 0\nje i+s\njne p+s\n\
                cmp {type(exp2)} 0\nje i2\ni2: cmp {type(exp1)} 1\nje i+p\njne i+s\n\
                cmp {type(exp2)} 1\nje p2\np2: cmp {type(exp1)} 0\nje i+p\njne p+s\n\
                cmp {type(exp2)} 2\nje s2\ns2: cmp {type(exp1)} 0\nje i+s\njne p+s\n\
                i+p: \njmp fin\n\
                i+s: \njmp fin\n\
                p+s: \njmp fin\nfin:"
            if t1==0 and t2==0:
                return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\nadd rax, rbx"
            elif (t1==0 and t2==1) or (t1==1 and t2==0):
                return #add int ot a pointer
            elif (t1==0 and t2==2) or (t1==2 and t2==0):
                if (t1==0):
                    e1 = expr.children[0].value
                    e2 = expr.children[2].value
                    long1 = len(str(expr.children[0].value))
                    long2 = len(expr.children[2].value)
                    lenconcat = long1+long2
                    compteur+=4
                    return f"""lea rcx, {e1}\nmov ebx, {e1}\mov edx, 8\nmov rsi, rcx\nmov edi, ebx\nmov ebx, 0\ncall itoa\mov edx, {long1}\nmov ebx, {long2}\nadd edx, ebx\nmovsx rdx, ebx\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, ebx\nmov r10, rdx\nmov r11d, 0
                    \nmovsx rdx, ebx\nmov r8, rdx\nmov e9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rbx, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi
                    \nimul rbx, rbx, 16\nsub rsp, rbx\nmov rbx, rsp\nadd rbx, 0\nmov rax, rbx\nmov i, 0\njmp debut{compteur-3}
                    \ndebut{compteur-3}:\nmov ebx, rax\ncmp eax, len_concat\njl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                    \ndebut{compteur-2}:\nmov ebx, rax\ncdqe\nmovzx ecx, [{e2}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\nfin{compteur-2}
                    \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\ncdque\ncmp rbx, 6\nja debut{compteur-2}\nmov ebx, i\ncdqe\nmovzx ecx, [{str(e1)}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov rdx+rbx, cl\njmp debut{compteur-1}\nfin{compteur}"""
                else:
                    e1 = expr.children[0].value
                    e2 = expr.children[2].value
                    long1 = len(e1)
                    long2 = len(str(e2))
                    lenconcat = long1+long2
                    compteur+=4
                    return f"""lea rcx, {e1}\nmov ebx, {e1}\mov edx, 8\nmov rsi, rcx\nmov edi, ebx\nmov ebx, 0\ncall itoa\mov edx, {long1}\nmov ebx, {long2}\nadd edx, ebx\nmovsx rdx, ebx\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, ebx\nmov r10, rdx\nmov r11d, 0
                    \nmovsx rdx, ebx\nmov r8, rdx\nmov e9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rbx, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi
                    \nimul rbx, rbx, 16\nsub rsp, rbx\nmov rbx, rsp\nadd rbx, 0\nmov rax, rbx\nmov i, 0\njmp debut{compteur-3}
                    \ndebut{compteur-3}:\nmov ebx, rax\ncmp eax, len_concat\njl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                    \ndebut{compteur-2}:\nmov ebx, rax\ncdqe\nmovzx ecx, [{str(e2)}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\nfin{compteur-2}
                    \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\ncdque\ncmp rbx, 6\nja debut{compteur-2}\nmov ebx, i\ncdqe\nmovzx ecx, [{e1}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov rdx+rbx, cl\njmp debut{compteur-1}\nfin{compteur}"""
            elif (t1==1 and t2==2) or (t1==2 and t2==1):
                return #add the content of the pointer in the string
            elif t1==1 and t2==1:
                return #add pointers
            else:
                e1 = expr.children[0].value
                e2 = expr.children[2].value
                long1 = len(e1)
                long2 = len(e2)
                lenconcat = long1+long2
                compteur+=4
                return f"""mov edx, {long1}\nmov ebx, {long2}\nadd edx, ebx\nmovsx rdx, ebx\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, ebx\nmov r10, rdx\nmov r11d, 0
                \nmovsx rdx, ebx\nmov r8, rdx\nmov r9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rbx, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi
                \nimul rbx, rbx, 16\nsub rsp, rbx\nmov rbx, rsp\nadd rbx, 0\nmov rax, rbx\nmov i, 0\njmp debut{compteur-3}
                \ndebut{compteur-3}:\nmov ebx, rax\ncmp ebx, {lenconcat} jl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                \ndebut{compteur-2}:\nmov ebx, rax\ncdqe\nmovzx ecx, [{e2}+rbx]\nmov rdx, rax\nmov ebx, i\ncdqe\nmov [rdx+rbx], cl\nfin{compteur-2}
                \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                \ndebut{compteur}:\nmov ebx, i\ncdque\ncmp rbx, 6\nja debut{compteur-2}\nmov ebx, i\ncdqe\nmovzx ecx, [{e1}+rax]\nmov rdx, rax\nmov ebx, i\ncdqe\nmov [rdx+rbx], cl\njmp debut{compteur-1}\nfin{compteur}"""
        elif expr.children[1] == "-":
                return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje eq\neq: cmp {type(exp1)} 0\nje int\npointer\nint: sub rax, rbx\njmp fin\n"
        elif expr.children[1] == "*":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje sol1\nsol1: cmp {type(exp1)} 0\n je int\nint: imul rax, rbx\njmp fin\n\
                cmp {type(exp1)} 0\nje i1\ni1: cmp {type(exp2)} 1\nje i+p\njne i+s\n\
                cmp {type(exp1)} 1\nje p1\np1: cmp {type(exp2)} 0\nje i+p\n\
                cmp {type(exp1)} 2\nje s1\ns1: cmp {type(exp2)} 0\nje i+s\n\
                cmp {type(exp2)} 0\nje i2\ni2: cmp {type(exp1)} 1\nje i+p\njne i+s\n\
                cmp {type(exp2)} 1\nje p2\np2: cmp {type(exp1)} 0\nje i+p\n\
                cmp {type(exp2)} 2\nje s2\ns2: cmp {type(exp1)} 0\nje i+s\n\
                i+p: \njmp fin\n\
                i+s: \njmp fin\nfin:"
        elif (t1=="1" and t2=="0") or (t1=="0" and t2=="1"):
                return 
        elif (t1=="2" and t2=="0") or (t1=="0" and t2=="2"):
            if (t1=="0"):
                    e1 = expr.children[0].value
                    e2 = expr.children[2].value
                    long = len(e2)
                    lenconcat = long*e1
                    compteur+=3
                    return f"""mov eax, {long}\nimul eax, {e2}\nmovsx rdx, eax\nsub rdx, 1\nmov concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov ebx, 16\nmov edx, 0\ndiv rbx\nimul rax, rax, 16
                    \nsub rsp, rbx\nmov rax, rsp\nadd rax, 0\nmov concat, rax\nmov i, 0\nmov k, 0\n jmp debut{compteur-3}
                    \ndebut{compteur-2}:\nmov eax, k\ncmp eax, {e1}\njl debut{compteur-1}\nmov rax, concat\nmov rsp, rsi\nfin{compteur-2}
                    \ndebut{compteur-1}:\nmov eax, i\ncmp eax, {long}\njl debut{compteur}\nadd k, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\nmovsx rdx, eax\nmov rax, {e2}\nadd rax, rdx\nmovzx ecx, [rax]\nmov rdx, concat\nmov eax, i\ncdqe\nmov [rdx+rax], cl\nadd i, 1\nfin{compteur}"""
            else:
                    e1 = expr.children[0].value
                    e2 = expr.children[2].value
                    long = len(e1)
                    lenconcat = long*e2
                    compteur+=3
                    return f"""mov eax, {long}\nimul eax, {e1}\nmovsx rdx, eax\nsub rdx, 1\nmov concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov ebx, 16\nmov edx, 0\ndiv rbx\nimul rax, rax, 16
                    \nsub rsp, rbx\nmov rax, rsp\nadd rax, 0\nmov concat, rax\nmov i, 0\nmov k, 0\n jmp debut{compteur-3}
                    \ndebut{compteur-2}:\nmov eax, k\ncmp eax, {e2}\njl debut{compteur-1}\nmov rax, concat\nmov rsp, rsi\nfin{compteur-2}
                    \ndebut{compteur-1}:\nmov eax, i\ncmp eax, {long}\njl debut{compteur}\nadd k, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\nmovsx rdx, eax\nmov rax, {e1}\nadd rax, rdx\nmovzx ecx, [rax]\nmov rdx, concat\nmov eax, i\ncdqe\nmov [rdx+rax], cl\nadd i, 1\nfin{compteur}"""
        elif t1==0 and t2==0:
                return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\nimul rax, rbx"
        else:
                raise Exception("incompatible types for this operation")
    elif expr.children[1] == "/":
            return f"{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
            cmp {type(exp1)} {type(exp2)}\nje sol1\nsol1: cmp {type(exp1)} 0\n je int\nint: div rax, rbx"
    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    elif expr.data == "len":
        long = len(expr.children[0].children[0].value)
        return f"mov rax, {long}"
    elif expr.data == "isequal":
        if expr.children[0].children[0].value == expr.children[1].children[0].value:
            isequal = 1
        else:
            isequal = 0
        return f"mov rax, {isequal}"
    
    elif expr.data == "charat":
        v = expr.children[0].value
        e = expr.children[1].children[0].value
        return f"movzx eax, [{v}[{e}]]"
    else:
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
        return f"debut{index}:{e}\ncmp {te}, 0\nje int\ncmp {te} 1\nje point\npoint: \njne str\nstr: \nint :cmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "printf":
        e1 = compile_cmd(cmd.children[0])
        return f"{e1}\nmov rdi, fmt\nmov rsi, rax\nxor rax, rax\ncall printf"
    elif cmd.data =="if":
        e1 = compile_expr(cmd.children[0])
        e2 = compile_cmd(cmd.children[1])
        index=next(cpt)
        return f"{e1}\ncmp {te}, 0\nje int\ncmp {te} 1\nje point\npoint: \njne str\nstr: \nint: cmp rax, 0\njz fin{index}\n{e2}\nfin{index}"
    elif cmd.data == "setcharat":
        v = cmd.children[0].value
        e1 = compile_expr(cmd.children[1])
        e2 = compile_expr(cmd.children[2])
        return f"movzx eax, {e2}\nmov {v}[{e1}], al"
    else:
        raise Exception ("Not Implemented")


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