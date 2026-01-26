# from wsgiref.validate import header_re
from tkinter import simpledialog, messagebox

import pandas as pd
import numpy as np
from mds_app.utils.validators import *


# load a *.cls file and return dataframe:
def load_csv(filepath):
    df = pd.read_csv(filepath)
    return df

# load a *.xlsx file and return dataframe (it enables read multi-sheet file):
def load_excel(filepath):
    dfs = pd.read_excel(filepath, sheet_name=None)

    # detects multi-sheet file
    ans = False
    if len(dfs) > 1:
        ans = messagebox.askyesnocancel(
            "Importação",
            "O arquivo possui múltiplas planilhas.\n\n"
            "Deseja importar TODAS as planilhas?\n\n"
        )

    if ans is None:
        return None

    if ans == False or len(dfs) == 1:
        return dict([next(iter(dfs.items()))])

    return dfs

# return a list with headers of dataframe (used to filter the forms headers):
def get_header(df):
    keywords = []
    colunas_validas = []

    for col in df.columns:
        # continuando...

        if "-" not in col:
            continue

        trecho = col.split("-")[1].strip()

        if " e " not in trecho:
            continue

        a, b = [x.strip() for x in trecho.split(" e ")]
        if a not in keywords:
            keywords.append(a)
        if b not in keywords:
            keywords.append(b)
    print(keywords)
    return keywords

# converts forms sheet into a list of dict, containing participant data:
def separate_df(df, file_type, file_ext):
    """Carrega o CSV em um DataFrame temporário"""
    participants_data = []
    names_temp = []
    groups_temp = []
    levels_temp = []
    keywords = []
    data_columns = []

    if file_ext == ".csv":

        if file_type == "ambiguous":
            pass

        # matrices already separated:
        if file_type == "matrix":
            # check is the sheet has an index name column:
            has_index_col = "Unnamed: 0" in df.columns

            # update index name column:
            if has_index_col:
                df.set_index(df.columns[0], inplace=True)

            # guarantee that df is a symmetric matrix:
            df = triangular_to_symmetric(df)

            # get the heardes keywords:
            keywords = list(df.columns)

            # building participant info:
            num_participants = len(participants_data)

            name = f"Aluno {num_participants}"
            group = f"Aluno"
            level = f""

            participant_data = {
                "pid": num_participants,
                "name": name,
                "group": group,
                "level": level,
                "df": df
            }

            participants_data.append(participant_data)

        elif file_type == "forms":
            # separate metadata and df
            for col in df.columns:

                # getting personal data from df:
                if "nome" in col.lower():
                    names_temp = df[col].tolist()

                if "grupo" in col.lower():
                    groups_temp = df[col].tolist()

                if "nível" in col.lower():
                    levels_temp = df[col].tolist()

                # proceeding...

                # filtering the keyword of columns headers (and listing the data_columns):
                if "-" not in col:
                    continue

                column = col.split("-")[1].strip()

                if " e " not in column:
                    continue

                a, b = [x.strip() for x in column.split(" e ")]

                if a not in keywords:
                    keywords.append(a)
                if b not in keywords:
                    keywords.append(b)

                data_columns.append(col)

            # generate matrices and building participants infos:
            for idx, row in df.iterrows():

                # DataFrame quadrado vazio (index = nome das linhas)
                mat = pd.DataFrame(0, index=keywords, columns=keywords, dtype=float)

                for col in data_columns:
                    column = col.split("-")[1].strip()
                    a, b = [x.strip() for x in column.split(" e ")]
                    valor = row[col]
                    mat.at[a, b] = int(valor)
                    mat.at[b, a] = int(valor)

                # matrices.append(mat)
                if mat.empty:
                    return None

                # building participant info:
                num_participants = len(participants_data)

                name = f"Aluno {num_participants}" if pd.isna(names_temp[idx]) else names_temp[idx]
                group = f"Aluno" if pd.isna(groups_temp[idx]) else groups_temp[idx]
                level = f"Básico" if pd.isna(levels_temp[idx]) else levels_temp[idx]

                participant_data = {
                    "pid": num_participants,
                    "name": name,
                    "group": group,
                    "level": level,
                    "df": mat
                }

                participants_data.append(participant_data)

    elif file_ext == ".xlsx" or file_ext == ".xls":
        if file_type == "ambiguous":
            pass

        # matrices already separated:
        # dict -> key = name; value = df
        if file_type == "matrix":

            # Adjust matrix index column,
            for key, value in df.items():

                # check is the sheet has an index name column:
                has_index_col = "Unnamed: 0" in value.columns

                # update index name column:
                if has_index_col:
                    value.set_index(value.columns[0], inplace=True)

                # guarantee that df is a symmetric matrix:
                value = triangular_to_symmetric(value)

                # get the heardes keywords:
                keywords = list(value.columns)

                # building participant info:
                num_participants = len(participants_data)

                name = f"Aluno {num_participants}" if pd.isna(key) else key
                group = f"Aluno" if (pd.isna(key) and "Aluno" in key) else key
                level = f""

                participant_data = {
                    "pid": num_participants,
                    "name": name,
                    "group": group,
                    "level": level,
                    "df": value
                }

                participants_data.append(participant_data)

        elif file_type == "forms":
            # just one sheet, but df is a dict():
            df_temp = list(df.values())[0].copy()

            # separate metadata and df
            for col in df_temp.columns:

                # getting personal data from df_temp:
                if "nome" in col.lower():
                    names_temp = df_temp[col].tolist()

                if "grupo" in col.lower():
                    groups_temp = df_temp[col].tolist()

                if "nível" in col.lower():
                    levels_temp = df_temp[col].tolist()

                # proceeding...

                # filtering the keyword of columns headers (and listing the data_columns):
                if "-" not in col:
                    continue

                column = col.split("-")[1].strip()

                if " e " not in column:
                    continue

                a, b = [x.strip() for x in column.split(" e ")]

                if a not in keywords:
                    keywords.append(a)
                if b not in keywords:
                    keywords.append(b)

                data_columns.append(col)

            # generate matrices and building participants infos:
            for idx, row in df_temp.iterrows():

                # DataFrame quadrado vazio (index = nome das linhas)
                mat = pd.DataFrame(0, index=keywords, columns=keywords, dtype=float)

                for col in data_columns:
                    column = col.split("-")[1].strip()
                    a, b = [x.strip() for x in column.split(" e ")]
                    valor = row[col]
                    mat.at[a, b] = int(valor)
                    mat.at[b, a] = int(valor)

                # matrices.append(mat)
                if mat.empty:
                    return None

                # building participant info:
                num_participants = len(participants_data)

                name = f"Aluno {num_participants}" if pd.isna(names_temp[idx]) else names_temp[idx]
                group = f"Aluno" if pd.isna(groups_temp[idx]) else groups_temp[idx]
                level = f"Básico" if pd.isna(levels_temp[idx]) else levels_temp[idx]

                participant_data = {
                    "pid": num_participants,
                    "name": name,
                    "group": group,
                    "level": level,
                    "df": mat
                }

                participants_data.append(participant_data)

    headers = keywords

    return participants_data, headers
