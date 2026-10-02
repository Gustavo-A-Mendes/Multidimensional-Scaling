from pathlib import Path
import pandas as pd
import numpy as np

from mds_app.data.participant import Participant
from mds_app.utils.validators import *

# load a *.cls file and return dataframe:
def load_csv(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    return df

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
            df_temp = df.copy()
            first_col = df_temp.columns[0]
            if "Unnamed" in first_col or first_col == "" or first_col is None:
                df_temp.set_index(first_col, inplace=True)
                df_temp.index.name = None
            
            df_temp.columns = [str(c).strip() for c in df_temp.columns]
            df_temp.index = [str(i).strip() for i in df_temp.index]
            
            keywords = list(df_temp.columns)
            mat = df_temp.apply(pd.to_numeric, errors='coerce')
            
            # Garantir simetria
            mat = triangular_to_symmetric(mat)
            
            p_data = Participant(
                pid=0,
                name="Matriz Importada",
                group="Aluno",
                familiarity_level=" - "
            )
            p_data.add_dataframe(mat, "pre")
            participants_data = [p_data]

        elif file_type == "forms":
            # separate metadata and df
            for col in df.columns:

                # getting personal data from df:
                if "identificação" in col.lower():
                    names_temp = df[col].tolist()

                if "grupo" in col.lower():
                    groups_temp = df[col].tolist()

                if "nível" in col.lower():
                    levels_temp = df[col].tolist()

                # proceeding...

                # filtering the keyword of columns headers (and listing the data_columns):
                column = col.split("]")[1].strip() if "]" in col else col

                # column = col.split("-")[1].strip()

                if " - " not in column:
                    continue

                a, b = [x.strip() for x in column.split(" - ")]

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
                    column = col.split("]")[1].strip() if "]" in col else col

                    a, b = [x.strip() for x in column.split(" - ")]
                    valor = df.loc[idx, col]
                    try:
                        if pd.isna(valor):
                            val_numeric = np.nan
                        else:
                            val_numeric = float(valor)
                        
                        if np.isnan(val_numeric):
                            mat.at[a, b] = np.nan
                            mat.at[b, a] = np.nan
                        else:
                            mat.at[a, b] = val_numeric
                            mat.at[b, a] = val_numeric
                    except (ValueError, TypeError):
                        mat.at[a, b] = np.nan
                        mat.at[b, a] = np.nan

                # matrices.append(mat)
                if mat.empty:
                    return [], []

                # building participant info:
                num_participants = len(participants_dict)

                if groups_temp and not pd.isna(groups_temp[idx]):
                    grp_clean = str(groups_temp[idx]).strip().upper()
                    if grp_clean in ["PROFESSOR", "PROFESSORES", "DOCENTE", "DOCENTES", "GABARITO"]:
                        if not names_temp or pd.isna(names_temp[idx]):
                            name = f"Professor {p_num_participants}"
                            p_num_participants += 1
                        else:
                            name = names_temp[idx]
                        group = "Professor"
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                    elif grp_clean in ["ALUNO", "ALUNOS", "ESTUDANTE", "ESTUDANTES"]:
                        if not names_temp or pd.isna(names_temp[idx]):
                            name = f"Aluno {s_num_participants}"
                            s_num_participants += 1
                        else:
                            name = names_temp[idx]
                        group = "Aluno"
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                    else:
                        name = f"Participante {num_participants}" if not names_temp or pd.isna(names_temp[idx]) else names_temp[idx]
                        group = f" - " if pd.isna(groups_temp[idx]) else str(groups_temp[idx]).strip()
                        level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

                else:
                    name = f"Participante {num_participants}" if not names_temp or pd.isna(names_temp[idx]) else names_temp[idx]
                    group = f" - " if not groups_temp or pd.isna(groups_temp[idx]) else groups_temp[idx]
                    level = f" - " if not levels_temp or pd.isna(levels_temp[idx]) else levels_temp[idx]

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
                
                participant_data.add_dataframe(mat, "pre")

            participants_data = list(participants_dict.values())

    headers = keywords
    return participants_data, headers
