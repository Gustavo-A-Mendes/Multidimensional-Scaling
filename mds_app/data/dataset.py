from typing import Any

import numpy as np
import numpy.typing as npt
import scipy
from pandas.core.array_algos.transforms import shift
from scipy.linalg import orthogonal_procrustes

from mds_app.data.participant import Participant

Matrix = npt.NDArray[np.float64]

class Dataset:
    def __init__(self) -> None:
        # self.participants: list[Participant] | None             = None
        #
        #
        # {
        #     "count": int,
        #     "professors": list[Participant],
        #     "professors_mean": {            -> Ideia de implementação
        #         "centroids": Matrix,
        #         "stds": Matrix
        #     }
        #     "students": list[Participant]
        #     "students_mean": {              -> ...
        #         "centroids": Matrix,
        #         "stds": Matrix
        #     }
        # }
        self.participants: dict[str, int|list[Participant]|None] | None = None

        self.has_professors = False
        self.has_students = False

        self.headers: list[str] | None                              = None
        self.selected_participants: list[Participant] | None        = None
        self.selected_headers: list[str] | None                     = None

        # self.centroids: Matrix | None   = None
        # self.stds: Matrix | None        = None
        # self.alinhados: Matrix | None   = None
        #
        # centroids | stds | alinhados {
        #     "professors": Matrix,
        #     "students": Matrix
        # }
        self.mean: dict[str, Matrix|None] | None = None
        self.centroids: dict[str, Matrix|None] | None = None
        self.stds: dict[str, Matrix|None] | None = None
        self.alinhados: dict[str, Matrix|None] | None = None

    #
    def set_new_participants(self, participants: list[Participant]) -> None:
        # clear dataset:
        self.participants = None
        self.has_professors = False
        self.has_students = False

        # --------------------------------------------------

        count = {
            "professors": 0,
            "students": 0
        }

        participants_dict = {
            "count": 0,
            "professors": [],
            "students": []
        }
        for p in participants:
            if p.group.upper() == "PROFESSOR":
                self.has_professors = True
                p.pid = count["professors"]
                count["professors"] += 1
                participants_dict["professors"].append(p)
                participants_dict["count"] += 1
            elif p.group.upper() == "ALUNO":
                self.has_students = True
                p.pid = count["students"]
                count["students"] += 1
                participants_dict["students"].append(p)
                participants_dict["count"] += 1

        self.participants = participants_dict

    #
    def add_participant(self, participant: Participant) -> None:
        participants_dict = {
            "count": 0 if self.participants["count"] is None else self.participants["count"],
            "professors": [] if self.participants["count"] is None else self.participants["professors"],
            "students": [] if self.participants["count"] is None else self.participants["students"]
        }

        if participant.group.upper() == "PROFESSOR":
            participants_dict["professors"].append(participant)
            participants_dict["count"] += 1
        elif participant.group.upper() == "ALUNO":
            participants_dict["students"].append(participant)
            participants_dict["count"] += 1

        self.participants = participants_dict

    #
    def set_headers(self, headers: list[str]) -> None:
        self.headers = list(headers)

    #
    def set_selected_headers(self, headers: list[str]) -> None:
        self.selected_headers = list(headers)

    #
    def headers_match(self, header: str) -> bool:
        return header in self.headers

    #
    def add_header(self, header: str) -> bool:
        if self.headers_match(header):
            return False

        self.headers.append(header)

        for p in self.participants["professors"]:
            p.dataframe[header] = "-"

        for p in self.participants["students"]:
            p.dataframe[header] = "-"

        return True

    #
    def can_remove_header(self, header: str) -> bool:
        if not self.headers_match(header):
            return False

        for p in self.participants["professors"]:
            if not p.dataframe[header].eq("-").all():
                return False

        for p in self.participants["students"]:
            if not p.dataframe[header].eq("-").all():
                return False

        return True

    #
    def remove_header(self, header: str) -> bool:
        if not self.can_remove_header(header):
            return False

        self.headers.remove(header)

        for p in self.participants["professors"]:
            if header in p.dataframe.columns:
                p.dataframe.drop(columns=[header], inplace=True)

        for p in self.participants["students"]:
            if header in p.dataframe.columns:
                p.dataframe.drop(columns=[header], inplace=True)

        return True

    #
    @staticmethod
    def rigid_procrustes(ref: Matrix, target: Matrix) -> Matrix:
        """
        Alinha 'target' a 'ref' sem alterar a escala (apenas rotação e translação).
        """
        # 1. Centralizar as matrizes na origem
        mu_ref = ref.mean(axis=0)
        mu_target = target.mean(axis=0)

        ref_centered = ref - mu_ref
        target_centered = target - mu_target

        # 2. Encontrar a matriz de rotação ideal (SVD)
        # orthogonal_procrustes resolve apenas a rotação
        R, _ = orthogonal_procrustes(ref_centered, target_centered)

        # 3. Aplicar rotação e depois voltar para a posição da referência (translação)
        target_aligned = (target_centered @ R.T) + mu_ref

        return target_aligned

    #
    def calc_mean(self) -> None:
        p_participants = self.participants["professors"]
        s_participants = self.participants["students"]
        # print(p_participants)
        # print(s_participants)

        p_coord_array = [p.mds_result.X for p in p_participants]
        p_matrix = [p.mds_result.D for p in p_participants]
        s_coord_array = [s.mds_result.X for s in s_participants]
        s_matrix = [s.mds_result.D for s in s_participants]

        mean: dict[str, Matrix|None]            = {"professors": None, "students": None}
        centroids: dict[str, Matrix|None]       = {"professors": None, "students": None}
        stds: dict[str, Matrix|None]            = {"professors": None, "students": None}
        alinhados: dict[str, list[Matrix]|None] = {"professors": None, "students": None}

        # ==================================================
        # 1. Professors

        # aligning all professors by using Procrustes based on the first professor:
        p_alinhados = []
        if p_coord_array:
            p_referencia = p_coord_array[0]
            p_alinhados = [p_referencia]

            if len(p_coord_array) > 1:
                for i in range(1, len(p_coord_array)):
                    m2 = self.rigid_procrustes(p_referencia, p_coord_array[i])
                    p_alinhados.append(m2)

            # 2. Calc centroids and dispersion of the columns of 'p_alinhados':
            p_mean = np.nanmean(p_matrix, axis=0)
            mean["professors"] = np.round(p_mean, 1)

            centroids["professors"] = np.mean(p_alinhados, axis=0)
            stds["professors"] = np.std(p_alinhados, axis=0)

        # 2. Students
        s_alinhados = []
        if p_coord_array:
            s_referencia = centroids["professors"]

            if p_coord_array:
                for i in range(len(s_coord_array)):
                    m2 = self.rigid_procrustes(s_referencia, s_coord_array[i])
                    s_alinhados.append(m2)

        elif s_coord_array:
            s_referencia = s_coord_array[0]
            s_alinhados = [s_referencia]

            # aligning all students by using Procrustes based on the professors mean:
            if len(s_coord_array) > 1:
                for i in range(1, len(s_coord_array)):
                    m2 = self.rigid_procrustes(s_referencia, s_coord_array[i])
                    s_alinhados.append(m2)

        if s_alinhados:
            s_mean = np.nanmean(s_matrix, axis=0)
            mean["students"] = np.round(s_mean, 1)

            centroids["students"] = np.mean(s_alinhados, axis=0)
            # manual std, because it'll use professors mean for the calc:
            stds["students"] = np.std(s_alinhados, axis=0)
            # stds["students"] = np.sqrt(np.mean((s_alinhados - centroids["professors"])**2, axis=0))

            # deslocar alinhados para o 1º quadrante:
            # total_alinhados = np.array([p_alinhados + s_alinhados])
            # shift_coord = self.get_shift_matrix(total_alinhados)
            # alinhados["students"] = [(s + shift_coord) for s in s_alinhados]
            alinhados["students"] = [s for s in s_alinhados]
            # colocar todos no quadrante 1:
            # alinhados["professors"] = [(p + shift_coord) for p in p_alinhados]
            alinhados["professors"] = [p for p in p_alinhados]

            self.mean = mean
            self.centroids = centroids
            self.alinhados = alinhados.copy()
            self.stds = stds.copy()

        # print(len(self.alinhados["professors"]))
        # print(len(self.alinhados["students"]))
        for i in range(len(p_participants)):
            p_participants[i].mds_result.X_aligned = self.alinhados["professors"][i]
        # print("Oi")

        for i in range(len(s_participants)):
            s_participants[i].mds_result.X_aligned = self.alinhados["students"][i]


        # print(self.alinhados)
        # print(self.centroids)

    #
    @staticmethod
    def get_shift_matrix(mats: npt.NDArray[Matrix]) -> Matrix:

        # encontre mínimos em x e y
        min_x = mats[..., 0].min()
        min_y = mats[..., 1].min()

        # deslocamentos necessários (se já forem positivos, o shift será 0)
        shift_x = -min_x if min_x < 0 else 0.0
        shift_y = -min_y if min_y < 0 else 0.0

        return np.array([shift_x, shift_y])

    #
    def get_global_limits(self) -> tuple[float, float]:
        participants = self.participants["professors"] + self.participants["students"]

        # Concatena todas as matrizes X_aligned em uma única nuvem de pontos
        all_coords = np.vstack([p.mds_result.X_aligned for p in participants])

        # Encontra o valor absoluto máximo para criar um gráfico centralizado e simétrico
        # Adicionamos uma margem de 10% (buffer) para os pontos não ficarem colados na borda
        margem = 1.1
        max_val = np.max((all_coords)) * margem
        min_val = np.min((all_coords)) * margem

        return (min_val, max_val)