# from wsgiref.validate import header_re
import math
from pathlib import Path
from tkinter import simpledialog, messagebox

import pandas as pd
import numpy as np
from mds_app.data.participant import Participant
from mds_app.data.dataset import Dataset
from mds_app.utils.validators import *


# load a *.cls file and return dataframe:
def load_csv(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    print(df)
    return df

# load a *.xlsx file and return dataframe (it enables read multi-sheet file):
def load_excel(filepath: Path) -> dict[str, pd.DataFrame] | None:
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

def export_csv(filename: str, dataset: Dataset) -> None:

    # convert each participant data into a row:
    rows = []

    # counting number os combination of 2:
    test = dataset.participants[0].dataframe.to_numpy()
    n_rows = test.shape[0]
    total_comb = math.comb(n_rows, 2)

    for participant in dataset.participants:
        df = participant.dataframe

        row = {
            "id": participant.pid,
            "Nome": participant.name,
            "Grupo": participant.group,
            "Nível": participant.familiarity_level
        }

        # add each value of flatten dataframe in the row:
        count = 0
        for i, r in enumerate(df.index):
            for h, c in enumerate(df.columns):
                if i >= h:
                    continue
                count += 1

                row[f"{count:02}/{total_comb} - {r} e {c}"] = df.loc[r, c]

        rows.append(row)

    df_csv = pd.DataFrame(rows)

    df_csv.to_csv(f"{filename}.csv", index=False)

def export_excel(filename: str, dataset: Dataset) -> None:

    # create info dataframe:
    info = pd.DataFrame([
        {
            "id": p.pid,
            "Nome": p.name,
            "Grupo": p.group,
            "Nivel": p.familiarity_level
        }
        for p in dataset.participants
    ])

    # exportar para um arquivo Excel:
    with pd.ExcelWriter(f"{filename}.xlsx") as writer:

        # info sheet:
        info.to_excel(writer, sheet_name="Participantes", index=False)

        # data sheets:
        for participant in dataset.participants:
            df = participant.dataframe
            sheet_name = f"Resposta_{participant.pid:02}"

            df.to_excel(writer, sheet_name=sheet_name)

# return a list with headers of dataframe (used to filter the forms headers):
def get_header(df: pd.DataFrame) -> list[str]:
    keywords = []

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
    # print(keywords)
    return keywords

# converts forms sheet into a list of dict, containing participant data:
def separate_df(df: pd.DataFrame | dict[str, pd.DataFrame], file_type: str, file_ext: str) -> tuple[list[Participant], list[str]] | None:
    """Carrega o CSV em um DataFrame temporário"""
    participants_data = []
    names_temp = []
    groups_temp = []
    levels_temp = []
    keywords = []
    data_columns = []

    if file_ext == ".csv" and isinstance(df, pd.DataFrame):
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


            participant_data = Participant(
                pid=num_participants,
                name=name,
                group=group,
                familiarity_level=level,
                dataframe=df
            )

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
            for idx in range(len(df)):

                # DataFrame quadrado vazio (index = nome das linhas)
                mat = pd.DataFrame(0, index=keywords, columns=keywords, dtype=float)

                for col in data_columns:
                    column = col.split("-")[1].strip()
                    a, b = [x.strip() for x in column.split(" e ")]
                    valor = df.loc[idx, col]
                    mat.at[a, b] = int(11-valor)
                    mat.at[b, a] = int(11-valor)

                # matrices.append(mat)
                if mat.empty:
                    return None

                # building participant info:
                num_participants = len(participants_data)

                name = f"Aluno {num_participants}" if pd.isna(names_temp[idx]) else names_temp[idx]
                group = f"Aluno" if pd.isna(groups_temp[idx]) else groups_temp[idx]
                level = f"Básico" if pd.isna(levels_temp[idx]) else levels_temp[idx]

                participant_data = Participant(
                    pid=num_participants,
                    name=name,
                    group=group,
                    familiarity_level=level,
                    dataframe=mat
                )
                participants_data.append(participant_data)

    elif (file_ext == ".xlsx" or file_ext == ".xls") and isinstance(df, dict):
        if file_type == "ambiguous":
            pass

        # matrices already separated:
        # dict -> key = name; value = df
        if file_type == "matrix":

            # Adjust matrix index column,
            for key, value in df.items():

                key = str(key)
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
                group = f"Aluno" if (not pd.isna(key) and "Aluno" in key) else "Professor"
                level = f"Nenhum"

                participant_data = Participant(
                    pid=num_participants,
                    name=name,
                    group=group,
                    familiarity_level=level,
                    dataframe=value
                )

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
            for idx in range(len(df_temp)):

                # DataFrame quadrado vazio (index = nome das linhas)
                mat = pd.DataFrame(0, index=keywords, columns=keywords, dtype=float)

                for col in data_columns:
                    column = col.split("-")[1].strip()
                    a, b = [x.strip() for x in column.split(" e ")]
                    valor = df_temp.loc[idx, col]
                    mat.at[a, b] = int(11 - valor)
                    mat.at[b, a] = int(11 - valor)

                # matrices.append(mat)
                if mat.empty:
                    return None

                # building participant info:
                num_participants = len(participants_data)

                name = f"Aluno {num_participants}" if pd.isna(names_temp[idx]) else names_temp[idx]
                group = f"Aluno" if pd.isna(groups_temp[idx]) else groups_temp[idx]
                level = f"Básico" if pd.isna(levels_temp[idx]) else levels_temp[idx]

                participant_data = Participant(
                    pid=num_participants,
                    name=name,
                    group=group,
                    familiarity_level=level,
                    dataframe=mat
                )

                participants_data.append(participant_data)

    headers = keywords
    return participants_data, headers
