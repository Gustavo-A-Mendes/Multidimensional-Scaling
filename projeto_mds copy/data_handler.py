import pandas as pd

class DataHandler:
    def __init__(self):
        self.df = None
        self.headers = []

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Carrega o CSV em um DataFrame temporário"""
        temp_df = pd.read_csv(file_path)
        self.df = temp_df
        self.headers = list(temp_df.columns)
        return temp_df

    def set_headers(self, headers: list):
        """Atualiza os cabeçalhos confirmados pelo usuário"""
        self.headers = headers
        self.df.columns = headers

    def add_row(self, row_data: dict):
        """Adiciona nova linha ao DataFrame"""
        new_row = pd.DataFrame([row_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
