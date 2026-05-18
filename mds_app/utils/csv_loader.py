# from wsgiref.validate import header_re
import math
from pathlib import Path
from tkinter import simpledialog, messagebox

import pandas as pd
import numpy as np
from numpy.ma.core import append

from mds_app.data.participant import Participant
from mds_app.data.dataset import Dataset
from mds_app.utils.validators import *


# load a *.cls file and return dataframe:
def load_csv(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    return df

def export_csv(filename: str, dataset: Dataset) -> None:
    participants = dataset.participants["professors"] + dataset.participants["students"]

    # convert each participant data into a row:
    rows = []

    # counting number os combination of 2:
    test = participants[0].dataframe.to_numpy()
    n_rows = test.shape[0]
    total_comb = math.comb(n_rows, 2)

    for participant in participants:
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
    p_participants = dataset.participants["professors"]
    s_participants = dataset.participants["students"]
    participants = p_participants + s_participants

    # create info dataframe:
    info = pd.DataFrame([
        {
            "id": p.pid,
            "Nome": p.name,
            "Grupo": p.group,
            "Nivel": p.familiarity_level
        }
        for p in participants
    ])

    # exportar para um arquivo Excel:
    with pd.ExcelWriter(f"{filename}.xlsx") as writer:

        # info sheet:
        info.to_excel(writer, sheet_name="Participantes", index=False)

        # data sheets:
        for participant in participants:
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
    return keywords

# converts forms sheet into a list of dict, containing participant data:
def separate_df(df: pd.DataFrame | dict[str, pd.DataFrame], file_type: str, file_ext: str) -> tuple[list[Participant], list[str]] | None:
    """Carrega o CSV em um DataFrame temporário"""
    participants_data = []
    names_temp = []
    groups_temp = []
    levels_temp = []
    phases_temp = []
    keywords = []
    data_columns = []

    if file_ext == ".csv" and isinstance(df, pd.DataFrame):
        if file_type == "ambiguous":
            pass

        # matrices already separated:
        if file_type == "matrix":
            pass

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

                if "fase" in col.lower() or "momento" in col.lower() or "etapa" in col.lower() or "periodo" in col.lower() or "período" in col.lower():
                    phases_temp = df[col].tolist()

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

            p_num_participants = 0
            s_num_participants = 0
            participants_dict = {}

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
                num_participants = len(participants_dict)

                if groups_temp and not pd.isna(groups_temp[idx]):
                    if groups_temp[idx].upper() == "PROFESSOR":
                        if not names_temp or pd.isna(names_temp[idx]):
                            name = f"Professor {p_num_participants}"
                            p_num_participants += 1
                        else:
                            name = names_temp[idx]
                        group = f"Professor"
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                    elif groups_temp[idx].upper() == "ALUNO":
                        if not names_temp or pd.isna(names_temp[idx]):
                            name = f"Aluno {s_num_participants}"
                            s_num_participants += 1
                        else:
                            name = names_temp[idx]
                        group = f"Aluno"
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                    else:
                        name = f"Participante {num_participants}" if not names_temp or pd.isna(names_temp[idx]) else names_temp[idx]
                        group = f" - " if pd.isna(groups_temp[idx]) else groups_temp[idx]
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                else:
                    name = f"Participante {num_participants}" if not names_temp or pd.isna(names_temp[idx]) else names_temp[idx]
                    group = f" - " if not groups_temp or pd.isna(groups_temp[idx]) else groups_temp[idx]
                    level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                phase = "pre" if not phases_temp or pd.isna(phases_temp[idx]) else phases_temp[idx]

                if name in participants_dict:
                    participant_data = participants_dict[name]
                else:
                    participant_data = Participant(
                        pid=num_participants,
                        name=name,
                        group=group,
                        familiarity_level=level
                    )
                    participants_dict[name] = participant_data
                
                participant_data.add_dataframe(mat, str(phase))

            participants_data = list(participants_dict.values())

    headers = keywords
    return participants_data, headers
