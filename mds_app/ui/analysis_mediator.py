import tkinter as tk
import numpy as np
import pandas as pd
from typing import TYPE_CHECKING

from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant

if TYPE_CHECKING:
    from mds_app.ui.control_panel import ControlPanel
    from mds_app.ui.visualization_area import VisualizationArea


class AnalysisMediator:
    """
    Mediador que centraliza o estado reativo, as métricas analíticas e a
    coordenação entre ControlPanel e VisualizationArea, eliminando o
    acoplamento direto entre as visões.
    """

    def __init__(self, dataset: Dataset, mode: str = "group") -> None:
        self.dataset = dataset
        self.mode = mode  # "group" ou "single"

        # Referências aos painéis visuais
        self.control_panel: "ControlPanel | None" = None
        self.visualization_area: "VisualizationArea | None" = None
        self.main_window = None

        # Seleção atual
        self.selected_id: int | None = 0 if mode == "single" else None
        self.selected_group: str = "students"

        # Variáveis reativas de análise e fase
        self.phase_var = tk.StringVar(value="pre")
        self.radio_var = tk.StringVar(value="default")

        # Variáveis de plot e visualização (Fonte Única da Verdade)
        self.highlight_values = tk.BooleanVar(value=False)
        self.destaque_view_values = tk.BooleanVar(value=True)
        self.mean_view_values = tk.BooleanVar(value=False)
        self.dispersion_view_values = tk.BooleanVar(value=False)
        self.ellipse_view_values = tk.BooleanVar(value=False)
        self.evo_view_values = tk.BooleanVar(value=False)
        self.all_selection_values = tk.BooleanVar(value=False)

        # Variáveis derivadas de plot
        self.p_mean_view = tk.BooleanVar(value=False)
        self.s_mean_view = tk.BooleanVar(value=False)
        self.ellipses_view = tk.BooleanVar(value=False)

        # Filtros de ranking
        self.ranking_mode_var = tk.StringVar(value="Todos os Alunos")
        self.ranking_n_var = tk.IntVar(value=5)

        # Lista de visibilidade de conceitos
        self.concept_visibility: list[tk.BooleanVar] = []
        self.sync_concept_visibility()

        # Cache analítico
        self.mds_results_pre: np.ndarray | None = None
        self.mds_results_pos: np.ndarray | None = None
        self.mds_results: np.ndarray | None = None
        self.ranked_indices: list[int] = []
        self.alignment_ranks: dict[int, int] = {}
        self.metric_values: dict[int, str] = {}

    # -------------------------------------------------------------------------
    # Registro de Componentes
    # -------------------------------------------------------------------------
    def register_control_panel(self, control_panel: "ControlPanel") -> None:
        self.control_panel = control_panel

    def register_visualization_area(self, visualization_area: "VisualizationArea") -> None:
        self.visualization_area = visualization_area

    # -------------------------------------------------------------------------
    # Gerenciamento de Conceitos e Visibilidade
    # -------------------------------------------------------------------------
    def sync_concept_visibility(self) -> None:
        """Garante que a lista de visibilidade de conceitos corresponda aos headers."""
        headers = self.dataset.headers if self.dataset else None
        num_concepts = len(headers) if headers else 0

        if len(self.concept_visibility) != num_concepts:
            self.concept_visibility = [tk.BooleanVar(value=True) for _ in range(num_concepts)]

        self.update_all_selection_state()

    def update_all_selection_state(self) -> None:
        """Atualiza a flag 'Selecionar Todos' conforme as caixas individuais."""
        if not self.concept_visibility:
            self.all_selection_values.set(False)
            return
        all_true = all(v.get() for v in self.concept_visibility)
        self.all_selection_values.set(all_true)

    def toggle_all_concepts(self, val: bool) -> None:
        """Ativa ou desativa a visibilidade de todos os conceitos."""
        for v in self.concept_visibility:
            v.set(val)
        self.all_selection_values.set(val)
        self.request_plot_update()

    def on_concept_visibility_changed(self) -> None:
        """Chamado quando um checkbox individual de conceito é alterado."""
        self.update_all_selection_state()
        self.request_plot_update()

    # -------------------------------------------------------------------------
    # Cálculos Analíticos de Coordenadas, Métricas e Rankings
    # -------------------------------------------------------------------------
    def compute_coordinates(self) -> None:
        """Extrai as coordenadas alinhadas de cada participante para pré e pós-teste."""
        if not self.dataset or not self.dataset.participants:
            self.mds_results_pre = None
            self.mds_results_pos = None
            self.mds_results = None
            return

        s_participants = self.dataset.participants.get("students", [])
        if not s_participants:
            self.mds_results_pre = None
            self.mds_results_pos = None
            self.mds_results = None
            return

        num_concepts = len(self.dataset.headers) if self.dataset.headers else 0

        def get_valid_mds(p_list, ph: str) -> np.ndarray:
            res = []
            for p in p_list:
                df = getattr(p, f"dataframe_{ph}", None)
                mds = getattr(p, f"mds_result_{ph}", None)
                if df is not None and not df.isna().all().all() and mds and mds.X_aligned is not None:
                    res.append(mds.X_aligned)
                else:
                    res.append(np.full((num_concepts, 2), np.nan))
            return np.array(res)

        self.mds_results_pre = get_valid_mds(s_participants, "pre")
        self.mds_results_pos = get_valid_mds(s_participants, "pos")

        actual_phase = self.phase_var.get()
        self.mds_results = self.mds_results_pos if actual_phase == "pos" else self.mds_results_pre

    def compute_ranking_and_metrics(self) -> None:
        """
        Calcula os índices ordenados de ranking e as métricas de alinhamento
        (distância euclidiana ao gabarito) e evolução (ganho pré->pós).
        """
        self.compute_coordinates()

        if self.dataset is None or not self.dataset.participants:
            self.ranked_indices = []
            self.alignment_ranks = {}
            self.metric_values = {}
            return

        students = self.dataset.participants.get("students", [])
        num_students = len(students)
        all_indices = list(range(num_students))

        p_centr_ref = self.dataset.centroids.get("professors") if self.dataset.centroids else None
        mode = self.ranking_mode_var.get()

        try:
            n = self.ranking_n_var.get()
        except (tk.TclError, ValueError):
            n = 5

        alignment_ranks: dict[int, int] = {}
        metric_values: dict[int, str] = {}
        ranked_indices = all_indices

        # 1. Distâncias absolutas de alinhamento ao gabarito
        if p_centr_ref is not None and self.mds_results is not None and len(self.mds_results) == num_students:
            distances: list[tuple[float, int]] = []
            for j in range(num_students):
                student_coords = self.mds_results[j]
                if (student_coords.shape == p_centr_ref.shape and
                    not np.any(np.isnan(student_coords)) and
                    not np.any(np.isnan(p_centr_ref))):
                    dist = float(np.sum(np.linalg.norm(student_coords - p_centr_ref, axis=1)))
                    distances.append((dist, j))

            # Ordenar por menor distância (mais alinhado)
            distances.sort(key=lambda x: x[0])
            for rank_pos, (dist, orig_idx) in enumerate(distances, start=1):
                alignment_ranks[orig_idx] = rank_pos

            # Se o modo for baseado em alinhamento, extrai rankings e textos formatados
            if mode == "Top Alinhados":
                for dist, orig_idx in distances:
                    metric_values[orig_idx] = f"{dist:.2f}"
                ranked_indices = [orig_idx for _, orig_idx in distances[:n]]

            elif mode == "Top Divergentes":
                for dist, orig_idx in distances:
                    metric_values[orig_idx] = f"{dist:.2f}"
                ranked_indices = [orig_idx for _, orig_idx in reversed(distances)][:n]

        # 2. Métricas de Evolução (Pré -> Pós)
        if mode == "Top Evolução" and p_centr_ref is not None:
            if self.mds_results_pre is not None and self.mds_results_pos is not None:
                evo_list: list[tuple[float, int]] = []
                for j in range(num_students):
                    pre_coords = self.mds_results_pre[j]
                    pos_coords = self.mds_results_pos[j]
                    if (pre_coords.shape == p_centr_ref.shape and
                        pos_coords.shape == p_centr_ref.shape and
                        not np.any(np.isnan(pre_coords)) and
                        not np.any(np.isnan(pos_coords)) and
                        not np.any(np.isnan(p_centr_ref))):

                        dist_pre = float(np.sum(np.linalg.norm(pre_coords - p_centr_ref, axis=1)))
                        dist_pos = float(np.sum(np.linalg.norm(pos_coords - p_centr_ref, axis=1)))
                        evo = dist_pre - dist_pos
                        evo_list.append((evo, j))
                        metric_values[j] = f"{evo:+.2f}"

                # Ordenar por maior evolução decrescente
                evo_list.sort(key=lambda x: x[0], reverse=True)
                ranked_indices = [orig_idx for _, orig_idx in evo_list[:n]]

        self.ranked_indices = ranked_indices
        self.alignment_ranks = alignment_ranks
        self.metric_values = metric_values

    def get_ranking_data(self) -> tuple[list[int], dict[int, int], dict[int, str]]:
        """Retorna os índices ordenados, ranks absolutos e textos de métricas."""
        return self.ranked_indices, self.alignment_ranks, self.metric_values

    def get_ranked_indices(self) -> list[int]:
        """Retorna a lista atual de índices filtrados."""
        return self.ranked_indices

    # -------------------------------------------------------------------------
    # Coordenação de Eventos e Ações do Usuário
    # -------------------------------------------------------------------------
    def select_participant(self, idx: int, group: str = "students", phase: str = None, status: str = None) -> None:
        """
        Sincroniza a seleção do participante ativo com os painéis.
        """
        self.selected_id = idx
        self.selected_group = group

        if phase:
            self.phase_var.set(phase)
        if status:
            self.radio_var.set(status)
            if status == "default":
                self.s_mean_view.set(False)
            elif status == "mean":
                self.s_mean_view.set(True)

        if self.visualization_area:
            self.visualization_area.set_index(
                idx=self.selected_id,
                phase=self.phase_var.get(),
                status=self.radio_var.get(),
                group=self.selected_group
            )

    def on_phase_or_view_changed(self) -> None:
        """Chamado quando o usuário alterna Pré/Pós-teste ou Modo Padrão/Média."""
        status = self.radio_var.get()
        if status == "default":
            self.s_mean_view.set(False)
        elif status == "mean":
            self.s_mean_view.set(True)

        self.compute_ranking_and_metrics()

        if self.control_panel:
            self.control_panel.refresh()

        if self.visualization_area:
            self.visualization_area.set_index(
                idx=self.selected_id if self.selected_id is not None else 0,
                phase=self.phase_var.get(),
                status=self.radio_var.get(),
                group=self.selected_group
            )

    def on_ranking_changed(self) -> None:
        """Chamado quando o modo de ranking ou a quantidade N é alterada."""
        self.compute_ranking_and_metrics()

        if self.control_panel:
            self.control_panel._populate_tree()

        self.request_plot_update()

    def request_plot_update(self) -> None:
        """Solicita ao painel de visualização o replot do gráfico MDS."""
        if self.visualization_area:
            self.visualization_area.show_mds()

    def notify_data_changed(self) -> None:
        """
        Notifica que a base de dados subjacente mudou estruturalmente
        (importação, inclusão/remoção de participante, limpeza ou alteração de conceitos).
        Recalcula médias, Procrustes, sincroniza visibilidades e renova os painéis.
        """
        self.dataset.calc_mean()
        self.sync_concept_visibility()
        self.compute_ranking_and_metrics()

        if self.visualization_area:
            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()
            self.visualization_area.refresh()

        if self.control_panel:
            self.control_panel.refresh()

    def clear_dataset(self) -> None:
        """Limpa o dataset e reconfigura o estado."""
        self.dataset.clear()
        self.selected_id = 0 if self.mode == "single" else None
        self.selected_group = "students"
        self.sync_concept_visibility()
        self.compute_ranking_and_metrics()

        if self.control_panel:
            self.control_panel.refresh()

        if self.visualization_area:
            self.visualization_area.refresh()
