import seaborn as sns
import pandas as pd
from sklearn.datasets import load_iris

import numpy as np
import matplotlib.pyplot as plt

def classical_mds(D, n_components=2):
    """
    Executa o MDS clássico com base na matriz de distâncias D (NxN).
    Retorna os pontos em n_components dimensões.
    """
    n = D.shape[0]

    print(n)

    # 1. Distância ao quadrado
    D_squared = D ** 2

    # 2. Duplo centramento: B = -0.5 * J * D^2 * J
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ D_squared @ J

    # 3. Autovalores e autovetores
    eigvals, eigvecs = np.linalg.eigh(B)

    # 4. Ordena em ordem decrescente
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # 5. Seleciona os n_components principais
    L = np.diag(np.sqrt(eigvals[:n_components]))
    V = eigvecs[:, :n_components]

    # 6. Nova representação dos pontos
    X_new = V @ L
    return X_new

# ===== Exemplo com dados =====
# Pontos em 2D (originalmente)
# X = np.array([
#     [0, 0],
#     [1, 0],
#     [0, 1],
#     [1, 1]
# ])

iris = load_iris()
X = iris.data
labels = iris.target
label_names = iris.target_names

# Calcula matriz de distâncias euclidianas
from math import dist
n = X.shape[0]

D = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        if i == j:
            D[i, j] = 0
            continue

        D[i, j] = pow(dist(X[i], X[j]), 2)

# Aplica MDS clássico
X_mds = classical_mds(D, n_components=2)

# Plot resultado
sns.scatterplot(data=X_mds, x='Dim1', y='Dim2', hue='species')
plt.title("Dados após MDS (4D → 2D)")
plt.xlabel("Dimensão 1")
plt.ylabel("Dimensão 2")
plt.legend()
plt.tight_layout()
plt.show()
