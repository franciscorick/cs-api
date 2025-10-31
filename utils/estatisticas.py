class Estatisticas:
    def __init__(self, nome, abates, mortes, assistencias, dano, data, dinheiro, id=None):
        self.id = id
        self.nome = nome
        self.abates = abates
        self.mortes = mortes
        self.assistencias = assistencias
        self.dano = dano
        self.data = data
        self.dinheiro = dinheiro

    def calcular_kd(self):
        """Calcula a razão K/D (abates/mortes)"""
        return self.abates / self.mortes

    def to_dict(self):
        """Converte o objeto Estatisticas para um dicionário"""
        resultado = {
            "nome": self.nome,
            "abates": self.abates,
            "mortes": self.mortes,
            "assistencias": self.assistencias,
            "dano": self.dano,
            "data": self.data,
            "dinheiro": self.dinheiro,
            "kd": self.calcular_kd()
        }
        if self.id is not None:
            resultado["id"] = self.id
        return resultado
