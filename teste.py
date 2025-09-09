import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.manifold import MDS

# Carrega os dados
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = [iris.target_names[i] for i in iris.target]

# # Pairplot dos dados brutos
# sns.pairplot(df, hue='species', diag_kind='hist')
# plt.suptitle("Dados Brutos - Pairplot", y=1.02)
# plt.show()

# Aplica MDS (4D para 2D)
mds = MDS(n_components=2, random_state=42)
X_mds = mds.fit_transform(iris.data)

# # Plota os dados MDS transformados
# df_mds = pd.DataFrame(X_mds_manual, columns=["Dim1", "Dim2"])
# df_mds['species'] = df['species']

# plt.figure(figsize=(6, 5))
# sns.scatterplot(data=df_mds, x='Dim1', y='Dim2', hue='species')
# plt.title("Dados após MDS (4D → 2D)")
# plt.xlabel("Dimensão 1")
# plt.ylabel("Dimensão 2")
# plt.legend()
# plt.tight_layout()
# plt.show()

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
