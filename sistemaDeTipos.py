from ttokenC import TOKEN

# ---------------------------------------------------------------- #
# Parte 1: Definição de Símbolos e a Tabela que os armazena
# ---------------------------------------------------------------- #

""" 'ficha de cadastro' que guarda todos os detalhes (nome, tipo, categoria)
 de uma única variável ou função. """
class Symbol:
    def __init__(self, name, category, sym_type, is_array=False, params=None):
        self.name = name # Nome do identificador
        self.category = category # Natureza do símbolo, variável ou função
        self.sym_type = sym_type # Tipo do dado (TOKEN.INT, etc) ou retorno, se for função
        self.is_array = is_array # Booleano, se é vetor ou não
        self.params = params if params is not None else [] # Lista de parâmetros, se for função

    def __str__(self):
        # Este metodo define o que será impresso ao usar print(objeto_symbol).

        # Se o símbolo for uma função...
        if self.category == 'funcao':
            # ...cria uma string formatada mostrando o tipo de retorno e o número de parâmetros.
            return f"Symbol(Name: {self.name}, Category: {self.category}, ReturnType: {TOKEN.msg(self.sym_type)}, Params: {len(self.params)})"
        else:
            # ...para qualquer outro caso (como 'variavel'), cria uma string mostrando o tipo e se é um vetor.
            return f"Symbol(Name: {self.name}, Category: {self.category}, Type: {TOKEN.msg(self.sym_type)}, IsArray: {self.is_array})"

""" 'fichário inteligente' que organiza todas as fichas (Symbol) em uma pilha de pastas
 que representam os escopos. """
