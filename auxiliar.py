# ---------------------------------------------------
# Tradutor para a linguagem CALC - Lexico2
#
# versao 1b (out-2024)
# ---------------------------------------------------
from ttoken import TOKEN


class Lexico:

    def __init__(self, arqFonte):
        self.arqFonte = arqFonte  # objeto file
        self.fonte = self.arqFonte.read()  # string contendo file
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.tokenLido = None  # (token, lexema, linha, coluna)
        self.linha = 1  # linha atual no fonte
        self.coluna = 0  # coluna atual no fonte

    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getchar(self):
        if self.fimDoArquivo():
            return '\0'
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
        print(f'(tk={msg} lex="{lexema}" lin={linha} col={coluna})')

    def getToken(self):
        estado = 1
        simbolo = self.getchar()
        lexema = ''

        # Ignora espaços, tabs, novas linhas, e comentários
        while simbolo in ['#', ' ', '\t', '\n']:
            if simbolo == '#':
                # Ignora o comentário até o fim da linha ou fim do arquivo
                while self.getchar() not in {'\n', '\0'}:
                    pass
                simbolo = self.getchar()  # Avança para o próximo símbolo após o comentário

            # Continua ignorando espaços em branco e tabs
            while simbolo in [' ', '\t', '\n']:
                simbolo = self.getchar()
        lin = self.linha
        col = self.coluna
        while (True):
            if estado == 1:
                if simbolo.isalpha() or simbolo == "_":
                    estado = 2
                elif simbolo.isdigit():
                    estado = 3
                elif simbolo == '"':
                    estado = 4
                elif simbolo == "(":
                    return (TOKEN.abrePar, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.fechaPar, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.virg, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.ptoVirg, ";", lin, col)
                elif simbolo == "+":
                    return (TOKEN.mais, "+", lin, col)
                elif simbolo == "-":
                    return (TOKEN.)
                elif simbolo == "*":
                    return (TOKEN.multiplica, "*", lin, col)
                elif simbolo == "%":
                    return (TOKEN.mod, "%", lin, col)
                elif simbolo == "/":
                    return (TOKEN.divide, "/", lin, col)
                elif simbolo == "{":
                    return (TOKEN.abreChave, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.fechaChave, "}", lin, col)
                elif simbolo == "[":
                    return (TOKEN.abreCol, "[", lin, col)
                elif simbolo == "]":
                    return (TOKEN.fechaCol, "]", lin, col)
                elif simbolo == ":":
                    return (TOKEN.doisPts, ":", lin, col)
                elif simbolo == "<":
                    estado = 5
                elif simbolo == ">":
                    estado = 6
                elif simbolo == "=":
                    estado = 7
                elif simbolo == "!":
                    estado = 8
                elif simbolo == '\0':
                    return (TOKEN.eof, '<eof>', lin, col)
                else:
                    lexema += simbolo
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 2:
                if simbolo.isalnum() or simbolo == "_":
                    estado = 2
                else:
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema.lower())
                    return (token, lexema, lin, col)

            elif estado == 3:
                if simbolo.isdigit():
                    estado = 3
                elif simbolo == '.':
                    estado = 31
                elif simbolo == 'e':
                    estado = 3
                else:
                    self.ungetchar(simbolo)

                    return (TOKEN.intVal, lexema, lin, col)

            elif estado == 31:
                if simbolo.isdigit():
                    estado = 32
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            elif estado == 32:
                if simbolo.isdigit():
                    estado = 32
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.floatVal, lexema, lin, col)

            elif estado == 4:
                while True:
                    if simbolo == '"':
                        lexema += simbolo
                        return (TOKEN.strVal, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        return (TOKEN.erro, lexema, lin, col)
                    if simbolo == '\\':
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            return (TOKEN.erro, lexema, lin, col)
                    lexema = lexema + simbolo
                    simbolo = self.getchar()

            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.menorIgual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.menor, lexema, lin, col)

            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.maiorIgual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.maior, lexema, lin, col)

            elif estado == 7:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.igual, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.atrib, lexema, lin, col)

            elif estado == 8:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.diferente, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.erro, lexema, lin, col)

            else:
                print('BUG!!!')

            lexema = lexema + simbolo
            simbolo = self.getchar()


# inicia a traducao
if __name__ == '__main__':
    print("Para testar, chame o Tradutor no main.py")