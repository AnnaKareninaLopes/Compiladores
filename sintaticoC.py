from ttokenC import TOKEN
from lexicoC import Lexico
from semanticoC import AnalisadorSemantico  # Importa o novo "cérebro"
import traceback


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
        token_info = self.tokenLido
        token = token_info[0]

        if token == TOKEN.FOR:
            self.semantico.entrar_laco(); self.forStmt(); self.semantico.sair_laco()
        elif token == TOKEN.WHILE:
            self.semantico.entrar_laco(); self.whileStmt(); self.semantico.sair_laco()
        elif token == TOKEN.IF:
            self.ifStmt()
        elif token == TOKEN.abreChave:
            self.compoundStmt()
        elif token in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}:
            self.declaration()
        elif token == TOKEN.BREAK:
            self.semantico.verificar_dentro_de_laco(token_info); self.consome(TOKEN.BREAK); self.consome(TOKEN.ptoVirg)
        elif token == TOKEN.CONTINUE:
            self.semantico.verificar_dentro_de_laco(token_info); self.consome(TOKEN.CONTINUE); self.consome(
                TOKEN.ptoVirg)
        elif token == TOKEN.RETURN:
            self.consome(TOKEN.RETURN)
            tipo_expr = self.expr()
            self.semantico.verifica_retorno(tipo_expr, token_info)
            self.consome(TOKEN.ptoVirg)
        elif token in first_expr:
            self.expr(); self.consome(TOKEN.ptoVirg)
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

    def restoExpr(self, tipo_esquerdo):
        if self.tokenLido[0] == TOKEN.atrib:
            op_token = self.tokenLido
            self.consome(TOKEN.atrib)
            tipo_direito = self.expr()
            self.semantico.validar_atribuicao(tipo_esquerdo, tipo_direito, op_token)
            return self.restoExpr(tipo_esquerdo)
        return tipo_esquerdo

    def log(self):
        return self.restoLog(self.nao())

    def restoLog(self, tipo_esquerdo):
        operador = self.tokenLido[0]
        if operador in {TOKEN.AND, TOKEN.OR}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_direito = self.nao()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, op_token)
            return self.restoLog(tipo_resultado)
        return tipo_esquerdo

    def nao(self):
        operador = self.tokenLido[0]
        if operador == TOKEN.NOT:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_operando = self.nao()
            return self.semantico.validar_op_unaria(operador, tipo_operando, op_token)
        else:
            return self.rel()

    def rel(self):
        return self.restoRel(self.soma())

    def restoRel(self, tipo_esquerdo):
        operador = self.tokenLido[0]
        if operador in {TOKEN.igual, TOKEN.diferente, TOKEN.menor, TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_direito = self.soma()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, op_token)
            return self.restoRel(tipo_resultado)
        return tipo_esquerdo

    def soma(self):
        return self.restoSoma(self.mult())

    def restoSoma(self, tipo_esquerdo):
        operador = self.tokenLido[0]
        if operador in {TOKEN.mais, TOKEN.menos}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_direito = self.mult()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, op_token)
            return self.restoSoma(tipo_resultado)
        return tipo_esquerdo

    def mult(self):
        return self.restoMult(self.uno())

    def restoMult(self, tipo_esquerdo):
        operador = self.tokenLido[0]
        if operador in {TOKEN.multiplica, TOKEN.divide, TOKEN.resto}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_direito = self.uno()
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, op_token)
            return self.restoMult(tipo_resultado)
        return tipo_esquerdo

    def uno(self):
        operador = self.tokenLido[0]
        if operador in {TOKEN.menos, TOKEN.mais}:
            op_token = self.tokenLido
            self.consome(operador)
            tipo_operando = self.uno()
            return self.semantico.validar_operacao_unaria(operador, tipo_operando, op_token)
        else:
            return self.folha()

    def folha(self):
        token, lexema, linha, _ = self.tokenLido
        token_info = self.tokenLido
        if token == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            tipo_expr = self.expr()
            self.consome(TOKEN.fechaPar)
            return tipo_expr
        elif token == TOKEN.ident:
            simbolo = self.semantico.verifica_identificador_declarado(lexema, token_info)
            self.consome(TOKEN.ident)
            self.opcIdentifier(simbolo)
            return (simbolo.sym_type, simbolo.is_array)
        elif token == TOKEN.valorInt:
            self.consome(TOKEN.valorInt); return (TOKEN.INT, False)
        elif token == TOKEN.valorFloat:
            self.consome(TOKEN.valorFloat); return (TOKEN.FLOAT, False)
        elif token == TOKEN.valorChar:
            self.consome(TOKEN.valorChar); return (TOKEN.CHAR, False)
        else:
            self.consome(TOKEN.valorString); return (TOKEN.CHAR, True)

    def opcIdentifier(self, symbol):
        token_info = self.tokenLido
        token = token_info[0]
        if token == TOKEN.abreColchete:
            if not symbol.is_array: raise Exception(
                f"Erro Semântico na linha {token_info[2]}: '{symbol.name}' não é um vetor e não pode ser indexado.")
            self.consome(TOKEN.abreColchete)
            tipo_indice = self.expr()
            if tipo_indice != (TOKEN.INT, False): raise Exception(
                f"Erro Semântico na linha {token_info[2]}: O índice de um vetor deve ser um inteiro.")
            self.consome(TOKEN.fechaColchete)
        elif token == TOKEN.abrePar:
            if symbol.category != 'funcao': raise Exception(
                f"Erro Semântico na linha {token_info[2]}: '{symbol.name}' não é uma função e não pode ser chamada.")
            self.consome(TOKEN.abrePar)
            self.params(symbol)
            self.consome(TOKEN.fechaPar)

    def params(self, func_symbol):
        first_expr = {TOKEN.NOT, TOKEN.mais, TOKEN.menos, TOKEN.abrePar, TOKEN.valorInt, TOKEN.valorFloat,
                      TOKEN.valorChar, TOKEN.valorString, TOKEN.ident}
        args_passados = []
        if self.tokenLido[0] in first_expr:
            tipo_arg = self.expr()
            args_passados.append(tipo_arg)
            self.restoParams(args_passados)

    def restoParams(self, args_passados):
        if self.tokenLido[0] == TOKEN.virg:
            self.consome(TOKEN.virg)
            tipo_arg = self.expr()
            args_passados.append(tipo_arg)
            self.restoParams(args_passados)


if __name__ == '__main__':
    sintatico = Sintatico("ExemploPutGet.txt")
    sintatico.traduz()