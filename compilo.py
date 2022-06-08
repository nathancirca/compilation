import lark

#définition de la grammaire du language utilisée 
#-----------------------------------------------------------------------------------------
grammaire = lark.Lark(""" 
variables : IDENTIFIANT ("," IDENTIFIANT)*
expr : IDENTIFIANT -> variable | NUMBER -> nombre | CHAR -> chaine | expr OP expr -> binexpr | "(" expr ")" -> parentexpr | "len" "(" expr ")" -> len | IDENTIFIANT".charAt" "(" expr ")" -> charat | expr "==" expr -> isequal
cmd : IDENTIFIANT "=" expr ";" -> assignment | "while" "(" expr ")" "{" bloc "}" -> while | "if" "(" expr ")" "{" bloc "}" -> if 
| "printf" "(" expr ")" ";" -> printf | IDENTIFIANT".setcharAt" "(" expr "," expr ")" ";"-> setcharat
bloc : (cmd)*
prog : "main" "(" variables ")" "{" bloc "return" "(" expr ")" ";" "}"
IDENTIFIANT : /[a-zA-Z][a-zA-Z0-9]*/
NUMBER : /[0-9]+/
OP : /[+\*>-]/ 
CHAR : /["][a-zA-Z0-9]*["]/
%import common.WS
%ignore WS
""", start = "prog" )

#---------------------------------------------------------------------------------------------
# définition des pp pour tous les types d'objet dans la grammaire
# (pp = pretty printer)
#---------------------------------------------------------------------------------------------

cpt = iter(range(10000))
compteur = 0

def pp_variables(vars):
    return """,""".join([t.value for t in vars.children])

def pp_expr(expr):
    if expr.data in {"variable", "nombre", "chaine"}:
        return expr.children[0].value
    elif expr.data == "binexpr":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[2])
        op = expr.children[1]
        return f"""{e1} {op} {e2}"""
    elif expr.data == """parentexpr""":
        return f"""({pp_expr(expr.children[0])})"""
    elif expr.data == "len":
        e = pp_expr(expr.children[0])
        return f"""len ( {e} )"""
    elif expr.data == "charat":
        v = expr.children[0].value
        e = pp_expr(expr.children[1])
        return f"""{v}.charAt( {e} )"""
    elif expr.data == "isequal":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[1])
        return f"""{e1} == {e2}"""
    else:
        raise Exception("Not implemented")

def pp_cmd(cmd):
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        rhs = pp_expr(cmd.children[1])
        return f"""{lhs} = {rhs};"""
    elif cmd.data == "printf":
        return f"""printf({pp_expr(cmd.children[0])});"""
    elif cmd.data in {"while","if"}:
        e=pp_expr(cmd.children[0])
        b=pp_bloc(cmd.children[1])
        return f"""{cmd.data}({e}) {{ {b}}}"""
    elif cmd.data =="setcharat":
        v = cmd.children[0].value
        e1 = pp_expr(cmd.children[1])
        e2 = pp_expr(cmd.children[2])
        return f"""{v}.setcharAt( {e1} , {e2} )"""
    else:
        raise Exception("Not implemented")


def pp_bloc(bloc):
    return """\n""".join([pp_cmd(t) for t in bloc.children])

def pp_prg(prg):
    vars = pp_variables(prg.children[0])
    bloc = pp_bloc(prg.children[1])
    ret = pp_expr(prg.children[2])
    return f"""main ({vars}){{ {bloc} return({ret});}}"""

def var_list(ast):
    if isinstance(ast, lark.Token):
        if ast.type == "IDENTIFIANT":
            return {ast.value}
        else:
            return set()
    s = set()
    for c in ast.children:
        s.update(var_list(c))
    return s

def compile(prg):
    with open("moule.asm") as f:
        code = f.read()
        var_decl= "\n".join([f"{x}: dq 0" for x in var_list(prg)])
        code = code.replace("VAR_DECL", var_decl)
        code = code.replace("RETURN", compile_expr(prg.children[2]))
        code = code.replace("BODY", compile_bloc(prg.children[1]))
        code = code.replace("INIT", compile_vars(prg.children[0]))
        return code

