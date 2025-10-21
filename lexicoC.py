from ttokenC import TOKEN

class Lexico:
    def __init__(self, nomeArquivo):
        with open(nomeArquivo, "r", encoding="utf-8") as f:
            self.fonte = f.read()
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.tokenLido = None # Tupla (token, lexema, linha, coluna)
        self.linha = 1
        self.coluna = 0

    def fimArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getchar(self):
        if self.fimArquivo():
            return '\0' # Caracter nulo
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1

        return car

    def ungetchar(self, simbolo):
        if simbolo == '\n':
            self.linha -= 1
        if self.indiceFonte > 0:
            self.indiceFonte -= 1
        self.coluna -= 1

    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)
        print(f'(tk={msg} lex="{lexema}" linha={linha} coluna={coluna})')

    # Ignora espaços, tabs, novas linhas, e comentários
    def descartaBrancosEComentarios(self, simbolo):
        while True:
            # 1. Descarta espaços em branco e quebras de linha
            if simbolo in [' ', '\t', '\n']:
                simbolo = self.getchar()
                continue  # Volta para o início do laço com o novo caractere

            # 2. Verifica se pode ser um comentário
            if simbolo == '/':
                proximo_char = self.getchar()
                if proximo_char == '/':
                    while simbolo not in {'\n', '\0'}:
                        simbolo = self.getchar()
                    continue
                else:
                    # Não, não era um comentário. Era um operador de divisão.
                    self.ungetchar(proximo_char)
                    break

            break

        return simbolo

    def _consumirErro(self, lexema_inicial, simbolo_inicial, linha, coluna):

        lexema = lexema_inicial
        simbolo = simbolo_inicial

        # Caracteres que finalizam um token (delimitadores)
        delimitadores = " \t\n"

        while simbolo not in delimitadores:
            lexema += simbolo
            simbolo = self.getchar()

        # Devolve o delimitador para ser processado na próxima chamada a getToken
        if simbolo != '\0':
            self.ungetchar(simbolo)

        return (TOKEN.erro, lexema, linha, coluna)

    def getToken(self):
        estado = 1
        simbolo = self.getchar()
        lexema = ''
        # Linha e coluna são "globais" e atributos do objeto

        simbolo = self.descartaBrancosEComentarios(simbolo);

        # Começa a pegar um token
        lin = self.linha
        col = self.coluna
        while (True):
            if estado == 1: # Decide o tipo de Token
                if simbolo.isalpha():
                    estado = 2 # identificador ou palavra reservada
                elif simbolo.isdigit():
                    estado = 3 # números
                elif simbolo == '"':
                    estado = 4 # cadeia de caracteres
                elif simbolo == "'":
                    estado = 10 # caractere
                elif simbolo == "(":
                    return (TOKEN.abrePar, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.fechaPar, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.virg, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.ptoVirg, ";", lin, col)
                elif simbolo == ".":
                    estado = 9 # Pode ser ponto ou número decimal
                elif simbolo == "=":
                    estado = 5 # Atribuição ou igual
                elif simbolo == "!":
                    estado = 6 # Diferente ou Not
                elif simbolo == "<":
                    estado = 7 # Menor ou menor igual
                elif simbolo == ">":
                    estado = 8 # Maior ou maior igual
                elif simbolo == "+":
                    return (TOKEN.mais, "+", lin, col)
                elif simbolo == "-":
                    return (TOKEN.menos, "-", lin, col)
                elif simbolo == "*":
                    return (TOKEN.multiplica, "*", lin, col)
                elif simbolo == "/":
                    return (TOKEN.divide, "/", lin, col)
                elif simbolo == "%":
                    return (TOKEN.resto, "%", lin, col)
                elif simbolo == "{":
                    return (TOKEN.abreChave, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.fechaChave, "}", lin, col)
                elif simbolo == "[":
                    return (TOKEN.abreColchete, "[", lin, col)
                elif simbolo == "]":
                    return (TOKEN.fechaColchete, "]", lin, col)
                elif simbolo == "&": # AND
                    estado = 11
                elif simbolo == "|": # OR
                    estado = 12
                elif simbolo == '\0':
                    return (TOKEN.eof, "EOF", lin, col)
                else:
                    lexema += simbolo
                    simbolo = self.getchar()
                    return self._consumirErro(lexema, simbolo, lin, col)

            elif estado == 2:
                # Aceita letras e dígitos no meio da palavra
                if simbolo.isalnum():
                    estado = 2
                # Se tiver _ no meio da palavra aceita
                elif simbolo == "_" and len(lexema) > 0:
                    estado = 2
                # Se terminou a palavra, ou seja, pegou um símbolo a mais, devolve ele
                else:
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema.lower())
                    return (token, lexema, lin, col)

            elif estado == 3: # Números
                if simbolo.isdigit():
                    estado = 3
                elif simbolo == ".":
                    estado = 31
                elif simbolo.isalpha():
                    lexema += simbolo
                    simbolo = self.getchar()
                    return self._consumirErro(lexema, simbolo, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.valorInt, lexema, lin, col)

            elif estado == 31:
                if simbolo.isdigit():
                    estado = 32
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 32: # Float
                if simbolo.isdigit():
                    estado = 32
                elif simbolo.isalpha():
                    lexema += simbolo
                    simbolo = self.getchar()
                    return self._consumirErro(lexema, simbolo, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.valorFloat, lexema, lin, col)

            elif estado == 4:
                while (True):
                    if simbolo == '"':
                        lexema += simbolo
                        return (TOKEN.valorString, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        return (TOKEN.erro, lexema, lin, col)
                    if simbolo == '\\':
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            return (TOKEN.erro, lexema, lin, col)
                    lexema += simbolo
                    simbolo = self.getchar()

            elif estado == 5: # Atribuição ou igual
                if simbolo == "=":
                    lexema += simbolo
                    return (TOKEN.igual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.atrib, lexema, lin, col)

            elif estado == 6:
                lexema += simbolo
                simbolo = self.getchar()
                if simbolo == "=":
                    lexema += simbolo
                    return (TOKEN.diferente, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.NOT, lexema, lin, col)

            elif estado == 7: # Menor ou menor igual
                if simbolo == "=":
                    lexema += simbolo
                    return (TOKEN.menorIgual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.menor, lexema, lin, col)

            elif estado == 8: # Maior ou maior igual
                if simbolo == "=":
                    lexema += simbolo
                    return (TOKEN.maiorIgual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.maior, lexema, lin, col)

            elif estado == 9:  # Verificação após o ponto inicial (Req 1 e Req 2)
                if simbolo.isdigit():
                    # REQ 1: Tratar .123 como erro.
                    lexema += simbolo  # Adiciona o dígito para o relatório de erro
                    simbolo = self.getchar()
                    return self._consumirErro(lexema, simbolo, lin, col)

            elif estado == 10:
                if simbolo != '\'' and simbolo not in ['\n', '\r']:
                    lexema += simbolo
                    simbolo = self.getchar()
                    if simbolo == '\'':  # fecha corretamente
                        lexema += simbolo
                        return (TOKEN.valorChar, lexema, lin, col)
                    else:
                        lexema += simbolo
                        simbolo = self.getchar()
                        return self._consumirErro(lexema, simbolo, lin, col)
                else:
                    lexema += simbolo
                    simbolo = self.getchar()
                    return self._consumirErro(lexema, simbolo, lin, col)

            elif estado == 11: # AND
                if simbolo == "&":
                    lexema += simbolo
                    return (TOKEN.AND, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 12: # OR
                if simbolo == "|":
                    lexema += simbolo
                    return (TOKEN.OR, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            else:
                print('BUG!!!')
                return (TOKEN.erro, lexema, lin, col)

            lexema = lexema + simbolo
            simbolo = self.getchar()


if __name__ == '__main__':
    lexico = Lexico("ExemploWalace_20-10-25.txt")
    token = lexico.getToken()
    while (token[0] != TOKEN.eof):
        lexico.imprimeToken(token)
        token = lexico.getToken()

