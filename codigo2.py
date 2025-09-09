# Importa as bibliotecas
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from sklearn.datasets import load_iris

# Carregar o conjunto de dados Iris
iris = load_iris()
X = iris.data
labels = iris.target
label_names = iris.target_names
X

import numpy as np
from math import dist

# Gera uma matriz distância entre os dados (Distância Euclediana):
def eucledian_distance(matrix):
    n = len(matrix)
    # print(n)
    distance = np.zeros((n, n))
    # print(distance)
    for i in range(n):
        for j in range(n):
            distance[i, j] = pow(dist(matrix[i], matrix[j]), 2)

    return distance


D = eucledian_distance(X)

# Processamento dos dados

def gram_matrix(matrix):
    n = len(matrix)

    # Definir matriz de Centralização J:
    I = np.eye(n)
    ones = np.ones((n, n)) / n

    J = I - ones
    J

    # Matriz G = -(1/2)JD²J
    G = -0.5 * J @ matrix @ J

    return G

B = gram_matrix(D)

def spectral_decomposition(matrix, n_components = 2):
    # Obtem os autovalores e autovetores da matriz:
    eigvals, eigvecs = np.linalg.eigh(matrix)

    # Ordenar do maior pro menor:
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # Apenas os "n_components" maiores:
    L = np.diag(np.sqrt(eigvals[:n_components]))
    V = eigvecs[:, :n_components]

    # Coordenadas finais
    matrix_mds = V @ L

    return matrix_mds

X_mds_manual = spectral_decomposition(B)

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.manifold import MDS

# Carrega os dados
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = [iris.target_names[i] for i in iris.target]

# Pairplot dos dados brutos
sns.pairplot(df, hue='species', diag_kind='hist')
plt.suptitle("Dados Brutos - Pairplot", y=1.02)
plt.show()

# Aplica MDS (4D para 2D)
mds = MDS(n_components=2, random_state=42)
X_mds = mds.fit_transform(iris.data)

# Plota os dados MDS transformados
df_mds = pd.DataFrame(X_mds_manual, columns=["Dim1", "Dim2"])
df_mds['species'] = df['species']

plt.figure(figsize=(6, 5))
sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', hue='species')
plt.title("Dados após MDS (4D → 2D)")
plt.xlabel("Dimensão 1")
plt.ylabel("Dimensão 2")
plt.legend()
plt.tight_layout()
plt.show()

# Plota os dados MDS transformados
df_mds = pd.DataFrame(X_mds, columns=["Dim1", "Dim2"])
df_mds['species'] = df['species']

plt.figure(figsize=(6, 5))
sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', hue='species')
plt.title("Dados após MDS (4D → 2D)")
plt.xlabel("Dimensão 1")
plt.ylabel("Dimensão 2")
plt.legend()
plt.tight_layout()
plt.show()
