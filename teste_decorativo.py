class Pessoa:
    def __init__(self, nome):
        self._nome = nome

    @property
    def nome(self):  # parece um atributo, mas é um método
        return self._nome

p = Pessoa("Ana")
print(p.nome)   # chama o método, mas sem usar parênteses

class Carro:
    total_carros = 0

    def __init__(self, modelo):
        self.modelo = modelo
        Carro.total_carros += 1

    @classmethod
    def quantidade_carros(cls):
        return cls.total_carros

c1 = Carro("Fusca")
c2 = Carro("Gol")
print(Carro.quantidade_carros())  # 2

class Matematica:
    # @staticmethod
    def soma(a, b):
        return a + b

print(Matematica.soma(2, 3))  # 5
