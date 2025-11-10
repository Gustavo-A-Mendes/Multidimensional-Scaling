from mds import MDS
import numpy as np

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from capitais_aereo import capitais
from distancias_aereo import distancias

C = np.array(capitais)

nova_dim = 2
tipo = "precomputed"

teste_mds = MDS(n_components=nova_dim, dissimilarity=tipo)

_, _, X = teste_mds.compute(distancias)

# Plota os dados MDS transformados
df_mds = pd.DataFrame(X, columns=["Dim1", "Dim2"])
# df_mds['species'] = ['A', 'B']

plt.figure(figsize=(6, 6))
sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', s=100)
plt.title("Dados após MDS Manual (4D → 2D)")
plt.xlabel("Dimensão 1")
plt.ylabel("Dimensão 2")

plt.tight_layout()
plt.show()