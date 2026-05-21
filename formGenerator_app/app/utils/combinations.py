from itertools import combinations
from math import ceil, floor


def generate_pairs(concepts):

    return list(combinations(concepts, 2))

def gerar_divisao_secao(total_pair):
    max_per_secao = 10

    num_secao = ceil(total_pair / max_per_secao)
    num_per_secao = ceil(total_pair / num_secao)

    return num_per_secao