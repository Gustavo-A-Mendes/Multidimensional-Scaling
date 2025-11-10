from mds import MDS
import numpy as np

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

label_names = [
    'OS', 'OM', 'T', 'F', 'CO', 'Ref', 'AS', 'VS', 'Refra'
]

distances = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 9, 0, 0, 0, 0, 0, 0, 0],
    [2, 5, 1, 0, 0, 0, 0, 0, 0],
    [2, 7, 4, 3, 0, 0, 0, 0, 0],
    [3, 8, 3, 2, 4, 0, 0, 0, 0],
    [1, 6, 2, 1, 2, 3, 0, 0, 0],
    [1, 7, 5, 1, 3, 2, 3, 0, 0],
    [3, 8, 7, 8, 5, 3, 6, 5, 0]
]

C = np.array(label_names)
Dist = np.array(distances)
nova_dim = 2
tipo = "precomputed"

teste_mds = MDS(n_components=nova_dim, dissimilarity=tipo)

D, G, X = teste_mds.compute(Dist.T)

print(D)
print(G)
print(X)

# Plota os dados MDS transformados
df_mds = pd.DataFrame(X, columns=["Dim1", "Dim2"])
df_mds['label'] = label_names


plt.figure(figsize=(6, 6))
sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', s=100)

# Adicionar labels
for i, row in df_mds.iterrows():
    plt.text(row["Dim1"]+0.1, row["Dim2"]+0.1, row["label"], fontsize=9)

plt.title("MDS dos dados de Pré-teste")
plt.xlabel("Dimensão 1") 
plt.ylabel("Dimensão 2")

plt.tight_layout()
# plt.grid(True, axis="both")
plt.grid(True, which='major', axis='both')  # apenas linhas principais
plt.show()