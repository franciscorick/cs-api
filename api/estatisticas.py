class Estatisticas:
    def __init__(self, nome, abates, mortes, assistencias, dano, data, dinheiro):
        self.nome = nome
        self.abates = abates
        self.mortes = mortes
        self.assistencias = assistencias
        self.dano = dano
        self.data = data
        self.dinheiro = dinheiro

    def calcular_kd(self):
        return self.abates / self.mortes
