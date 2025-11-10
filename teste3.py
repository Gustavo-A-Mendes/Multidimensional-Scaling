from mds import MDS
import numpy as np

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

nova_dim = 2
tipo = "euclidean"

teste_mds = MDS(n_components=nova_dim, dissimilarity=tipo)

A = [
        [2, 3, 4],
        [1, 2, 2],
        [0, 0, 1],
        [1, 3, 4]
]

B = [
        [0, 2, 3, 4],
        [0, 0, 2, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
]

distancia, G, X = teste_mds.compute(A)

print(distancia)
print(G)
print(X)


# Carrega os dados

# Plota os dados MDS transformados
df_mds = pd.DataFrame(X, columns=["Dim1", "Dim2"])
# df_mds['species'] = ['A', 'B']

plt.figure(figsize=(6, 6))
sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', s=100)
plt.title("Dados após MDS Manual (4D → 2D)")
plt.xlabel("Dimensão 1")
plt.ylabel("Dimensão 2")
# plt.xlim(-1500, 2500)
# plt.ylim(-1500, 2000)
# plt.legend()
# Plota os dados MDS transformados
# Plotagem 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Separar colunas em x, y, z
x = np.array(A)[:, 0]
y = np.array(A)[:, 1]
z = np.array(A)[:, 2]

ax.scatter(x, y, z, c='r', marker='o', s=50)

# Eixos e título
ax.set_title('MDS em 3D')
ax.set_xlabel('Dim 1')
ax.set_ylabel('Dim 2')
ax.set_zlabel('Dim 3')

plt.tight_layout()
plt.show()