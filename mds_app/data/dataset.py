from typing import Any

import numpy as np
import numpy.typing as npt
import scipy
from scipy.linalg import orthogonal_procrustes

from mds_app.data.participant import Participant

Matrix = npt.NDArray[np.float64]

class Dataset:
    def __init__(self) -> None:
        self.participants: list[Participant] | None             = None
        self.headers: list[str] | None                          = None
        self.selected_participants: list[Participant] | None    = None
        self.selected_headers: list[str] | None                 = None

        self.centroids: Matrix | None   = None
        self.stds: Matrix | None        = None
        self.alinhados: Matrix | None   = None

    def set_participants(self, participants: list[Participant]) -> None:
        self.participants = participants

    def add_participant(self, participant: Participant) -> None:
        self.participants.append(participant)

    def set_headers(self, headers: list[str]) -> None:
        self.headers = list(headers)

    def set_selected_headers(self, headers: list[str]) -> None:
        self.selected_headers = list(headers)

    def headers_match(self, header: str) -> bool:
        return header in self.headers

    def add_header(self, header: str) -> bool:
        if self.headers_match(header):
            return False

        self.headers.append(header)

        for p in self.participants:
            p.dataframe[header] = "-"

        return True

    def can_remove_header(self, header: str) -> bool:
        if not self.headers_match(header):
            return False

        for p in self.participants:
            if not p.dataframe[header].eq("-").all():
                return False
        return True

    def remove_header(self, header: str) -> bool:
        if not self.can_remove_header(header):
            return False

        self.headers.remove(header)

        for p in self.participants:
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

    def calc_mean(self) -> None:
        coord_array = [p.mds_result.X for p in self.participants]

        # 1. Alinha todos os alunos usando Procrustes em relação ao Aluno 0 (ou professor)
        referencia = coord_array[0]
        alinhados = [referencia]

        for i in range(1, len(coord_array)):
            m2 = self.rigid_procrustes(referencia, coord_array[i])
            alinhados.append(m2)

        # 2. Calcula o centróide (média de cada ponto x,y)
        self.centroids = np.mean(alinhados, axis=0)

        self.alinhados = alinhados.copy()

        # 3. Calcula o desvio padrão para a elipse
        self.stds = np.std(alinhados, axis=0)

        for i in range (len(self.participants)):
            self.participants[i].mds_result.X_aligned = self.alinhados[i]

        # print(self.alinhados)
        # print(self.centroids)

    def get_global_limits(self) -> tuple[float, float]:
        # Concatena todas as matrizes X_aligned em uma única nuvem de pontos
        todas_coords = np.vstack([p.mds_result.X_aligned for p in self.participants])

        # Encontra o valor absoluto máximo para criar um gráfico centralizado e simétrico
        # Adicionamos uma margem de 10% (buffer) para os pontos não ficarem colados na borda
        margem = 1.1
        max_val = np.max(np.abs(todas_coords)) * margem

        return (-max_val, max_val)