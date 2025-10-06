# Arquivo: semantico.py

from ttokenC import TOKEN
from sistemaDeTipos import Symbol, SymbolTable, checar_op_binaria, checar_op_unaria, checar_atribuicao


class AnalisadorSemantico:
    def __init__(self):
        self.tabela_simbolos = SymbolTable()
        self.tipo_retorno_funcao_atual = None  # Guarda o tipo de retorno esperado da função corrente
        self.nivel_laco = 0  # Conta em quantos níveis de laço aninhados estamos

        self._declarar_funcoes_biblioteca()

    def _declarar_funcoes_biblioteca(self):
        # --- Funções de Inteiro ---
        putint = Symbol(name='putint', category='funcao', sym_type=TOKEN.INT)
        putint.params.append({'type': TOKEN.INT, 'is_array': False})
        self.tabela_simbolos.add(putint)

        getint = Symbol(name='getint', category='funcao', sym_type=TOKEN.INT)
        self.tabela_simbolos.add(getint)

        # --- Funções de Float ---
        putfloat = Symbol(name='putfloat', category='funcao', sym_type=TOKEN.INT)
        putfloat.params.append({'type': TOKEN.FLOAT, 'is_array': False})
        self.tabela_simbolos.add(putfloat)

        getfloat = Symbol(name='getfloat', category='funcao', sym_type=TOKEN.FLOAT)
        self.tabela_simbolos.add(getfloat)

        # --- Funções de Char ---
        putchar = Symbol(name='putchar', category='funcao', sym_type=TOKEN.INT)
        putchar.params.append({'type': TOKEN.CHAR, 'is_array': False})
        self.tabela_simbolos.add(putchar)

        getchar = Symbol(name='getchar', category='funcao', sym_type=TOKEN.CHAR)
        self.tabela_simbolos.add(getchar)

    # --- Métodos de Gerenciamento de Escopo ---

    def enter_scope(self):
        """ Inicia um novo escopo na tabela de símbolos. """
        self.tabela_simbolos.enter_scope()

    def leave_scope(self):
        """ Finaliza o escopo atual. """
        self.tabela_simbolos.leave_scope()

    # --- Métodos de Gerenciamento de Declaração ---

    def declara_funcao(self, nome, tipo_retorno, token_info):
        """ Declara uma função no escopo atual. """
        simbolo = Symbol(name=nome, category='funcao', sym_type=tipo_retorno)
        success, error = self.tabela_simbolos.add(simbolo)
        if not success:
            raise Exception(f"Erro Semântico na linha {token_info[2]}: {error}")

        # Guarda o tipo de retorno para verificações futuras do comando 'return'
        self.tipo_retorno_funcao_atual = tipo_retorno
        return simbolo

    def declara_argumento(self, nome, tipo, is_array, lista_params, token_info):
        """ Declara um argumento de função, adicionando-o à lista de parâmetros e ao escopo local. """
        lista_params.append({'type': tipo, 'is_array': is_array})
        simbolo = Symbol(name=nome, category='variavel', sym_type=tipo, is_array=is_array)
        success, error = self.tabela_simbolos.add(simbolo)
        if not success:
            raise Exception(f"Erro Semântico na linha {token_info[2]}: {error}")

    def declara_variavel(self, nome, tipo, is_array, token_info):
        """ Declara uma variável no escopo atual. """
        simbolo = Symbol(name=nome, category='variavel', sym_type=tipo, is_array=is_array)
        success, error = self.tabela_simbolos.add(simbolo)
        if not success:
            raise Exception(f"Erro Semântico na linha {token_info[2]}: {error}")

    # --- Métodos de Verificação de Uso e Contexto ---

    def verifica_identificador_declarado(self, nome, token_info):
        """ Procura por um identificador na tabela de símbolos e lança um erro se não for encontrado. """
        simbolo = self.tabela_simbolos.lookup(nome)
        if simbolo is None:
            raise Exception(f"Erro Semântico na linha {token_info[2]}: Identificador '{nome}' não declarado.")
        return simbolo

    def verifica_retorno(self, tipo_expressao, token_info):
        """ Verifica se o tipo de uma expressão de 'return' é compatível com o retorno da função. """
        if self.tipo_retorno_funcao_atual is None:
            raise Exception(f"Erro Semântico na linha {token_info[2]}: Comando 'return' encontrado fora de uma função.")

        tipo_esperado_tupla = (self.tipo_retorno_funcao_atual, False)  # Funções retornam valores, não vetores
        if not checar_atribuicao(tipo_esperado_tupla, tipo_expressao):
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Tipo de retorno incompatível. Esperado '{TOKEN.msg(self.tipo_retorno_funcao_atual)}' mas a expressão é do tipo {tipo_expressao}.")

    def entrar_laco(self):
        """ Sinaliza a entrada em um laço de repetição. """
        self.nivel_laco += 1

    def sair_laco(self):
        """ Sinaliza a saída de um laço de repetição. """
        self.nivel_laco -= 1

    def verificar_dentro_de_laco(self, token_info):
        """ Verifica se os comandos 'break' ou 'continue' estão dentro de um laço. """
        if self.nivel_laco == 0:
            comando = TOKEN.msg(token_info[0])
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Comando '{comando}' só pode ser usado dentro de um laço.")

    def validar_chamada_funcao(self, func_symbol, args_passados, token_info):
        """ Valida o número e os tipos dos argumentos em uma chamada de função. """
        params_esperados = func_symbol.params

        # 1. Verifica o número de argumentos
        if len(args_passados) != len(params_esperados):
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Número incorreto de argumentos para a função '{func_symbol.name}'. Esperado {len(params_esperados)}, mas foram passados {len(args_passados)}.")

        # 2. Verifica o tipo de cada argumento
        for i, arg_passado_tipo in enumerate(args_passados):
            param_esperado = params_esperados[i]
            tipo_esperado_tupla = (param_esperado['type'], param_esperado['is_array'])

            if not checar_atribuicao(tipo_esperado_tupla, arg_passado_tipo):
                raise Exception(
                    f"Erro Semântico na linha {token_info[2]}: Tipo incorreto para o argumento {i + 1} da função '{func_symbol.name}'. Esperado {tipo_esperado_tupla}, mas foi passado {arg_passado_tipo}.")

    # --- Métodos de Validação de Tipos de Expressão ---

    def validar_operacao_binaria(self, tipo_esq, op, tipo_dir, token_info):
        """ Delega a verificação para a função importada e formata o erro se necessário. """
        tipo_resultado = checar_op_binaria(tipo_esq, op, tipo_dir)
        if tipo_resultado is None:
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Operação '{TOKEN.msg(op)}' inválida entre os tipos {tipo_esq} e {tipo_dir}.")
        return tipo_resultado

    def validar_operacao_unaria(self, op, tipo_operando, token_info):
        """ Delega a verificação para a função importada e formata o erro se necessário. """
        tipo_resultado = checar_op_unaria(op, tipo_operando)
        if tipo_resultado is None:
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Operador unário '{TOKEN.msg(op)}' inválido para o tipo {tipo_operando}.")
        return tipo_resultado

    def validar_atribuicao(self, tipo_variavel, tipo_expressao, token_info):
        """ Delega a verificação para a função importada e formata o erro se necessário. """
        if not checar_atribuicao(tipo_variavel, tipo_expressao):
            raise Exception(
                f"Erro Semântico na linha {token_info[2]}: Atribuição incompatível. Não é possível atribuir tipo {tipo_expressao} a uma variável do tipo {tipo_variavel}.")