import pandas as pd
from mds_app.analysis.mds_engine import MDSEngine

class Participant:
    def __init__(self, pid: int, name: str, group: str, familiarity_level: str) -> None:
        self.pid = pid
        self.name = name
        self.group = group
        self.familiarity_level = familiarity_level
        
        self.dataframe_pre = None
        self.mds_result_pre = None
        
        self.dataframe_pos = None
        self.mds_result_pos = None
        
    def add_dataframe(self, dataframe: pd.DataFrame, phase: str) -> None:
        if phase.lower() in ["pos", "pós", "pós-teste", "pos-teste", "fim", "final"]:
            self.dataframe_pos = dataframe
            self.mds_result_pos = MDSEngine(n_components=2, dissimilarity='precomputed')
            self.mds_result_pos.fit(self.dataframe_pos)
        else:
            self.dataframe_pre = dataframe
            self.mds_result_pre = MDSEngine(n_components=2, dissimilarity='precomputed')
            self.mds_result_pre.fit(self.dataframe_pre)

    @property
    def dataframe(self):
        return self.dataframe_pre
        
    @property
    def mds_result(self):
        return self.mds_result_pre
