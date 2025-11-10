import pandas as pd
import numpy as np
import re

class Participante:
    header = None
    
    def __init__(self, df_results, group="Aluno"):
        # Armazena um cabeçalho dos conceitos comparados:
        header_temp = Participante.__get_key(df_results)

        if Participante.header is None:
            Participante.header = header_temp
        # Se o valor recebido em uma nova inicialização for diferente da existente, cancela a instância:
        elif Participante.header != header_temp:
            raise ValueError(
                f"Valores de cabeçalho incompatíveis! Esperado {Participante.header}, "
                f"mas recebido {header_temp}."
            )

        self.group = group
        self.matrix = self.__compute_results(df_results)
    
    # Métodos Privados:

    def __compute_results(self, dict_results):
        '''
            Reorganiza os dados fornecidos em uma Matrix de Dissimilaridades
        '''

        matriz_dissimilaridade = np.zeros([len(Participante.header), len(Participante.header)])

        data = list(dict_results.keys())[1:]

        for value in data:
            print(value)
            comp = re.findall(r"\((.*?)\)", value)
            print(comp)

            row = Participante.header.index(comp[0])
            col = Participante.header.index(comp[1])

            matriz_dissimilaridade[row, col] = dict_results[value]
        
        # retorna a matriz simetrica do resultado:
        return matriz_dissimilaridade + matriz_dissimilaridade.T - np.diag(matriz_dissimilaridade.diagonal())

    @staticmethod
    def __get_key(df_data):
        '''
            Retorna os valores chave das colunas dos DataFrame
        '''
        # header = df_results.columns

        # Conjunto dos valores comparados:
        conceitos = []

        # Recupera os parâmetros comparados, a partir do cabeçalho da tabela: 
        headers = list(df_data.keys())
        for header in headers:
            c = re.findall(r"\((.*?)\)", header)
            # print(c)

            # Adiciona os valores únicos na lista total (sem repetições):
            for value in c:
                if value not in conceitos:
                    conceitos.append(value)

        # retorna a lista:
        return conceitos


df = pd.read_csv("Teste - Respostas ao formulário 1.csv")
# print(df.head())
# print(df["(OS) Onda Sonora [(OM) Onda Mecânica]"][2])
# print(df.iloc[0].data)

df_dict = df.to_dict(orient="records")

aluno1 = Participante(df_dict[0])