from mds_app.analysis.mds_engine import MDSEngine

class Participant:
    def __init__(self, pid, name, group, familiarity_level, dataframe):
        self.pid = pid
        self.name = name
        self.group = group
        self.familiarity_level = familiarity_level
        self.dataframe = dataframe  # pandas DataFrame
        self.mds_result = MDSEngine(
            n_components=2,
            dissimilarity='precomputed',
        )   # placeholder para MDS

        # Calc MDS:
        self.mds_result.fit(self.dataframe)

        print(self.pid)
        # print(self.name)
        # print(self.dataframe)
        # print(self.mds_result.D)
        # print(self.mds_result.D_hat)
        print(self.mds_result.X)
        # print(self.mds_result.labels)
        print(self.mds_result.stress)
