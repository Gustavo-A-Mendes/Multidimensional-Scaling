class Dataset:
    def __init__(self):
        self.participants = []
        self.headers = []

    def add_participant(self, participant):
        self.participants.append(participant)

    def set_headers(self, headers):
        self.headers = headers

    def headers_match(self, headers):
        return self.headers == headers
