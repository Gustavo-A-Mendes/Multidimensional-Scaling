from math import sqrt, dist
import numpy as np
import numpy.typing as npt
from typing import Union
import pandas as pd
from scipy.spatial.distance import pdist, squareform

Matrix = npt.NDArray[np.float64]

class MDSEngine:
    """
        Classical Multidimensional Scaling (MDS).

        This class implements the algebraic (classical) MDS algorithm,
        which reconstructs coordinates of objects in a low-dimensional
        Euclidean space based on a dissimilarity matrix.

        The algorithm follows these steps:

            1. Compute the dissimilarity matrix D
            2. Compute the Gram matrix:
                    B = -1/2 * J * D² * J
            3. Perform spectral decomposition of B
            4. Construct the embedding using the largest eigenvalues
            5. Compute the Stress-1 metric

        Attributes
        ----------
        D : ndarray
            Original dissimilarity matrix.

        gram_ : ndarray
            Gram matrix derived from the dissimilarity matrix.

        X : ndarray
            Coordinates of the objects in the reduced space
            (the MDS embedding).

        D_hat : ndarray
            Reconstructed distance matrix from the embedding.

        eigenvalues : ndarray
            Eigenvalues obtained from spectral decomposition.

        stress : float
            Stress-1 value measuring embedding quality.
    """

    # def __init__(self, n_components=2, metric=True, n_init=4, max_iter=300, verbose=0, eps=0.001, n_jobs=1, random_state=None, dissimilarity='euclidean'):
    def __init__(self, n_components : int = 2, *, dissimilarity : str = 'precomputed', method : str = 'algebraic') -> None:
        """
            Initialize the MDS model.

            Parameters
            ----------
            n_components : int, default=2
                Number of dimensions for the embedding.

            dissimilarity : {'euclidean', 'precomputed'}
                Specifies the input format.

                'euclidean'
                    Input is raw feature data. Pairwise Euclidean
                    distances will be computed.

                'precomputed'
                    Input is already a dissimilarity matrix.
        """
        self.n_components: int  = n_components
        self.dissimilarity: str = dissimilarity
        self.method: str        = method

        # Core data:
        self.D: Matrix | None           = None
        self.labels: list[str] | None   = None
        self.n: int | None              = None # self.D.shape[0]

        # Intermediate results:
        self.gram_: Matrix | None       = None
        self.eigenvalues: Matrix | None = None

        # Final results:
        self.X: Matrix | None           = None
        self.X_aligned: Matrix | None   = None
        self.D_hat: Matrix | None       = None
        self.stress: float | None       = None

    # ----------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------

    # Fit the MDS model:
    def fit(self, data : Union[np.ndarray, pd.DataFrame], method : str = None) -> None:
        """
            Fit the MDS model.

            Parameters
            ----------
            data : array-like
                Input data or dissimilarity matrix.
            method : str
                Set MDS method (algebraic or iterative)
        """

        calc_method = method if method else self.method

        self.__prepare_dissimilarity(data)

        if calc_method == 'algebraic':
            self.__algebraic_compute()
        elif calc_method == 'iterative':
            self.__iterative_compute()
        else:
            raise ValueError("Método deve ser 'algebraic' ou 'interative'")

        # self.D, self.gram_, self.mds_data, self.stress = self.compute(X)

    # Fit the model and return the embedding:
    def fit_transform(self, data : Union[np.ndarray, pd.DataFrame], method : str = None) -> Matrix:
        """
            Fit the model and return the embedding.

            Parameters
            ----------
            data : array-like
                Input data or dissimilarity matrix.
            method : str
                Set MDS method (algebraic or iterative)

            Returns
            -------
            ndarray
                MDS embedding coordinates.
        """
        self.fit(data, method)
        return self.X

    # ----------------------------------------------------------------------
    # Private methods:
    # ----------------------------------------------------------------------

    # Perform the full MDS computation:
    def __algebraic_compute(self) -> None:
        """
            Perform the full MDS computation.
        """
        # Validação extra: O algébrico NÃO aceita NaNs
        if np.any(np.isnan(self.D)):
            # Aqui você pode aplicar a imputação por média discutida antes
            media = np.nanmean(self.D, dtype=np.float64)
            self.D = np.where(np.isnan(self.D), media, self.D)  # np.where([condition], [isTrue], [isFalse]

        # Compute Gram matrix:
        self.gram_ = self.__gram_matrix()

        # Spectral decomposition:
        self.X = self.__spectral_decomposition(self.gram_)

        # Reconstructed distantes:
        self.D_hat = squareform(pdist(self.X, metric="euclidean"))

        # Stress calculation:
        self.stress = self.__stress()

    #
    def __iterative_compute(self) -> None:
        """
            Implementação do MDS Iterativo (Ex: SMACOF).
            Este método é ideal quando há NaNs, pois pode ignorá-los no cálculo do Stress.
        """
        pass

    # Prepare the dissimilarity matrix based on input type:
    def __prepare_dissimilarity(self, data : Union[np.ndarray, pd.DataFrame]) -> None:
        """
        Prepare the dissimilarity matrix based on input type.
        """

        if isinstance(data, pd.DataFrame):
            self.labels = data.index.tolist()
            data = data.to_numpy()

        n = len(data)

        if self.dissimilarity == "euclidean":
            self.D = self.__euclidean_distance(data)

        elif self.dissimilarity == "precomputed":

            D = np.array(data)[:n, :n]

            # Ensure symmetry using upper triangle
            tri_sup = np.triu(D)
            self.D = tri_sup + tri_sup.T - np.diag(np.diag(tri_sup))

        else:
            raise ValueError(
                "dissimilarity must be 'euclidean' or 'precomputed'"
            )

        self.n = len(self.D)

    # Compute pairwise Euclidean distance matrix:
    @staticmethod
    def __euclidean_distance(data: Union[np.ndarray, list]) -> Matrix:
        """
            Compute pairwise Euclidean distance matrix.

            Parameters
            ----------
            data : array-like

            Returns
            -------
            ndarray
                Pairwise distance matrix.
        """

        # Efficient vectorized computation:
        return squareform(pdist(data, metric="euclidean"))

    # Compute the Gram matrix from the dissimilarity matrix:
    def __gram_matrix(self) -> Matrix:
        """
            Compute the Gram matrix from the dissimilarity matrix.

            Returns
            -------
            ndarray
                Gram matrix.
        """

        n = self.n

        # Definir matriz de Centralização J:
        I = np.eye(n)
        ones = np.ones((n, n)) / n

        J = I - ones
        # J

        # Matriz G = -(1/2)J * D² * J
        G = -0.5 * J @ (self.D**2) @ J

        return G

    # Perform eigenvalue decomposition of the Gram matrix:
    def __spectral_decomposition(self, matrix: np.ndarray) -> Matrix:
        """
            Perform eigenvalue decomposition of the Gram matrix.

            Parameters
            ----------
            matrix : ndarray
                Gram matrix.

            Returns
            -------
            ndarray
                Coordinates in the reduced dimensional space.
        """

        # Obtem os autovalores e autovetores da matriz:
        eigvals, eigvecs = np.linalg.eigh(matrix)

        # Sort descending:
        idx = np.argsort(eigvals)[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]

        # Keep positive eigenvalues only:
        positive = eigvals > 0
        eigvals = eigvals[positive]
        eigvecs = eigvecs[:, positive]

        # Verifica validade dos dados:
        if len(eigvals) < self.n_components:
            raise ValueError(
                "Number of positive eigenvalues is smaller thann n_components."
            )

        self.eigenvalues = eigvals

        L = np.diag(np.sqrt(eigvals[:self.n_components]))
        V = eigvecs[:, :self.n_components]

        # Final coordinates:
        matrix_mds = V @ L
        return matrix_mds

    # Compute Stress-1 (Kruskal) value:
    def __stress(self) -> float:
        """
            Compute Stress-1 (Kruskal) value.

            Returns
            -------
            float
                Stress value.
        """
        # Máscara para pegar apenas i < j:
        mask = np.triu(np.ones(self.D.shape), k=1).astype(bool)

        num = float(np.sum((self.D[mask] - self.D_hat[mask]) ** 2))
        den = float(np.sum(self.D[mask] ** 2))
        stress = np.sqrt(num / den)
        return stress