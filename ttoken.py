#---------------------------------------------------
# Tradutor para a linguagem TOY
#
# versao 1a (set-2025)
#---------------------------------------------------

from enum import IntEnum
class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    num = 4
    string = 5
    IF = 6
    ELSE = 7
    INICIO = 8
    FIM = 9
    PROG = 10
    abrePar = 11
    fechaPar = 12
    virg = 13
    ptoVirg = 14
    pto = 15
    atrib = 16
    igual = 17
    diferente = 18
    menor = 19
    menorIgual = 20
    maior = 21
    maiorIgual = 22
    AND = 23
    OR = 24
    NOT = 25
    mais = 26
    menos = 27
    multiplica = 28
    divide = 29
    resto = 30
    LEIA = 31
    ESCREVA = 32
    abreChave = 33
    fechaChave = 34

    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'num',
            5:'string',
            6:'if',
            7:'else',
            8:'inicio',
            9:'fim',
            10:'Prog',
            11:'(',
            12:')',
            13:',',
            14:';',
            15:'.',
            16:'=',
            17:'==',
            18:'!=',
            19:'<',
            20:'<=',
            21:'>',
            22:'>=',
            23:'and',
            24:'or',
            25:'not',
            26:'+',
            27:'-',
            28:'*',
            29:'/',
            30:'%',
            31:'leia',
            32:'escreva',
            33:'{',
            34:'}',
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'program': TOKEN.PROG,
            'if': TOKEN.IF,
            'inicio': TOKEN.INICIO,
            'fim': TOKEN.FIM,
            'else': TOKEN.ELSE,
            'leia': TOKEN.LEIA,
            'escreva': TOKEN.ESCREVA,
            'and': TOKEN.AND,
            'or': TOKEN.OR,
            'not': TOKEN.NOT,
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident
