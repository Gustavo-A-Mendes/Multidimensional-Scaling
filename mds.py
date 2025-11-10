from math import sqrt, dist
import numpy as np

class MDS:
    # def __init__(self, n_components=2, metric=True, n_init=4, max_iter=300, verbose=0, eps=0.001, n_jobs=1, random_state=None, dissimilarity='euclidean'):
    def __init__(self, n_components=2, *, dissimilarity='euclidean'):
        self.n_components = n_components
        self.dissimilarity = dissimilarity
        print("Classe inicializada!")
    

    def compute(self, X, y=None, init=None):
        
        # Verifica a quantidade de dados:
        n = len(X)

        # Inicializa matriz de dissimilaridades:
        distance = np.zeros((n, n))

        # Preenche os dados, dado a opção predefinida:
        if self.dissimilarity == "euclidean":
            distance = self.__euclidian_distance(X, n)

        elif self.dissimilarity == "precomputed":
            distance = np.array(X)[:n, :n]
        
            # Utilizando apenas o triângulo superior da matriz, garante que a matriz seja simétrica:
            tri_sup = np.triu(distance)
            distance = tri_sup + tri_sup.T - np.diag(np.diag(tri_sup))
        
        # Gerando a matriz de Gram a partir das distâncias:
        B = self.__gram_matrix(distance)

        X_mds = self.__spectral_decomposition(B)

        return distance, B, X_mds

    # Private methods:
    def __euclidian_distance(self, data, n):
        distance = np.zeros((n, n))
        
        # print(distance)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                distance[i, j] = dist(data[i], data[j])

        return distance

    # Processamento dos dados (Matriz de Gram)
    def __gram_matrix(self, matrix):
        n = len(matrix)

        # Definir matriz de Centralização J:
        I = np.eye(n)
        ones = np.ones((n, n)) / n

        J = I - ones
        J

        # Matriz G = -(1/2)J * D² * J
        G = -0.5 * J @ (matrix**2) @ J

        return G
    
    def __spectral_decomposition(self, matrix):
        # Obtem os autovalores e autovetores da matriz:
        eigvals, eigvecs = np.linalg.eigh(matrix)

        # Ordenar do maior pro menor:
        idx = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]

        # Apenas os "n_components" maiores:
        L = np.diag(np.sqrt(eigvals[:self.n_components]))
        V = eigvecs[:, :self.n_components]

        # Coordenadas finais
        matrix_mds = V @ L

        return matrix_mds