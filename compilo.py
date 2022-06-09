import lark

grammaire = lark.Lark("""
variables : IDENTIFIANT ("," IDENTIFIANT)*
expr : IDENTIFIANT -> variable | NUMBER -> nombre | CHAR -> chaine | expr OP expr ->binexpr| "(" expr ")" -> parenexpr | "len" "(" expr ")" -> len | IDENTIFIANT".charAt" "(" expr ")" -> charat | expr "==" expr -> isequal|"*" expr -> pointer|"&" IDENTIFIANT -> adresse| "malloc" "(" NUMBER ")" -> malloc
cmd : IDENTIFIANT "=" expr ";" -> assignment | "while" "(" expr ")" "{" bloc "}" -> while | "if" "(" expr ")" "{" bloc "}" -> if | "printf" "(" expr ")" ";" -> printf | IDENTIFIANT".setcharAt" "(" expr "," expr ")" ";"-> setcharat|"*" IDENTIFIANT "=" expr ";"-> pointer |IDENTIFIANT "=" "malloc" "(" NUMBER ")" ";"-> malloc
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
index=0
def read_file(file):
    f = open(file, "r")
    code = f.read()
    f.close()
    return code

def pp_variables(vars):
    return ", ".join([t.value for t in vars.children])
def pp_expr(expr):
    if expr.data in {"variable","nombre","chaine"}:
        return expr.children[0].value
    elif expr.data == "binexpr":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[2])
        op = expr.children[1].value
        return f"{e1} {op} {e2}"
    elif expr.data == "parenexpr":
        return f"({pp_expr(expr.children[0])})"
    elif expr.data == "len":
        e = pp_expr(expr.children[0])
        return f"len( {e} )"
    elif expr.data == "charat":
        v = expr.children[0].value
        e = pp_expr(expr.hildren[1])
        return f"{v}.charAt({e})"
    elif expr.data == "isequal":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[1])
        return f"{e1} == {e2}"
    elif expr.data=="pointer":
        return f"*{pp_expr(expr.children[0])}"
    elif expr.data=="adresse":
        return f"&{expr.children[0].value}"
    elif expr.data=="malloc":
        return f"malloc({expr.children[0].value})"
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
    elif cmd.data == "setcharat":
        v = cmd.children[0].value
        e1 = pp_expr(cmd.children[1])
        e2 = pp_expr(cmd.children[2])
        return f"{v}.setcharAt( {e1} , {e2} )"
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


def adresse(expr):
    if expr.data=="adresse":
        return f"*{compile_expr(expr.children[0])}"
    else:
        return compile_expr(expr)

def pointer(expr):
    if expr.data=="pointer":
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
    elif expr.data=="chaine":
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
        return f"mov [{lhs}_type], [{expr.children[0].value}_type]"
    elif expr.data == "nombre" or expr.data=="adresse":
        return f"mov rcx,0\nmov [{lhs}_type], rcx"
    elif expr.data == "pointer" or expr.data=="malloc":
        return f"mov rcx,1\nmov [{lhs}_type], rcx"
    elif expr.data =="chaine":
        return f"mov rcx,2\nmov [{lhs}_type], rcx"
    elif expr.data == "binexpr":
        t1 = type(expr.children[0])
        t2 = type(expr.children[2])
        if expr.children[1] == "+":
            if (t1=="2" or t2=="2"):
                return f"mov rcx,2\nmov [{lhs}_type], rcx"
            elif (t1=="1" or t2=="1"):
                return f"mov rcx,1\nmov [{lhs}_type], rcx"
            else :
                return f"mov rcx,0\nmov [{lhs}_type], rcx"
    elif expr.data == "parenexpr":
        return type_assign(expr.chidlren[0])
    else :
        raise Exception("Not implemented")



def compile_expr(expr):
    global index
    index+=5
    if expr.data == "variable":
        return f"mov rax, [{expr.children[0].value}]"
    elif expr.data == "nombre":
        return f"mov rax,{expr.children[0].value}"
    elif expr.data == "chaine":
        e=''
        for i in expr.children[0].value:
            if ord(i) != 34:
                e+=f"{ord(i)}"
        return f"movabs rax, {e}"
    elif expr.data == "binexpr":
        exp1=expr.children[0]
        exp2=expr.children[2]
        e1 = compile_expr(exp1)
        e2 = compile_expr(exp2)
        if expr.children[1] == "+":
            long1 = len(str(exp1.children[0].value))
            long2 = len(str(exp2.children[0].value))

            return f"""{e1}\npush rax\n{e2}\npop rbx\nmov rcx, {type(exp1)}\nmov rdx,{type(exp2)}\n\
                cmp rcx, rdx\nje eqadd{index}\njne neqadd{index}\neqadd{index}: cmp rcx, 0\nje intadd{index}\ncmp rcx, 1\nje pointadd{index}\njne stradd{index}\nstradd{index}: \njmp fin{index}\npointadd{index}:\nadd rax,rbx\njmp fin{index}\nintadd{index}:\n add rax, rbx\njmp fin{index}\n\
                neqadd{index}: cmp rcx, 0\nje i1{index}\njne cp1{index}\ni1{index}: cmp rdx, 1\nje iaddp{index}\njne iadds{index}\n
                cp1{index}: cmp rcx, 1\nje p1{index}\njne cs1{index}\np1{index}: cmp rdx, 0\nje iaddp{index}\njne fin{index}\n
                cs1{index}: cmp rdx, 0\nje saddi{index}\njne fin{index}\n
                iaddp{index}: add rax,rbx\njmp fin{index}\n
                iadds{index}: lea rax, {exp1.children[0].value}\nmov rbx, {exp1.children[0].value}\nmov edx, 8\nmov rsi, rax\nmov edi, rbx\nmov ebx, 0\ncall itoa\nmov edx, {long1}\nmov ebx, {long2}\nadd edx, ebx\nmovsx rdx, ebx\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, ebx\nmov r10, rdx\nmov r11d, 0\nmovsx rdx, ebx\nmov r8, rdx\nmov e9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rbx, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi\nimul rbx, rbx, 16\nsub rsp, rbx\nmov rbx, rsp\nadd rbx, 0\nmov rax, rbx\nmov i, 0\njmp debut_iadds{index-4}\ndebut_iadds{index-1}:\nmov eax, i\ncdqe\ncmp rbx, 6\nja debut_iadds{index-3}\nmov ebx, i\ncdqe\nmovzx ecx, [{exp1.children[0].value}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\njmp debut_iadds{index-2}\nfin_iadds{index-1}:\ndebut_iadds{index-2}:\nadd i, 1\nfin_iadds{index-2}:\ndebut_iadds{index-4}:\nmov ebx, rax\ncmp eax, len_concat\njl debut_iadds{index-1}\nmov rsp, rsi\nfin_iadds{index-4}:\ndebut_iadds{index-3}:\nmov ebx, rax\ncdqe\nmovzx ecx, [{exp2.children[0].value}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\nfin_iadds{index-3}:   
                saddi{index}: lea rax, {exp1.children[0].value}\nmov rbx, {exp1.children[0].value}\nmov edx, 8\nmov rsi, rax\nmov edi, rbx\nmov ebx, 0\ncall itoa\nmov edx, {long1}\nmov ebx, {long2}\nadd edx, ebx\nmovsx rdx, ebx\nsub rdx, 1\nmov len_concat, rdx\nmovsx rdx, ebx\nmov r10, rdx\nmov r11d, 0\nmovsx rdx, ebx\nmov r8, rdx\nmov e9d, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rbx, rdx\nmov esi, 16\nmov edx, 0\ndiv rsi\nimul rbx, rbx, 16\nsub rsp, rbx\nmov rbx, rsp\nadd rbx, 0\nmov rax, rbx\nmov i, 0\njmp debut_saddi{index-4}\ndebut_saddu{index-1}:\nmov eax, i\ncdqe\ncmp rbx, 6\nja debut_saddi{index-3}\nmov ebx, i\ncdqe\nmovzx ecx, [{exp1.children[0].value}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\njmp debut_saddi{index-2}\nfin_saddi{index-1}:\ndebut_saddi{index-2}:\nadd i, 1\nfin_saddi{index-2}:\ndebut_saddi{index-4}:\nmov ebx, rax\ncmp eax, len_concat\njl debut_saddi{index-1}\nmov rsp, rsi\nfin_saddi{index-4}:\ndebut_saddi{index-3}:\nmov ebx, rax\ncdqe\nmovzx ecx, [{exp2.children[0].value}+rbx]\nmov rdx, rax\nmov eax, i\ncdqe\nmov [rdx+rbx], cl\nfin_saddi{index-3}:
                fin{index}:"""
        elif expr.children[1] == "-":
                return f"{e1}\npush rax\n{e2}\npop rbx\nmov rcx, {type(exp1)}\nmov rdx,{type(exp2)}\n\
                cmp rcx, rdx\nje eq{index}\njne fin{index}\neq{index}: cmp rcx, 2\nje fin{index}\nsub rax, rbx\njmp fin{index}\nfin{index}:"
        elif expr.children[1] == "*":
            long1 = len(str(exp1.children[0].value))
            long2 = len(str(exp2.children[0].value))
            compteur+=3
            return f"""{e1}\npush rax\n{e2}\npop rbx\nmov rcx, {type(exp1)}\nmov rdx,{type(exp2)}\n\
                cmp rcx, rdx\nje eqmul{index}\njne neq{index}\neqmul{index}: cmp rcx, 0\n je intmul{index}\nintmul: imul rax, rbx\njmp fin{index}\n\
                neq{index}: cmp rcx, 0\nje i1mul{index}\njne cp{index}\ni1mul{index}: cmp rdx, 1\nje imulp{index}\njne imuls{index}\n\
                cp{index}: cmp rcx, 1\nje p1mul{index}\njne cs{index}\np1mul{index}: cmp rdx, 0\nje imulp{index}\n\
                cs{index}: cmp rdx, 0\nje smuli{index}\n\
                imulp{index}: imul rax, rbx\njmp fin{index}\n\
                imuls{index}: lea rax, {e1}\nmov rdi, rax\ncall strlen\nimul eax, {e2}\nmovsx rdx, eax\nsub rdx, 1\nmov concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov ebx, 16\nmov edx, 0\ndiv rbx\nimul rax, rax, 16\nsub rsp, rbx\nmov rax, rsp\nadd rax, 0\nmov concat, rax\nmov i, 0\nmov k, 0\n jmp debut_imuls{index-3}\ndebut_imuls{index-1}:\nmov eax, i\nmovsx rdx, eax\nmov rax, {e2}\nadd rax, rdx\nmovzx ecx, [rax]\nmov rdx, concat\nmov eax, i\ncdqe\nmov [rdx+rax], cl\nadd i, 1\nfin_imuls{index-1}:\ndebut_imuls{index-2}:\nmov eax, i\ncmp eax, {long1}\njl debut_imuls{index-1}\nadd k, 1\nfin_imuls{index-2}:\ndebut_imuls{index-3}:\nmov eax, k\ncmp eax, {e1}\njl debut_imuls{index-2}\nmov rax, concat\nmov rsp, rsi\nfin_imuls{index-3}: 
                smuli{index}: lea rax, {e2}\nmov rdi, rax\ncall strlen\nimul eax, {e2}\nmovsx rdx, eax\nsub rdx, 1\nmov concat, rdx\nmovsx rdx, eax\nmov r8, rdx\nmov r9d, 0\nmovsx rdx, eax\nmov rcx, rdx\nmov ebx, 0\ncdqe\nmov edx, 16\nsub rdx, 1\nadd rax, rdx\nmov ebx, 16\nmov edx, 0\ndiv rbx\nimul rax, rax, 16\nsub rsp, rbx\nmov rax, rsp\nadd rax, 0\nmov concat, rax\nmov i, 0\nmov k, 0\n jmp debut_smuli{index-3}\ndebut_smuli{index-1}:\nmov eax, i\nmovsx rdx, eax\nmov rax, {e1}\nadd rax, rdx\nmovzx ecx, [rax]\nmov rdx, concat\nmov eax, i\ncdqe\nmov [rdx+rax], cl\nadd i, 1\nfin_smuli{index-1}:\ndebut_smuli{index-2}:\nmov eax, i\ncmp eax, {long2}\njl debut_smuli{index-1}\nadd k, 1\nfin_smuli{index-2}:\ndebut_smuli{index-3}:\nmov eax, k\ncmp eax, {e2}\njl debut_smuli{index-2}\nmov rax, concat\nmov rsp, rsi\nfin_smuli{index-3}:
                fin{index}"""

        elif expr.children[1] == "/":
            return f"{e1}\npush rax\n{e2}\npop rbx\nmov rcx, {type(exp1)}\nmov rdx,{type(exp2)}\n\
                cmp rcx, rdx\nje eqdiv{index}\njne fin{index}\neqdiv{index}: cmp rcx, 0\n je intdiv{index}\njne fin{index}\nintdiv{index}: div rax, rbx\nfin{index}:"
        else:
                raise Exception("incompatible types for this operation")
    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    elif expr.data == "len":
        e1= expr.children[0]
        return f"""lea rax, {e1}\nmov rdi, rax\ncall strlen"""
    elif expr.data == "isequal":
        if expr.children[0].children[0].value == expr.children[1].children[0].value:
            isequal = 1
        else:
            isequal = 0
        return f"mov rax, {isequal}"
    elif expr.data == "charat":
        v = expr.children[0].value
        e = expr.children[1].children[0].value
        return f"movzx rax, [{v} - {e}]\n"
    elif expr.data=="pointer":
        #return f"\nmov rax,QWORD [rbp-8]\nmov QWORD [rax],{expr.children[1].value}\npop rbp"
        return f"\nmov rax,QWORD [rbp-8]\nmov eax, [rax]\nmov  [rbp-12], eax"

        #return f"\npush rbp\nmov rbp,rsp\nmov rax,QWORD [rbp+8]\nmov QWORD [rax],{expr.children[1].value}\npop rbp"
    elif expr.data=="adresse":
        return f"\npush rbp\nmov rbp,rsp\nmov QWORD [rbp], {expr.children[0]}\nlea rax,[rbp]\nmov QWORD [rbp],rax\npop rbp"
    elif expr.data=="malloc":
        return f"mov edi,{expr.children[0].value}\nextern malloc\ncall malloc"
    else:
        raise Exception("Not implemented")
    

def compile_cmd(cmd):
    global index
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        expr = cmd.children[1]
        rhs = compile_expr(expr)
        return f"{rhs}\n{type_assign(expr,lhs)}\nmov [{lhs}],rax"
    elif cmd.data == "while":
        e = compile_expr(cmd.children[0])
        te = type(cmd.children[0])
        b = compile_bloc(cmd.children[1])
        index+=1
        print(index)
        return f"debut{index}:{e}\ncmp {te}, 0\nje int{index}\ncmp {te}, 1\nje point{index}\njne str{index}\npoint{index}:\nmov eax, [rax]\ntest eax, eax\njz fin{index}\njnz ok{index}\nstr{index}: \nint{index}:\n cmp rax,0\njz fin{index}\n jnz ok{index}\nok{index}: {b}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "printf":
        e1 = compile_cmd(cmd.children[0])
        return f"{e1}\nmov rdi, fmt\nmov rsi, rax\nxor rax, rax\ncall printf"
    elif cmd.data =="if":
        e1 = compile_expr(cmd.children[0])
        e2 = compile_cmd(cmd.children[1])
        te1=type(cmd.children[0])
        index+=1
        return f"{e1}\ncmp {te1}, 0\nje int\ncmp {te1} 1\nje point\njne str\npoint: mov eax, [rax]\ntest eax, eax\njz fin{index}\njnz ok{index}\nstr: \nint :cmp rax,0\njz fin{index}\njnz ok{index}\nok: {e2}\nfin{index}:\n"
    elif cmd.data=="pointer":
        lhs= cmd.children[0].value
        rhs=compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    elif cmd.data == "setcharat":
        v = cmd.children[0].value
        e1 = cmd.children[1].children[0].value
        e2 = cmd.children[2]
        if type(e2) == "2":
            e_str=''
            len_str = 0
            for i in e2.children[0].value:
                if ord(i) != 34:
                    e_str+=f"{ord(i)}"
                    len_str+=1
            if len_str== 1:
                return f"mov rax, {e_str}\nmovzx [{v} - {e1}], rax\n"
            else:
                raise Exception ("Too long string")
        else:
            str_e2 =  str(e2.children[0].value)
            e_str=''
            len_str=0
            for i in str_e2:
                 if ord(i) != 34:
                    e_str+=f"{ord(i)}"
                    len_str+=1
            if len_str == 1:
                return f"mov rax, {e_str}\nmovzx [{v} - {e1}], rax\n"
            else:
                raise Exception ("Too long string")
    else :
        raise Exception("Not implemented")


def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])

def compile_vars(ast):
    s="\n"
    for i in range(len(ast.children)):
        s+= f"mov rbx, [rbp+0x10]\nmov rdi,[rbx+{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].value}],rax\n"
    return s

def compile(prg):
    with open("moule.asm") as f:
        code = f.read()
        var_decl = "\n".join([f"{x}: dq 0\n{x}_type: dq 0" for x in var_list(prg)])
        code = code.replace("VAR_DECL", var_decl)
        code = code.replace("RETURN",compile_expr(prg.children[2]))
        code = code.replace("BODY", compile_bloc(prg.children[1]))
        code = code.replace("VAR_INIT", compile_vars(prg.children[0]))
        g = open("demo.asm", "w")
        g.write(code)
        g.close()
        return code

#prg = grammaire.parse("""main(X) {X = "abcdef"; X.setcharAt( 3 ,"b"); return(X);}""")
#print(compile(prg))

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

prg=grammaire.parse(read_file("test.txt"))
print(prg)
print(pp_prg(prg))
compile(prg)