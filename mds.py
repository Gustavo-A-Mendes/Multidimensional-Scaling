class MDS:
    # def __init__(self, n_components=2, metric=True, n_init=4, max_iter=300, verbose=0, eps=0.001, n_jobs=1, random_state=None, dissimilarity='euclidean'):
    def __init__(self, n_components=2, *, dissimilarity='euclidean'):
        self.n_components = n_components
        self.dissimilarity = dissimilarity

    def compute(self, X, y=None, init=None):
        