def compile_vars(ast):
    s=""
    for i in range(len(ast.children[1])):
        s+= f"mov rbx, [rbp-0x10]\nmov rdi,[rbx-{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].value}],rax\n"
    return s


def compile_expr(expr):
    global compteur
    if expr.data == "variable":
        return f"mov rax,[{expr.children[0].value}]"
    elif expr.data == "nombre":
        return f"mov rax,[{expr.children[0].value}]"
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
        long1=len(str(exp1.children[0].value))
        long2=len(str(exp2.children[0].value))
        if expr.children[1] == "+":
            return f"""{e1}\npush rax\n{e2}\npush rbx\npop rax\npop rbx\n\
                cmp {type(exp1)} {type(exp2)}\nje sol1\nsol1: cmp {type(exp1)} 0\nje int\ncmp {type(exp1)} 1\nje point\nstr: mov edx, {long1}\nmov eax, {long2}\nadd edx, eax\nmovsx rdx, eax\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, eax\nmov r10, rdx\nmov r11d, 0\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi\nimul rax, rax, 16\nsub rsp, rax\nmov rax, rsp\nadd rax, 0\nmov assign, rax\nmov i, 0\njmp debut{compteur-3}\ndebut{compteur}:\nmov eax, i\ncdque\ncmp rax, 6\nja debut{compteur-2}\nmov eax, i\ncdqe\nmovzx ecx, [{e1}+rax]\nmov rdx, assign\nmov eax, i\ncdqe\nmov rdx+rax, cl\njmp debut{compteur-1}\nfin{compteur}\npoint: \nint: add rax, rbx\njmp fin\n\\ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1} \ndebut{compteur-2}:\nmov eax, assign\ncdqe\nmovzx ecx, [{e2}+rax]\nmov rdx, assign\nmov eax, i\ncdqe\nmov rdx+rax, cl\nfin{compteur-2}\ndebut{compteur-3}:\nmov eax, assign\ncmp eax, {long1+long2} jl debut{compteur}\nmov rsp rsi\nfin{compteur-3}   
                cmp {type(exp1)} 0\nje i1\ni1: cmp {type(exp2)} 1\nje i+p\njne i+s\n\
                cmp {type(exp1)} 1\nje p1\np1: cmp {type(exp2)} 0\nje i+p\njne p+s\n\
                cmp {type(exp1)} 2\nje s1\ns1: cmp {type(exp2)} 0\nje i+s\njne p+s\n\
                i+p: \njmp fin\n\
                i+s: \nlea rcx, [{e1}]\nmov eax, [{e1}]\mov edx, 8\nmov rsi, rcx\nmov edi, eax\nmov eax, 0\ncall itoa\nmov lenconcat, {long1 + long2}\nmov eax, lenconcat\nmovsx rdx, eax\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov edi, 16\nmov edx, 0\ndiv rsi
                    \nimul rax, rax, 16\nsub rsp, rax\nmov rax, rsp\nadd rax, 0\nmov {assign}, rax\nmov i, 0\njmp debut{compteur-3}
                    \ndebut{compteur-3}:\nmov eax, {assign}\ncmp eax, {lenconcat} jl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                    \ndebut{compteur-2}:\nmov eax, {assign}\ncdqe\nmovzx ecx, [{e2}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\nfin{compteur-2}
                    \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\ncdque\ncmp rax, 6\nja debut{compteur-2}\nmov eax, i\ncdqe\nmovzx ecx, [{str(e1)}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\njmp debut{compteur-1}\nfin{compteur}\n\
                s+i: \njmp fin\n\
                p+s: \njmp fin\nfin:"""
                    return f"""lea rcx, [{e1}]\nmov eax, [{e1}]\mov edx, 8\nmov rsi, rcx\nmov edi, eax\nmov eax, 0\ncall itoa\nmov lenconcat, {long1 + long2}\nmov eax, [{lenconcat}]\nmovsx rdx, eax\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0
                    \nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov edi, 16\nmov edx, 0\ndiv rsi
                    \nimul rax, rax, 16\nsub rsp, rax\nmov rax, rsp\nadd rax, 0\nmov {assign}, rax\nmov i, 0\njmp debut{compteur-3}
                    \ndebut{compteur-3}:\nmov eax, {assign}\ncmp eax, {lenconcat} jl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                    \ndebut{compteur-2}:\nmov eax, {assign}\ncdqe\nmovzx ecx, [{e2}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\nfin{compteur-2}
                    \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\ncdque\ncmp rax, 6\nja debut{compteur-2}\nmov eax, i\ncdqe\nmovzx ecx, [{str(e1)}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\njmp debut{compteur-1}\nfin{compteur}"""
                    e1 = expr.children[0].value
                    e2 = expr.children[2].value
                    assign = expr.parent.children[0].value
                    long1 = len(expr.children[0].value)
                    long2 = len(expr.children[2].value)
                    lenconcat = long1+long2
                    compteur+=4
                    return f"""lea rcx, [{e2}]\nmov eax, [{e2}]\mov edx, 8\nmov rsi, rcx\nmov edi, eax\nmov eax, 0\ncall itoa\nmov lenconcat, {long1 + long2}\nmov eax, [{lenconcat}]\nmovsx rdx, eax\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0
                    \nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov edi, 16\nmov edx, 0\ndiv rdi
                    \nimul rax, rax, 16\nsub rsp, rax\nmov rax, rsp\nadd rax, 0\nmov {assign}, rax\nmov i, 0\njmp debut{compteur-3}
                    \ndebut{compteur-3}:\nmov eax, {assign}\ncmp eax, {lenconcat} jl debut{compteur}\nmov rsp rsi\nfin{compteur-3}
                    \ndebut{compteur-2}:\nmov eax, {assign}\ncdqe\nmovzx ecx, [{str(e2)}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\nfin{compteur-2}
                    \ndebut{compteur-1}:\nadd i, 1\nfin{compteur-1}
                    \ndebut{compteur}:\nmov eax, i\ncdque\ncmp rax, 6\nja debut{compteur-2}\nmov eax, i\ncdqe\nmovzx ecx, [{str(e1)}+rax]\nmov rdx, {assign}\nmov eax, i\ncdqe\nmov rdx+rax, cl\njmp debut{compteur-1}\nfin{compteur}"""
        else:
            raise Exception ("OP not implemented")
            
    elif expr.data == "parentexpr":
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

def compile_cmd(cmd):
    global compteur
    if cmd.data == "assignment":
        e1 = cmd.children[0].value
        e2 = compile_expr(cmd.children[1])
        if cmd.children[1].data == "charat":
            return f"{e2}\nmov [{e1}], al"
        else:
            return f"{e2}\nmov [{e1}], rax"
    elif cmd.data == "printf":
        e1 = compile_expr(cmd.children[0])
        return f"{e1}\nmov rdi, fmt\nmov rsi, rax\nxor rax, rax\ncall printf"
    elif cmd.data =="if":
        e1 = compile_expr(cmd.children[0])
        e2 = compile_cmd(cmd.children[1])
        compteur += 1
        return f"{e1}\n cmp rax, 0\njz fin{compteur}\n{e2}\nfin{compteur}"
    elif cmd.data =="while":
        e1 = compile_expr(cmd.children[0])
        e2 = compile_cmd(cmd.children[1])
        compteur +=1
        return f"debut{compteur}: {e1}\n cmp rax, 0\njz fin{compteur}\n{e2}\njmp debut{compteur}\nfin{compteur}"
    elif cmd.data == "setcharat":
        v = cmd.children[0].value
        e1 = compile_expr(cmd.children[1])
        e2 = compile_expr(cmd.children[2])
        return f"movzx eax, {e2}\nmov {v}[{e1}], al"
    else:
        raise Exception ("Not Implemented")

def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])


prg = grammaire.parse("""main(X,Y,L) {
X = "abcd";
L = len(X);
Y = X.charAt ( 2 );
X.setcharAt ( 2 , Y + 1 );
printf(X);
return (X==Y);}""")
print(prg)
print(compile(prg))

