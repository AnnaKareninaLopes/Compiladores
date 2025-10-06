#---------------------------------------------------
# Tradutor para a linguagem Mini-C
#
# versao 1a (set-2025)
#---------------------------------------------------

from enum import IntEnum
class TOKEN(IntEnum):
    erro = 1
    eof = 2
    ident = 3
    INT = 4
    FLOAT = 5
    CHAR = 6
    valorInt = 7
    valorFloat = 8
    valorChar = 9
    valorString = 10
    IF = 11
    ELSE = 12
    FOR = 13
    WHILE = 14
    abrePar = 15
    fechaPar = 16
    virg = 17
    ptoVirg = 18
    atrib = 19
    igual = 20
    diferente = 21
    menor = 22
    menorIgual = 23
    maior = 24
    maiorIgual = 25
    AND = 26
    OR = 27
    NOT = 28
    mais = 29
    menos = 30
    multiplica = 31
    divide = 32
    resto = 33
    abreChave = 34
    fechaChave = 35
    abreColchete = 36
    fechaColchete = 37
    BREAK = 38
    CONTINUE = 39
    RETURN = 40
    FUNCTION = 41

    @classmethod
    def msg(cls, token):
        nomes = {
            1:'erro',
            2:'<eof>',
            3:'ident',
            4:'int',
            5:'float',
            6:'char',
            7:'valorInt',
            8:'valorFloat',
            9:'valorChar',
            10:'valorString',
            11:'if',
            12:'else',
            13:'for',
            14:'while',
            15:'(',
            16:')',
            17:',',
            18:';',
            19:'=',
            20:'==',
            21:'!=',
            22:'<',
            23:'<=',
            24:'>',
            25:'>=',
            26:'&&',
            27:'||',
            28:'!',
            29:'+',
            30:'-',
            31:'*',
            32:'/',
            33:'%',
            34:'{',
            35:'}',
            36:'[',
            37:']',
            38:'break',
            39:'continue',
            40:'return',
            41:'function',
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'if': TOKEN.IF,
            'else': TOKEN.ELSE,
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'char': TOKEN.CHAR,
            'for': TOKEN.FOR,
            'while': TOKEN.WHILE,
            'break': TOKEN.BREAK,
            'continue': TOKEN.CONTINUE,
            'return': TOKEN.RETURN,
            'funcion': TOKEN.FUNCTION,
        }
        if lexema in reservadas:
            return reservadas[lexema]
        else:
            return TOKEN.ident
