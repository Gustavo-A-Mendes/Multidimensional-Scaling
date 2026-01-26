class Dataset:
    def __init__(self):
        self.participants = []
        self.headers = []
        self.selected_participants = []
        self.selected_headers = []

    def set_participants(self, participant):
        self.participants = list(participant)

    def add_participant(self, participant):
        self.participants.append(participant)

    def set_headers(self, headers):
        self.headers = list(headers)

    def set_selected_headers(self, headers):
        self.selected_headers = list(headers)

    def headers_match(self, headers):
        return headers in self.headers

    def add_header(self, header):
        if self.headers_match(header):
            return False

        self.headers.append(header)

        for p in self.participants:
            p.dataframe[header] = "-"

        return True

    def can_remove_header(self, header):
        if not self.headers_match(header):
            return False

        for p in self.participants:
            if not p.dataframe[header].eq("-").all():
                return False
        return True

    def remove_header(self, header):
        if not self.can_remove_header(header):
            return False

        self.headers.remove(header)

        for p in self.participants:
            if header in p.dataframe.columns:
                p.dataframe.drop(columns=[header], inplace=True)

        return True
