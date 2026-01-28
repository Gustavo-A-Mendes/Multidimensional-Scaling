class Participant:
    def __init__(self, pid, name, group, familiarity_level, dataframe):
        self.pid = pid
        self.name = name
        self.group = group
        self.familiarity_level = familiarity_level
        self.dataframe = dataframe  # pandas DataFrame
        self.mds_result = None      # placeholder para MDS
