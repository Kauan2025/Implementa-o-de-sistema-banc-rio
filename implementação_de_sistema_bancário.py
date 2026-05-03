from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, date
from textwrap import dedent

class Transação(ABC):
    @property
    @abstractproperty 
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transação):
    def __init__(self, valor:float):
        self._valor = valor
        self._data = datetime.now()

    @property
    def valor(self):
        return self._valor

    @property
    def data(self):
        return self._data

    def registrar(self, conta):
        sucesso = conta.depositar(self._valor)
        if sucesso:
            conta.historico.adicionar_transação(self)

class Saque(Transação):
    def __init__(self, valor):
        self._valor = valor
        self._data = datetime.now()

    @property
    def valor(self):
        return self._valor

    @property
    def data(self):
        return self._data

    def registrar(self, conta):
        sucesso = conta.sacar(self._valor)
        if sucesso:
            conta.historico.adicionar_transação(self)

class Historico:
    def __init__(self):
        self._transações = []

    @property
    def transações(self):
        return self._transações
    
    def adicionar_transação(self, transação:Transação):
        self._transações.append(transação)

    def extrato(self):
        print(f'\n{20* '='} EXTRATO {20* '='}\n')
        if not self._transações:
            print('Sem movimentações bancárias')
        else:
            for transação in self._transações:
                tipo = transação.__class__.__name__
                data_formatada = transação.data.strftime('%d/%m/%Y %H:%M:%S')
                print(f'{data_formatada}\t{tipo} : R${transação.valor:.2f}\n')
        print(f'{49*'='}')

class Conta:
    def __init__(self, numero:int, agencia:str, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, cliente, numero:int):
        return cls(cliente, numero)
    
    def sacar(self, valor:float):
        if valor > self._saldo:
            print('\nSaque falhou! Tente Novamente\n')
            return False
        elif valor > 0:
            self._saldo -= valor
            print('\n====== Saque concluído! ======\n')
            return True
    
    def depositar(self, valor:float):
        if valor > 0:
            self._saldo += valor
            print('\n====== Depósito concluído! ======\n')
            return True
        else:
            print('\nDepósito falhou! Tente Novamente\n')
            return False

class ContaCorrente(Conta):
    def __init__(self, numero:int, agencia:str, cliente, limite:float, limite_saques:int):
        super().__init__(numero, agencia, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor:float):
        q_saques = len([t for t in self._historico.transações if isinstance(t, Saque)])
        if valor > self._limite:
            print('\nSaque falhou, limite excedido!')
        elif q_saques >= self._limite_saques:
            print('\nSaque falhou, limite de saques excedido!')
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        pass

class Cliente:
    def __init__(self, endereço:str):
        self._endereço = endereço
        self._contas = []

    def realizar_transação(self, conta:Conta, transação:Transação):
        transação.registrar(conta)

    def adicionar_conta(self, conta:Conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf:str, nome:str, data_nascimento:date, endereço = str):
        super().__init__(endereço)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

def menu():
    menu = """\
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [0]\tSair
    => """
    return int(input(dedent(menu)))


def filtrar_clientes(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_cliente(cliente):
    if not cliente.contas:
        print('====== Cliente sem contas! ======')
        return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Informe seu CPF: ')
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print('====== Cliente não encontrado ======')
        return
    
    valor = float(input('Valor do depósito: '))
    transação = Deposito(valor)

    conta = recuperar_cliente(cliente)
    cliente.realizar_transação(conta = conta, transação = transação)


def sacar(clientes):
    cpf = input('Informe seu CPF: ')
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print('====== Cliente não encontrado ======')
        return
    
    valor = float(input('Valor do Saque: '))
    transação = Saque(valor)

    conta = recuperar_cliente(cliente)
    cliente.realizar_transação(conta = conta, transação = transação)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("====== Cliente não encontrado! ======")
        return

    conta = recuperar_cliente(cliente)
    if not conta:
        return
    
    conta.historico.extrato()

def nova_conta(numero_conta, clientes, contas):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_clientes(cpf, clientes )

    if not cliente:
        print('====== Cliente não encontrado, fluxo de criação de conta encerrado! ======')
        return

    agencia = input('Informe sua agência: ')
    limite = float(input('Informe seu limite: '))
    limite_saques = int(input('Informe seu limite de saques: '))

    conta = ContaCorrente(cliente = cliente, numero = numero_conta, agencia = agencia, limite = limite, limite_saques = limite_saques)

    contas.append(conta)
    cliente._contas.append(conta)

    print('Conta criada com sucesso!')

def listar_contas(contas):
    for conta in contas:
        print(100*'=')
        print(dedent(str(conta)))


def novo_usuario(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_clientes(cpf, clientes )

    if cliente:
        print('====== Esse cliente já existe" ======')
        return
    
    nome = input('Informe seu nome: ')
    data_nascimento = input('Informe sua data de nascimento (dd-mm-aaaa)')
    endereço = input('Informe seu endereço: ')
    cliente = PessoaFisica(nome = nome, cpf = cpf, data_nascimento = data_nascimento, endereço = endereço)

    clientes.append(cliente)

    print('Cliente criado com sucesso!')

def sistema():
    contas = []
    clientes = []
    
    while True:
        opção = menu()

        if opção == 1:
            depositar(clientes)
        elif opção == 2:
            sacar(clientes)
        elif opção == 3:
            exibir_extrato(clientes)
        elif opção == 4:
            numero_conta = len(contas) + 1
            nova_conta(numero_conta, clientes, contas)
        elif opção == 5:
            listar_contas(contas)
        elif opção == 6:
            novo_usuario(clientes)
        elif opção == 0:
            print('Saindo do sistema ...')
            break
        else:
            print('====== Opção Inválida ======')


sistema()
