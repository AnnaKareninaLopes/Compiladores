from ttokenC import TOKEN
from lexicoC import Lexico
from semanticoC import AnalisadorSemantico  # Importa o novo "cérebro"


class Sintatico:
    def __init__(self, nomeArquivo):
        self.lexico = Lexico(nomeArquivo)
        # O Sintatico gerencia uma instância do Analisador Semântico
        self.semantico = AnalisadorSemantico()

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.program()
            self.consome(TOKEN.eof)
            print("\nTraduzido com sucesso!")
        except Exception as e:
            print("\nFalha na tradução:", e)

    def consome(self, tokenAtual):
        (token, _, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgLido = TOKEN.msg(token)
            msgEsperado = TOKEN.msg(tokenAtual)
            raise Exception(
                f"Erro Sintático na linha {linha}, coluna {coluna}: esperado '{msgEsperado}', mas foi lido '{msgLido}'")

    # --- Métodos de Análise Sintática (apenas delegam a semântica) ---

    def program(self):
        if self.tokenLido[0] in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}:
            self.function()
            self.program()

    def function(self):
        return_type = self.type()
        func_name = self.tokenLido[1]
        func_token = self.tokenLido
        self.consome(TOKEN.ident)

        # Delega a declaração da função para o semantico
        func_symbol = self.semantico.declara_funcao(func_name, return_type, func_token)

        self.consome(TOKEN.abrePar)
        self.semantico.enter_scope()
        self.argList(func_symbol.params)  # Passa a lista de params do símbolo
        self.consome(TOKEN.fechaPar)
        self.compoundStmt()
        self.semantico.leave_scope()

    def argList(self, params_list):
        if self.tokenLido[0] in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}:
            self.arg(params_list)
            self.restoArgList(params_list)

    def restoArgList(self, params_list):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            self.arg(params_list)
            self.restoArgList(params_list)

    def arg(self, params_list):
        arg_type = self.type()
        arg_name, is_array = self.identArg()
        # Delega a declaração do argumento para o semantico
        self.semantico.declara_argumento(arg_name, arg_type, is_array, params_list, self.tokenLido)

    def identArg(self):
        arg_name = self.tokenLido[1]
        self.consome(TOKEN.ident)
        is_array = self.opcIdentArg()
        return (arg_name, is_array)

    def opcIdentArg(self):
        if self.tokenLido[0] == TOKEN.abreColchete:
            self.consome(TOKEN.abreColchete)
            self.consome(TOKEN.fechaColchete)
            return True
        return False

    def compoundStmt(self):
        self.consome(TOKEN.abreChave)
        self.semantico.enter_scope()
        self.stmtList()
        self.consome(TOKEN.fechaChave)
        self.semantico.leave_scope()

    def stmtList(self):
        first_stmt = {
            TOKEN.BREAK, TOKEN.CONTINUE, TOKEN.RETURN, TOKEN.ptoVirg, TOKEN.FOR, TOKEN.IF, TOKEN.WHILE,
            TOKEN.abreChave, TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR, TOKEN.NOT, TOKEN.mais, TOKEN.menos,
            TOKEN.abrePar, TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString, TOKEN.ident
        }
        if self.tokenLido[0] in first_stmt:
            self.stmt()
            self.stmtList()

    def stmt(self):
        first_expr = {TOKEN.NOT, TOKEN.mais, TOKEN.menos, TOKEN.abrePar, TOKEN.valorInt, TOKEN.valorFloat,
                      TOKEN.valorChar, TOKEN.valorString, TOKEN.ident}

        token_info = self.tokenLido;
        token = token_info[0]

        if token == TOKEN.FOR:
            self.semantico.entrar_laco();
            self.forStmt();
            self.semantico.sair_laco()
        elif token == TOKEN.WHILE:
            self.semantico.entrar_laco();
            self.whileStmt();
            self.semantico.sair_laco()
        elif token == TOKEN.IF:
            self.ifStmt()
        elif token == TOKEN.abreChave:
            self.compoundStmt()
        elif token in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}:
            self.declaration()
        elif token == TOKEN.BREAK:
            self.semantico.verificar_dentro_de_laco(token_info);
            self.consome(TOKEN.BREAK);
            self.consome(TOKEN.ptoVirg)
        elif token == TOKEN.CONTINUE:
            self.semantico.verificar_dentro_de_laco(token_info);
            self.consome(TOKEN.CONTINUE);
            self.consome(TOKEN.ptoVirg)
        elif token == TOKEN.RETURN:
            self.consome(TOKEN.RETURN)
            tipo_expr, _, _ = self.expr()
            self.semantico.verifica_retorno(tipo_expr, token_info)
            self.consome(TOKEN.ptoVirg)
        elif token in first_expr:
            self.expr();
            self.consome(TOKEN.ptoVirg)
        else:
            self.consome(TOKEN.ptoVirg)

    def forStmt(self):
        self.consome(TOKEN.FOR); self.consome(TOKEN.abrePar); self.expr(); self.consome(
            TOKEN.ptoVirg); self.optExpr(); self.consome(TOKEN.ptoVirg); self.optExpr(); self.consome(
            TOKEN.fechaPar); self.stmt()

    def optExpr(self):
        first_expr = {TOKEN.NOT, TOKEN.mais, TOKEN.menos, TOKEN.abrePar, TOKEN.valorInt, TOKEN.valorFloat,
                      TOKEN.valorChar, TOKEN.valorString, TOKEN.ident}
        if self.tokenLido[0] in first_expr: self.expr()

    def whileStmt(self):
        self.consome(TOKEN.WHILE); self.consome(TOKEN.abrePar); self.expr(); self.consome(TOKEN.fechaPar); self.stmt()

    def ifStmt(self):
        self.consome(TOKEN.IF); self.consome(TOKEN.abrePar); self.expr(); self.consome(
            TOKEN.fechaPar); self.stmt(); self.elsePart()

    def elsePart(self):
        if self.tokenLido[0] == TOKEN.ELSE: self.consome(TOKEN.ELSE); self.stmt()

    def declaration(self):
        var_type = self.type()
        self.identList(var_type)
        self.consome(TOKEN.ptoVirg)

    def type(self):
        token = self.tokenLido[0]
        if token in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}: self.consome(token); return token
        raise Exception(f"Erro Sintático na linha {self.tokenLido[2]}: tipo inválido '{TOKEN.msg(token)}'")

    def identList(self, var_type):
        self.identDeclar(var_type); self.restoIdentList(var_type)

    def restoIdentList(self, var_type):
        if self.tokenLido[0] == TOKEN.virg: self.consome(TOKEN.virg); self.identList(var_type)

    def identDeclar(self, var_type):
        var_name = self.tokenLido[1]
        var_token = self.tokenLido
        self.consome(TOKEN.ident)
        is_array, size = self.opcIdentDeclar()
        self.semantico.declara_variavel(var_name, var_type, is_array, var_token)

    def opcIdentDeclar(self):
        if self.tokenLido[0] == TOKEN.abreColchete:
            self.consome(TOKEN.abreColchete);
            size = self.tokenLido[1];
            self.consome(TOKEN.valorInt);
            self.consome(TOKEN.fechaColchete)
            return (True, size)
        return (False, None)

    # --- Métodos de Análise de Expressão ---

    def expr(self):
        return self.restoExpr(self.log())

    def restoExpr(self, tipo_codigo_natureza_esquerdo):
        # 1. Desempacota a tupla tripla que vem da expressão da esquerda.
        tipo_esquerdo, codigo_esquerdo, natureza_esquerda = tipo_codigo_natureza_esquerdo
        if self.tokenLido[0] == TOKEN.atrib:
            #    Verifica se a "natureza" do lado esquerdo permite atribuição.
            if natureza_esquerda not in {'identificador', 'acesso_vetor'}:
                raise Exception(
                    f"Erro Semântico na linha {self.tokenLido[2]}: O lado esquerdo de uma atribuição deve ser uma variável ou um elemento de vetor (L-value).")

            op_token = self.tokenLido
            self.consome(TOKEN.atrib)

            # 3. A expressão da direita também retorna uma tupla tripla.
            tipo_direito_tupla, codigo_direito, _ = self.expr() # Se não for aceitar a = b = c, coloca self.log()

            # 4. A validação usa apenas a parte do TIPO de cada lado.
            self.semantico.validar_atribuicao(tipo_esquerdo, tipo_direito_tupla, op_token)

            # Gera o código para a atribuição
            novo_codigo = f"{codigo_esquerdo} = {codigo_direito}"

            # Continua a recursão para atribuições encadeadas (a = b = c)
            # O resultado de uma atribuição é sempre um R-value ('expressao')
            return self.restoExpr((tipo_esquerdo, novo_codigo, 'expressao'))

        # Se não houver '=', apenas retorna a tupla original que recebeu.
        return (tipo_esquerdo, codigo_esquerdo, natureza_esquerda)

    def log(self):
        return self.restoLog(self.nao())

    def restoLog(self, tipo_codigo_natureza_esquerdo):
        tipo_esq, codigo_esq, nat_esq = tipo_codigo_natureza_esquerdo
        operador = self.tokenLido[0]
        if operador in {TOKEN.AND, TOKEN.OR}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_dir, codigo_dir, _ = self.nao()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esq, operador, tipo_dir, op_token)
            novo_codigo = f"({codigo_esq} {TOKEN.msg(operador)} {codigo_dir})"
            return self.restoLog((tipo_resultado, novo_codigo, 'expressao'))
        return (tipo_esq, codigo_esq, nat_esq)

    def nao(self):
        operador = self.tokenLido[0]
        if operador == TOKEN.NOT:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_operando, codigo_operando, _ = self.nao()
            tipo_resultado = self.semantico.validar_operacao_unaria(operador, tipo_operando, op_token)
            novo_codigo = f"(!{codigo_operando})"
            return (tipo_resultado, novo_codigo, 'expressao')
        else:
            return self.rel()

    def rel(self):
        return self.restoRel(self.soma())

    def restoRel(self, tipo_codigo_natureza_esquerdo):
        tipo_esq, codigo_esq, nat_esq = tipo_codigo_natureza_esquerdo
        operador = self.tokenLido[0]
        if operador in {TOKEN.igual, TOKEN.diferente, TOKEN.menor, TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_dir, codigo_dir, _ = self.soma()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esq, operador, tipo_dir, op_token)
            novo_codigo = f"({codigo_esq} {TOKEN.msg(operador)} {codigo_dir})"
            return self.restoRel((tipo_resultado, novo_codigo, 'expressao'))
        return (tipo_esq, codigo_esq, nat_esq)

    def soma(self):
        return self.restoSoma(self.mult())

    def restoSoma(self, tipo_codigo_natureza_esquerdo):
        tipo_esq, codigo_esq, nat_esq = tipo_codigo_natureza_esquerdo
        operador = self.tokenLido[0]
        if operador in {TOKEN.mais, TOKEN.menos}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_dir, codigo_dir, _ = self.mult()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esq, operador, tipo_dir, op_token)
            novo_codigo = f"({codigo_esq} {TOKEN.msg(operador)} {codigo_dir})"
            return self.restoSoma((tipo_resultado, novo_codigo, 'expressao'))
        return (tipo_esq, codigo_esq, nat_esq)

    def mult(self):
        return self.restoMult(self.uno())

    def restoMult(self, tipo_codigo_natureza_esquerdo):
        tipo_esq, codigo_esq, nat_esq = tipo_codigo_natureza_esquerdo
        operador = self.tokenLido[0]
        if operador in {TOKEN.multiplica, TOKEN.divide, TOKEN.resto}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_dir, codigo_dir, _ = self.uno()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esq, operador, tipo_dir, op_token)
            novo_codigo = f"({codigo_esq} {TOKEN.msg(operador)} {codigo_dir})"
            return self.restoMult((tipo_resultado, novo_codigo, 'expressao'))
        return (tipo_esq, codigo_esq, nat_esq)

    def uno(self):
        operador = self.tokenLido[0]
        if operador in {TOKEN.menos, TOKEN.mais}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_operando, codigo_operando, _ = self.uno()
            tipo_resultado = self.semantico.validar_operacao_unaria(operador, tipo_operando, op_token)
            novo_codigo = f"({TOKEN.msg(operador)}{codigo_operando})"
            return (tipo_resultado, novo_codigo, 'expressao')
        else:
            return self.folha()

    def folha(self):
        token, lexema, linha, _ = self.tokenLido
        token_info = self.tokenLido

        if token == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            tipo, codigo, _ = self.expr()
            self.consome(TOKEN.fechaPar)
            return (tipo, f"({codigo})", 'expressao')

        elif token == TOKEN.ident:
            simbolo = self.semantico.verifica_identificador_declarado(lexema, token_info)
            self.consome(TOKEN.ident)
            return self.opcIdentifier(simbolo)

        elif token == TOKEN.valorInt:
            self.consome(TOKEN.valorInt);
            return ((TOKEN.INT, False), lexema, 'literal')

        elif token == TOKEN.valorFloat:
            self.consome(TOKEN.valorFloat);
            return ((TOKEN.FLOAT, False), lexema, 'literal')

        elif token == TOKEN.valorChar:
            self.consome(TOKEN.valorChar);
            return ((TOKEN.CHAR, False), lexema, 'literal')

        else:
            self.consome(TOKEN.valorString);
            return ((TOKEN.CHAR, True), lexema, 'literal')

    def opcIdentifier(self, symbol):
        token_info = self.tokenLido
        token = token_info[0]

        # --- Caminho 1: Acesso a Vetor ---
        if token == TOKEN.abreColchete:
            if not symbol.is_array: raise Exception(
                f"Erro Semântico na linha {token_info[2]}: '{symbol.name}' não é um vetor e não pode ser indexado.")
            self.consome(TOKEN.abreColchete)
            tipo_indice, codigo_indice, _ = self.expr()
            if tipo_indice != (TOKEN.INT, False): raise Exception(
                f"Erro Semântico na linha {token_info[2]}: O índice de um vetor deve ser um inteiro.")
            self.consome(TOKEN.fechaColchete)

            tipo_elemento = (symbol.sym_type, False)
            codigo_acesso = f"{symbol.name}[{codigo_indice}]"
            natureza = 'acesso_vetor' # L-value

            return (tipo_elemento, codigo_acesso, natureza)

        # --- Caminho 2: Chamada de Função ---
        elif token == TOKEN.abrePar:
            if symbol.category != 'funcao': raise Exception(
                f"Erro Semântico na linha {token_info[2]}: '{symbol.name}' não é uma função e não pode ser chamada.")

            self.consome(TOKEN.abrePar)
            tipos_args, codigos_args = self.params(symbol)
            self.semantico.validar_chamada_funcao(symbol, tipos_args, token_info)
            self.consome(TOKEN.fechaPar)

            tipo_retorno = (symbol.sym_type, False)
            codigo_chamada = f"{symbol.name}({', '.join(codigos_args)})"
            natureza = 'expressao' # R-value

            return (tipo_retorno, codigo_chamada, natureza)

            # --- Caminho 3: Uso Simples da Variável ---
        else:
            tipo_variavel = (symbol.sym_type, symbol.is_array)
            codigo_variavel = symbol.name
            natureza = 'identificador'  # L-value

            return (tipo_variavel, codigo_variavel, natureza)

    def params(self, func_symbol):
        first_expr = {TOKEN.NOT, TOKEN.mais, TOKEN.menos, TOKEN.abrePar, TOKEN.valorInt, TOKEN.valorFloat,
                      TOKEN.valorChar, TOKEN.valorString, TOKEN.ident}

        tipos_passados = []
        codigos_passados = []

        if self.tokenLido[0] in first_expr:
            tipo_arg, codigo_arg, _  = self.expr()
            tipos_passados.append(tipo_arg)
            codigos_passados.append(codigo_arg)
            self.restoParams(tipos_passados, codigos_passados)

        return tipos_passados, codigos_passados

    def restoParams(self, tipos_passados, codigos_passados):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo_arg, codigo_arg, _ = self.expr()
            tipos_passados.append(tipo_arg)
            codigos_passados.append(codigo_arg)
            self.restoParams(tipos_passados, codigos_passados)


if __name__ == '__main__':
    sintatico = Sintatico("novoTeste.txt")
    sintatico.traduz()