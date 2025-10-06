from ttoken import TOKEN
from lexico import Lexico
import traceback

class Sintatico:

    def __init__(self, nomeArquivo):
        self.lexico = Lexico(nomeArquivo)

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            self.consome(TOKEN.eof)
            print("Traduzido com sucesso!")
        except Exception as e:
            print("Falha na tradução:", e)
            traceback.print_exc()

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f"Erro na linha {linha}, coluna {coluna}: ")

            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f"Era esperado {msgTokenAtual} mas foi lido {msg}")
            raise Exception("Erro Sintático")

    def prog(self):
        self.consome(TOKEN.INICIO)
        self.coms()
        self.consome(TOKEN.FIM)
        self.consome(TOKEN.pto)

    def coms(self): # LAMBDA | Com Coms
        if self.tokenLido[0] in {TOKEN.ident, TOKEN.LEIA, TOKEN.ESCREVA, TOKEN.IF, TOKEN.abreChave}:
            self.com()
            self.coms()
        else:
            pass

    def com(self): # Ler | Escrever | If | Atrib | Bloco
        if self.tokenLido[0] == TOKEN.ident:
            self.atribuicao()
        elif self.tokenLido[0] == TOKEN.LEIA:
            self.ler()
        elif self.tokenLido[0] == TOKEN.ESCREVA:
            self.escrever()
        elif self.tokenLido[0] == TOKEN.IF:
            self.se()
        else:
            self.bloco()

    def ler(self): # leia ( string, ident ) ;
        self.consome(TOKEN.LEIA)
        self.consome(TOKEN.abrePar)
        self.consome(TOKEN.string)
        self.consome(TOKEN.virg)
        self.consome(TOKEN.ident)
        self.consome(TOKEN.fechaPar)
        self.consome(TOKEN.ptoVirg)

    def escrever(self): # escreva ( string RestoEscreva
        self.consome(TOKEN.ESCREVA)
        self.consome(TOKEN.abrePar)
        self.consome(TOKEN.string)
        self.restoEscreva()

    def restoEscreva(self): # ); | , ident );
        if(self.tokenLido[0] == TOKEN.virg):
            self.consome(TOKEN.virg)
            self.consome(TOKEN.ident)
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)
        else:
            self.consome(TOKEN.fechaPar)
            self.consome(TOKEN.ptoVirg)

    def se(self): # if ( Exp ) Com RestoIf
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abrePar)
        self.exp()
        self.consome(TOKEN.fechaPar)
        self.com()
        self.restoSe()

    def restoSe(self): # else Com | LAMBDA
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass

    def bloco(self): # { Coms }
        self.consome(TOKEN.abreChave)
        self.coms()
        self.consome(TOKEN.fechaChave)

    def atribuicao(self): # ident = Exp ;
        self.consome(TOKEN.ident)
        self.consome(TOKEN.atrib)
        self.exp()
        self.consome(TOKEN.ptoVirg)

    def exp(self): # Nao RestoExp
        self.nao()
        self.restoExp()

    def restoExp(self): # LAMBDA | and Nao RestoExp | or Nao RestoExp
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.nao()
            self.restoExp()
        elif self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.nao()
            self.restoExp()
        else:
            pass

    def nao(self): # not Nao | Rel
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.nao()
        else:
            self.rel()

    def rel(self): # Soma RestoRel
        self.soma()
        self.restoRel()

    def restoRel(self): # LAMBDA | OpRel Soma
        if self.tokenLido[0] in {TOKEN.igual, TOKEN.diferente, TOKEN.menor, TOKEN.menorIgual, TOKEN.maior, TOKEN.maiorIgual}:
            self.consome(self.tokenLido[0])
            self.soma()
        else:
            pass

    def soma(self): # Mult RestoSoma
        self.mult()
        self.restoSoma()

    def restoSoma(self): # LAMBDA | + Mult RestoSoma | - Mult RestoSoma
        if self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.mult()
            self.restoSoma()
        elif self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.mult()
            self.restoSoma()
        else:
            pass

    def mult(self): # Uno RestoMult
        self.uno()
        self.restoMult()

    def restoMult(self): # LAMBDA | * Uno RestoMult | / Uno RestoMult | % Uno RestoMult
        if self.tokenLido[0] == TOKEN.multiplica:
            self.consome(TOKEN.multiplica)
            self.uno()
            self.restoMult()
        elif self.tokenLido[0] == TOKEN.divide:
            self.consome(TOKEN.divide)
            self.uno()
            self.restoMult()
        elif self.tokenLido[0] == TOKEN.resto:
            self.consome(TOKEN.resto)
            self.uno()
            self.restoMult()
        else:
            pass

    def uno(self): # - Uno | + Uno | folha
        if self.tokenLido[0] == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.uno()
        elif self.tokenLido[0] == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.uno()
        else:
            self.folha()

    def folha(self): # ( Exp ) | ident | num
        if self.tokenLido[0] == TOKEN.abrePar:
            self.consome(TOKEN.abrePar)
            self.exp()
            self.consome(TOKEN.fechaPar)
        elif self.tokenLido[0] == TOKEN.ident:
            self.consome(TOKEN.ident)
        elif self.tokenLido[0] == TOKEN.num:
            self.consome(TOKEN.num)
        else:
            raise Exception(f"Erro Sintático: token inesperado {self.tokenLido}")

if __name__ == '__main__':
    sintatico = Sintatico("Toy-sample.txt")
    sintatico.traduz()