class SymbolTable:
    def __init__(self):
        self.scope_stack = [{}] # Escopo global

    def enter_scope(self):
        self.scope_stack.append({}) # Entra em uma função ou bloco {} - topo da pilha
        # print(">> Entrou em um novo escopo.")

    def leave_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop() # Sai de uma função ou bloco {}
            # print("<< Saiu do escopo.")

    """ 'Cadastra' uma nova ficha (Symbol) na pasta que está no topo da pilha (o escopo atual),
     após verificar se já não existe uma com o mesmo nome. """
    def add(self, symbol):
        current_scope = self.scope_stack[-1]
        if symbol.name in current_scope:
            return False, f"Identificador '{symbol.name}' já declarado neste escopo."
        current_scope[symbol.name] = symbol
        return True, ""

    """ Procura por uma ficha (Symbol) em todas as pastas (escopos) da pilha,"""
    def lookup(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None


# ---------------------------------------------------------------- #
# Parte 2: Regras de Tipo C-Style
# ---------------------------------------------------------------- #

# --- REGRAS PARA OPERAÇÕES BINÁRIAS (a + b) ---
regras_operacoes_binarias = {
    # --- Operações Aritméticas ---
    # As regras com char refletem a "Promoção Inteira" para int.
    # O tipo mais forte (float > int) prevalece no resultado.

    # '+' (Soma)
    frozenset({(TOKEN.INT, False), TOKEN.mais, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.INT, False), TOKEN.mais, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.mais, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    # char+char -> int+int -> int
    frozenset({(TOKEN.INT, False), TOKEN.mais, (TOKEN.CHAR, False)}): (TOKEN.INT, False),  # int+char -> int+int -> int
    frozenset({(TOKEN.FLOAT, False), TOKEN.mais, (TOKEN.CHAR, False)}): (TOKEN.FLOAT, False),
    # float+char -> float+int -> float

    # '-' (Subtração) - mesmas regras da soma
    frozenset({(TOKEN.INT, False), TOKEN.menos, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menos, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.menos, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menos, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menos, (TOKEN.CHAR, False)}): (TOKEN.FLOAT, False),

    # '*' (Multiplicação) - mesmas regras da soma
    frozenset({(TOKEN.INT, False), TOKEN.multiplica, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.INT, False), TOKEN.multiplica, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.multiplica, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.multiplica, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.multiplica, (TOKEN.CHAR, False)}): (TOKEN.FLOAT, False),

    # '/' (Divisão)
    frozenset({(TOKEN.INT, False), TOKEN.divide, (TOKEN.INT, False)}): (TOKEN.INT, False),
    # Divisão de inteiros em C resulta em inteiro
    frozenset({(TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.INT, False), TOKEN.divide, (TOKEN.FLOAT, False)}): (TOKEN.FLOAT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.divide, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.divide, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.divide, (TOKEN.CHAR, False)}): (TOKEN.FLOAT, False),

    # '%' (Resto) - Definido apenas entre tipos inteiros (int, char)
    frozenset({(TOKEN.INT, False), TOKEN.resto, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.resto, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    # char%char -> int%int -> int
    frozenset({(TOKEN.INT, False), TOKEN.resto, (TOKEN.CHAR, False)}): (TOKEN.INT, False),  # int%char -> int%int -> int

    # --- Operações Relacionais (resultado é sempre booleano -> int) ---
    # Todos os tipos numéricos (int, float, char) podem ser comparados entre si.

    # '==' (Igualdade)
    frozenset({(TOKEN.INT, False), TOKEN.igual, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.igual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.igual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.igual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.igual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.igual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # '!=' (Diferente)
    frozenset({(TOKEN.INT, False), TOKEN.diferente, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.diferente, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.diferente, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.diferente, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.diferente, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.diferente, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # '<' (Menor que)
    frozenset({(TOKEN.INT, False), TOKEN.menor, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menor, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.menor, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menor, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menor, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menor, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # '<=' (Menor ou Igual)
    frozenset({(TOKEN.INT, False), TOKEN.menorIgual, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menorIgual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.menorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menorIgual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.menorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.menorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # '>' (Maior que)
    frozenset({(TOKEN.INT, False), TOKEN.maior, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.maior, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.maior, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.maior, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.maior, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.maior, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # '>=' (Maior ou Igual)
    frozenset({(TOKEN.INT, False), TOKEN.maiorIgual, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.maiorIgual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.maiorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.maiorIgual, (TOKEN.FLOAT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.maiorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.FLOAT, False), TOKEN.maiorIgual, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # --- Operações Lógicas (operam sobre booleanos -> int. Chars são promovidos para int) ---
    frozenset({(TOKEN.INT, False), TOKEN.AND, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.AND, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    # char && int -> int && int -> int
    frozenset({(TOKEN.CHAR, False), TOKEN.AND, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    # char && char -> int && int -> int

    frozenset({(TOKEN.INT, False), TOKEN.OR, (TOKEN.INT, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.INT, False), TOKEN.OR, (TOKEN.CHAR, False)}): (TOKEN.INT, False),
    frozenset({(TOKEN.CHAR, False), TOKEN.OR, (TOKEN.CHAR, False)}): (TOKEN.INT, False),

    # --- Concatenação (não faz parte do C, mas mantendo a regra para literais de string) ---
    frozenset({(TOKEN.CHAR, True), TOKEN.mais, (TOKEN.CHAR, True)}): (TOKEN.CHAR, True),
}

# --- REGRAS PARA OPERAÇÕES UNÁRIAS (!a, -a) ---
regras_operacoes_unarias = {
    # Negação Aritmética
    (TOKEN.menos, (TOKEN.INT, False)): (TOKEN.INT, False),
    (TOKEN.menos, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
    (TOKEN.menos, (TOKEN.CHAR, False)): (TOKEN.INT, False),  # -char -> -int -> int

    # Unário Mais
    (TOKEN.mais, (TOKEN.INT, False)): (TOKEN.INT, False),
    (TOKEN.mais, (TOKEN.FLOAT, False)): (TOKEN.FLOAT, False),
    (TOKEN.mais, (TOKEN.CHAR, False)): (TOKEN.INT, False),  # +char -> +int -> int

    # Negação Lógica (NOT)
    (TOKEN.NOT, (TOKEN.INT, False)): (TOKEN.INT, False),
    (TOKEN.NOT, (TOKEN.CHAR, False)): (TOKEN.INT, False),  # !char -> !int -> int
}


# ---------------------------------------------------------------- #
# Parte 3: Funções Auxiliares para o Parser
# ---------------------------------------------------------------- #

def checar_op_binaria(tipo_comp1, op, tipo_comp2):
    """Verifica operações binárias (a + b)."""
    chave = frozenset({tipo_comp1, op, tipo_comp2})
    # frozenset não se importa com a ordem dos operandos, então precisa testar as duas ordens
    return regras_operacoes_binarias.get(chave, None)


def checar_op_unaria(op, tipo_comp):
    """Verifica operações unárias (-a, !a)."""
    chave = (op, tipo_comp)
    return regras_operacoes_unarias.get(chave, None)


def checar_atribuicao(tipo_variavel, tipo_expressao):
    """
    Verifica se um tipo pode ser atribuído a uma variável.
    Ex: int x = ...; float y = ...;
    - tipo_variavel: (TOKEN.INT, False)
    - tipo_expressao: (TOKEN.FLOAT, False)
    """
    # Não se pode atribuir a um vetor inteiro, apenas a seus elementos
    if tipo_variavel[1]:
        return False

    # Atribuição idêntica (int=int, float=float)
    if tipo_variavel == tipo_expressao:
        return True

    # Promoção: float x = <expressão int>;
    if tipo_variavel == (TOKEN.FLOAT, False) and tipo_expressao == (TOKEN.INT, False):
        return True

    # "Demotion" (perda de precisão): int x = <expressão float>;
    # Em C isso é permitido (com warning). Aqui estou permitindo.
    if tipo_variavel == (TOKEN.INT, False) and tipo_expressao == (TOKEN.FLOAT, False):
        return True  # Decisão de design: permitir perda de dados

    # Atribuições envolvendo char (são como inteiros) - VER COM WALLACE
    if tipo_variavel[0] in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR} and tipo_expressao[0] in {TOKEN.INT, TOKEN.FLOAT,
                                                                                          TOKEN.CHAR}:
        return True

    return False