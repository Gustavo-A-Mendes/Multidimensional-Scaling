class Participant:
    def __init__(self, pid, group, familiarity, dataframe):
        self.pid = pid
        self.group = group
        self.familiarity = familiarity
        self.dataframe = dataframe  # pandas DataFrame
        self.mds_result = None      # placeholder para MDS
