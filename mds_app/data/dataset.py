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
        self.participants: dict[str, list[Participant]] | None = None

        self.has_professors = False
        self.has_students = False

        self.headers: list[str] | None                              = None
        self.selected_participants: list[Participant] | None        = None
        self.selected_headers: list[str] | None                     = None
        self.concept_mapping: dict[str, str]                        = {}

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
            "professors": [],
            "students": []
        }
        for p in participants:
            if p.group.upper() == "PROFESSOR":
                self.has_professors = True
                p.pid = count["professors"]
                count["professors"] += 1
                participants_dict["professors"].append(p)
            elif p.group.upper() == "ALUNO":
                self.has_students = True
                p.pid = count["students"]
                count["students"] += 1
                participants_dict["students"].append(p)

        self.participants = participants_dict

    #
    def add_participant(self, participant: Participant) -> None:
        if self.participants is None:
            self.participants = {
                "professors": [],
                "students": []
            }

        if participant.group.upper() == "PROFESSOR":
            self.participants["professors"].append(participant)
            self.has_professors = True
        elif participant.group.upper() == "ALUNO":
            self.participants["students"].append(participant)
            self.has_students = True

    def add_participants(self, participants: list[Participant]) -> None:
        if self.participants is None:
            self.participants = {
                "professors": [],
                "students": []
            }

        for p_new in participants:
            group_key = "professors" if p_new.group.upper() == "PROFESSOR" else "students"
            
            # Tentar encontrar o participante existente pelo nome para fundir os dados
            existing_p = next((p for p in self.participants[group_key] if p.name == p_new.name), None)
            
            if existing_p:
                # Mescla a matriz lida no pós-teste para dentro do objeto existente
                if p_new.dataframe_pre is not None:
                    existing_p.add_dataframe(p_new.dataframe_pre, phase="pos")
            else:
                # Participante novo que só respondeu o pós-teste
                if p_new.dataframe_pre is not None:
                    p_new.add_dataframe(p_new.dataframe_pre, phase="pos")
                    p_new.dataframe_pre = None
                    p_new.mds_result_pre = None
                    
                p_new.pid = len(self.participants[group_key])
                self.participants[group_key].append(p_new)
                
                if group_key == "professors":
                    self.has_professors = True
                else:
                    self.has_students = True

    #
    def set_headers(self, headers: list[str]) -> None:
        self.headers = list(headers)
        self.concept_mapping = {h: f"C{i+1}" for i, h in enumerate(self.headers)}

    #
    def set_selected_headers(self, headers: list[str]) -> None:
        self.selected_headers = list(headers)

    #
    def headers_match(self, header: str) -> bool:
        return header in self.headers

    def add_header(self, header: str) -> bool:
        if self.headers_match(header):
            return False

        self.headers.append(header)
        self.concept_mapping = {h: f"C{i+1}" for i, h in enumerate(self.headers)}

        for p in self.participants["professors"] + self.participants["students"]:
            if p.dataframe_pre is not None:
                p.dataframe_pre[header] = "-"
            if p.dataframe_pos is not None:
                p.dataframe_pos[header] = "-"

        return True

    #
    def can_remove_header(self, header: str) -> bool:
        if not self.headers_match(header):
            return False

        for p in self.participants["professors"] + self.participants["students"]:
            if p.dataframe_pre is not None and not p.dataframe_pre[header].eq("-").all():
                return False
            if p.dataframe_pos is not None and not p.dataframe_pos[header].eq("-").all():
                return False

        return True

    #
    def remove_header(self, header: str) -> bool:
        if not self.can_remove_header(header):
            return False

        self.headers.remove(header)
        self.concept_mapping = {h: f"C{i+1}" for i, h in enumerate(self.headers)}

        for p in self.participants["professors"] + self.participants["students"]:
            if p.dataframe_pre is not None and header in p.dataframe_pre.columns:
                p.dataframe_pre.drop(columns=[header], inplace=True)
            if p.dataframe_pos is not None and header in p.dataframe_pos.columns:
                p.dataframe_pos.drop(columns=[header], inplace=True)

        return True

    #
    @staticmethod
    def rigid_procrustes(ref: Matrix, target: Matrix) -> Matrix:
        """
        Alinha 'target' a 'ref' sem alterar a escala (apenas rotação e translação).
        """
        if ref is None or target is None:
            raise ValueError("As matrizes para Procrustes não podem ser nulas.")
            
        if ref.shape != target.shape:
            raise ValueError(
                f"As matrizes de coordenadas possuem dimensões diferentes para alinhamento: "
                f"Referência {ref.shape} vs Alvo {target.shape}. Certifique-se de que todos os "
                f"participantes tenham respondido os mesmos conceitos e itens."
            )
            
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

    def calc_mean(self) -> None:
        mean: dict[str, Matrix|None]            = {}
        centroids: dict[str, Matrix|None]       = {}
        stds: dict[str, Matrix|None]            = {}
        alinhados: dict[str, list[Matrix]|None] = {}

        # 1. Unificar Professores (Priorizar Pós, usar Pré como fallback)
        unified_p_matrices = []
        unified_p_coords = []
        unified_p_participants = []

        for p in self.participants["professors"]:
            if p.dataframe_pos is not None:
                unified_p_matrices.append(p.mds_result_pos.D)
                unified_p_coords.append(p.mds_result_pos.X)
                unified_p_participants.append(p)
            elif p.dataframe_pre is not None:
                unified_p_matrices.append(p.mds_result_pre.D)
                unified_p_coords.append(p.mds_result_pre.X)
                unified_p_participants.append(p)

        mean["professors"] = None
        centroids["professors"] = None
        stds["professors"] = None
        alinhados["professors"] = None

        if unified_p_coords:
            p_referencia = unified_p_coords[0]
            p_alinhados = [p_referencia]
            if len(unified_p_coords) > 1:
                for i in range(1, len(unified_p_coords)):
                    m2 = self.rigid_procrustes(p_referencia, unified_p_coords[i])
                    p_alinhados.append(m2)

            p_mean = np.nanmean(unified_p_matrices, axis=0)
            mean["professors"] = np.round(p_mean, 1)
            centroids["professors"] = np.mean(p_alinhados, axis=0)
            stds["professors"] = np.std(p_alinhados, axis=0)
            alinhados["professors"] = p_alinhados

            # Salvar X_aligned em ambas as instâncias mds_result do professor (se existirem)
            for i, p in enumerate(unified_p_participants):
                if p.dataframe_pre is not None:
                    p.mds_result_pre.X_aligned = p_alinhados[i]
                if p.dataframe_pos is not None:
                    p.mds_result_pos.X_aligned = p_alinhados[i]

        # 2. Estudantes
        for phase in ["pre", "pos"]:
            s_participants = [p for p in self.participants["students"] if getattr(p, f"dataframe_{phase}") is not None]

            s_coord_array = [getattr(s, f"mds_result_{phase}").X for s in s_participants]
            s_matrix = [getattr(s, f"mds_result_{phase}").D for s in s_participants]

            mean[f"students_{phase}"] = None
            centroids[f"students_{phase}"] = None
            stds[f"students_{phase}"] = None
            alinhados[f"students_{phase}"] = None

            s_alinhados = []
            s_referencia = centroids["professors"]

            if s_referencia is not None:
                if s_coord_array:
                    for i in range(len(s_coord_array)):
                        m2 = self.rigid_procrustes(s_referencia, s_coord_array[i])
                        s_alinhados.append(m2)
            elif s_coord_array:
                if phase == "pos" and centroids.get("students_pre") is not None:
                    s_referencia = centroids["students_pre"]
                    for i in range(len(s_coord_array)):
                        m2 = self.rigid_procrustes(s_referencia, s_coord_array[i])
                        s_alinhados.append(m2)
                else:
                    s_referencia = s_coord_array[0]
                    s_alinhados = [s_referencia]
                    if len(s_coord_array) > 1:
                        for i in range(1, len(s_coord_array)):
                            m2 = self.rigid_procrustes(s_referencia, s_coord_array[i])
                            s_alinhados.append(m2)

            if s_alinhados:
                s_mean = np.nanmean(s_matrix, axis=0)
                mean[f"students_{phase}"] = np.round(s_mean, 1)
                centroids[f"students_{phase}"] = np.mean(s_alinhados, axis=0)
                stds[f"students_{phase}"] = np.std(s_alinhados, axis=0)
                
            alinhados[f"students_{phase}"] = s_alinhados

            for i, s in enumerate(s_participants):
                getattr(s, f"mds_result_{phase}").X_aligned = alinhados[f"students_{phase}"][i]

        self.mean = mean
        self.centroids = centroids
        self.alinhados = alinhados
        self.stds = stds

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
        all_coords = []
        for p in participants:
            if p.mds_result_pre and p.mds_result_pre.X_aligned is not None:
                all_coords.append(p.mds_result_pre.X_aligned)
            if p.mds_result_pos and p.mds_result_pos.X_aligned is not None:
                all_coords.append(p.mds_result_pos.X_aligned)
        
        if not all_coords:
            return (-1.0, 1.0)
            
        all_coords = np.vstack(all_coords)
        if np.all(np.isnan(all_coords)):
            return (-1.0, 1.0)

        # Encontra o valor absoluto máximo para criar um gráfico centralizado e simétrico
        # Adicionamos uma margem de 15% (buffer) para os pontos não ficarem colados na borda
        margem = 1.15
        max_abs = np.nanmax(np.abs(all_coords))
        if max_abs == 0 or np.isnan(max_abs):
            return (-1.0, 1.0)
            
        limit_val = max_abs * margem
        return (-limit_val, limit_val)