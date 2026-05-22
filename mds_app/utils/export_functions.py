import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PathCollection, LineCollection

import pandas as pd
import zipfile
import io

def gerar_plot_para_exportar(dados_aluno, config_opcoes):
    # Cria uma figura nova que não vai para o canvas da tela
    fig, ax = plt.subplots(figsize=(8, 6))

    # ... executa a mesma lógica da sua função show_mds ...
    # Se config_opcoes['gabarito']: desenha linhas de conexão
    # Se config_opcoes['elipse']: desenha as elipses

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)  # Importante para não vazar memória
    return buf.getvalue()  # Retorna os bytes da imagem


def exportar_tudo_para_zip(zip_path, data, ui_config, filtered_indices=None, progress_callback=None):
    alunos_orig = data.participants["students"]
    if filtered_indices is not None:
        alunos = [alunos_orig[i] for i in filtered_indices]
    else:
        alunos = alunos_orig
        
    professores = data.participants["professors"]
    total_participant = professores + alunos

    headers = data.headers
    generic_headers = [data.concept_mapping.get(h, h) for h in headers]

    phases_to_export = []
    if ui_config.var_phase_pre.get(): phases_to_export.append("pre")
    if ui_config.var_phase_pos.get(): phases_to_export.append("pos")

    total_steps = 0
    if ui_config.var_matrizes.get(): total_steps += len(phases_to_export)
    if ui_config.var_coords.get(): total_steps += len(phases_to_export)
    if ui_config.var_plot_indiv.get(): total_steps += len(alunos) * len(phases_to_export)
    if ui_config.var_plot_media.get(): total_steps += len(phases_to_export)

    current_step = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:

        for phase in phases_to_export:
            phase_name = "Pre-teste" if phase == "pre" else "Pos-teste"
            
            alunos_mean = data.mean.get(f"students_{phase}")
            alunos_centroid = data.centroids.get(f"students_{phase}")
            professores_mean = data.mean.get("professors")
            professores_centroid = data.centroids.get("professors")
            
            if filtered_indices is not None and len(filtered_indices) > 0:
                filtered_mds = data.alinhados.get(f"students_{phase}")
                if filtered_mds is not None:
                    alunos_mean = None # For matrices we don't recalculate the raw matrix mean, wait, yes we can!
                    filtered_df = [data.participants["students"][i].dataframe for i in filtered_indices]
                    # But the mean of dataframes is not easily calculated here. Let's stick to centroid mean.
                    # Wait, if we use filtered_indices, we won't output Média_Turma in Matrices, or we output the global.
                    # Let's keep alunos_mean global for matrices, or calculate it.
                    # Actually, data.mean["students"] is what we have. It's complex to average DataFrames.
                    filtered_mds_subset = [filtered_mds[i] for i in filtered_indices]
                    alunos_centroid = np.mean(filtered_mds_subset, axis=0)
            
            # --- EXPORTAÇÃO DE MATRIZES ---
            if ui_config.var_matrizes.get():
                if progress_callback:
                    progress_callback(current_step, total_steps, f"Gerando matrizes ({phase_name})...")

                output = io.BytesIO()

                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Folha de Legenda como a primeira aba
                    df_legenda = pd.DataFrame([
                        {"Sigla": data.concept_mapping.get(h, f"C{i+1}"), "Conceito": h}
                        for i, h in enumerate(headers)
                    ])
                    df_legenda.to_excel(writer, sheet_name="Legenda", index=False)

                    info = pd.DataFrame([
                        {
                            "id": p.pid,
                            "Nome": p.name,
                            "Grupo": p.group,
                            "Nivel": p.familiarity_level
                        }
                        for p in total_participant
                    ])
                    info.to_excel(writer, sheet_name="Participantes")

                    if professores_mean is not None:
                        df_media = pd.DataFrame(professores_mean, index=generic_headers, columns=generic_headers)
                        df_media.to_excel(writer, sheet_name="Gabarito")

                    if alunos_mean is not None:
                        df_media = pd.DataFrame(alunos_mean, index=generic_headers, columns=generic_headers)
                        df_media.to_excel(writer, sheet_name="Média_Turma")

                    for participant in total_participant:
                        df = getattr(participant, f"dataframe_{phase}", None)
                        if df is None and participant.group.upper() == "PROFESSOR" and phase == "pos":
                            df = participant.dataframe_pre
                        
                        if df is not None:
                            if participant.group.upper() == "PROFESSOR":
                                nome = f"Prof_{participant.pid:02}_{phase}"[:31]
                            else:
                                nome =  f"Aluno_{participant.pid:02}_{phase}"[:31]
                            df_copy = df.copy()
                            df_copy.rename(index=data.concept_mapping, columns=data.concept_mapping, inplace=True)
                            df_copy.to_excel(writer, sheet_name=nome)

                zf.writestr(f"{phase_name}/matrizes_dissimilaridade_{phase}.xlsx", output.getvalue())
                current_step += 1
                if progress_callback: progress_callback(current_step, total_steps)

            # --- EXPORTAÇÃO DE COORDENADAS ---
            if ui_config.var_coords.get():
                if progress_callback:
                    progress_callback(current_step, total_steps, f"Gerando coordenadas ({phase_name})...")

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Folha de Legenda como a primeira aba
                    df_legenda = pd.DataFrame([
                        {"Sigla": data.concept_mapping.get(h, f"C{i+1}"), "Conceito": h}
                        for i, h in enumerate(headers)
                    ])
                    df_legenda.to_excel(writer, sheet_name="Legenda", index=False)

                    if professores_centroid is not None:
                        df_media = pd.DataFrame(professores_centroid, index=generic_headers, columns=['X', 'Y'])
                        df_media.to_excel(writer, sheet_name="Gabarito")

                    if alunos_centroid is not None:
                        df_media = pd.DataFrame(alunos_centroid, index=generic_headers, columns=['X', 'Y'])
                        df_media.to_excel(writer, sheet_name="Média_Turma")

                    for participant in total_participant:
                        mds_res = getattr(participant, f"mds_result_{phase}", None)
                        if mds_res is None and participant.group.upper() == "PROFESSOR" and phase == "pos":
                            mds_res = participant.mds_result_pre
                            
                        if mds_res is not None and mds_res.X_aligned is not None:
                            df = pd.DataFrame(mds_res.X_aligned, index=generic_headers, columns=['X', 'Y'])
                            if participant.group.upper() == "PROFESSOR":
                                nome = f"Prof_{participant.pid:02}_{phase}"[:31]
                            else:
                                nome = f"Aluno_{participant.pid:02}_{phase}"[:31]
                            df.to_excel(writer, sheet_name=nome)

                zf.writestr(f"{phase_name}/coordenadas_mds_{phase}.xlsx", output.getvalue())
                current_step += 1
                if progress_callback: progress_callback(current_step, total_steps)

            limite = data.get_global_limits()
            
            # --- EXPORTAÇÃO DE PLOTS ---
            if ui_config.var_plot_indiv.get():
                for aluno in alunos:
                    if progress_callback: progress_callback(current_step, total_steps, f"Gerando gráfico: Aluno {aluno.pid} ({phase_name})")

                    img_data = gerar_imagem_mds(aluno, data, phase, headers, limite, ui_config)
                    if img_data is not None:
                        zf.writestr(f"{phase_name}/plots_individuais/mds_{aluno.pid}_{phase}.png", img_data)

                    current_step += 1

            if ui_config.var_plot_media.get():
                if progress_callback: progress_callback(current_step, total_steps, f"Gerando média da turma ({phase_name})...")

                img_media = gerar_imagem_media(data, phase, limite, ui_config, filtered_indices)
                if img_media is not None:
                    zf.writestr(f"{phase_name}/plot_turma/mds_media_turma_{phase}.png", img_media)

                current_step += 1


def gerar_imagem_mds(aluno, data, phase, headers, limite, ui_config):
    mds_res = getattr(aluno, f"mds_result_{phase}", None)
    if mds_res is None or mds_res.X_aligned is None:
        return None
        
    aluno_mds = mds_res.X_aligned
    professor_data = data.centroids.get("professors")
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    num_concepts = len(aluno_mds)
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i % 20) for i in range(num_concepts)]

    # 1. Plotar os pontos do aluno
    ax.scatter(aluno_mds[:, 0], aluno_mds[:, 1], c=colors, marker='o', label='Aluno', zorder=3)

    plot_range = limite[1] - limite[0]
    proximity_threshold = 0.06 * plot_range
    placed_positions = []
    offsets = [
        (0.0, 0.12),    # Acima
        (0.0, -0.22),   # Abaixo
        (0.18, -0.05),  # Direita
        (-0.18, -0.05), # Esquerda
        (0.13, 0.13),   # Superior Direito
        (-0.13, -0.18), # Inferior Esquerdo
        (0.13, -0.18),  # Inferior Direito
        (-0.13, 0.13)   # Superior Esquerdo
    ]

    for i in range(num_concepts):
        generic_name = data.concept_mapping.get(headers[i], f"C{i+1}")
        x, y = aluno_mds[i, 0], aluno_mds[i, 1]
        
        collision_count = 0
        for px, py in placed_positions:
            if np.sqrt((x - px)**2 + (y - py)**2) < proximity_threshold:
                collision_count += 1
                
        offset_idx = collision_count % len(offsets)
        dx, dy = offsets[offset_idx]
        scaled_dx = dx * (plot_range / 10.0)
        scaled_dy = dy * (plot_range / 10.0)
        
        ax.text(
            x + scaled_dx,
            y + scaled_dy,
            generic_name,
            fontsize=9,
            fontweight='bold',
            color=colors[i],
            ha='center',
            va='center',
            zorder=4
        )
        placed_positions.append((x, y))

    if ui_config.var_gabarito_indiv.get() and professor_data is not None:
        ax.scatter(professor_data[:, 0], professor_data[:, 1], c=colors, marker='x', label='Gabarito')
        for i in range(num_concepts):
            ax.plot(
                [aluno_mds[i, 0], professor_data[i, 0]],
                [aluno_mds[i, 1], professor_data[i, 1]],
                color='gray', linestyle='--', linewidth=1, alpha=0.5, zorder=1
            )
            
    # Evolution Lines
    if ui_config.var_evolucao.get() and phase == "pos":
        mds_pre = getattr(aluno, "mds_result_pre", None)
        if mds_pre is not None and mds_pre.X_aligned is not None:
            for i in range(num_concepts):
                ax.plot(
                    [mds_pre.X_aligned[i, 0], aluno_mds[i, 0]],
                    [mds_pre.X_aligned[i, 1], aluno_mds[i, 1]],
                    color='green', linestyle='-', linewidth=1.5, alpha=0.6, zorder=2
                )

    ax.set_title(f"MDS - Aluno {aluno.pid} ({phase.upper()})")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(limite)
    ax.set_ylim(limite)
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120)
    plt.close(fig)
    return buf.getvalue()


def gerar_imagem_media(data, phase, limite, ui_config, filtered_indices=None):
    alunos_all = data.alinhados.get(f"students_{phase}")
    
    if alunos_all is None: return None
    
    if filtered_indices is not None and len(filtered_indices) > 0:
        alunos = [alunos_all[i] for i in filtered_indices]
        alunos_centroid = np.mean(alunos, axis=0)
        aluno_std = np.std(alunos, axis=0)
    else:
        alunos = alunos_all
        alunos_centroid = data.centroids.get(f"students_{phase}")
        aluno_std = data.stds.get(f"students_{phase}")
        
    headers = data.headers
    professores_centroid = data.centroids.get("professors")
    opcao = ui_config.opt_media.get()

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    num_concepts = len(alunos_centroid)
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i % 20) for i in range(num_concepts)]

    # 1. Plotar Médias
    ax.scatter(alunos_centroid[:, 0], alunos_centroid[:, 1], c=colors, marker='o', label='Média Turma')
    plot_range = limite[1] - limite[0]
    proximity_threshold = 0.06 * plot_range
    placed_positions = []
    offsets = [
        (0.0, 0.12),    # Acima
        (0.0, -0.22),   # Abaixo
        (0.18, -0.05),  # Direita
        (-0.18, -0.05), # Esquerda
        (0.13, 0.13),   # Superior Direito
        (-0.13, -0.18), # Inferior Esquerdo
        (0.13, -0.18),  # Inferior Direito
        (-0.13, 0.13)   # Superior Esquerdo
    ]

    for i in range(num_concepts):
        generic_name = data.concept_mapping.get(headers[i], f"C{i+1}")
        x, y = alunos_centroid[i, 0], alunos_centroid[i, 1]
        
        collision_count = 0
        for px, py in placed_positions:
            if np.sqrt((x - px)**2 + (y - py)**2) < proximity_threshold:
                collision_count += 1
                
        offset_idx = collision_count % len(offsets)
        dx, dy = offsets[offset_idx]
        scaled_dx = dx * (plot_range / 10.0)
        scaled_dy = dy * (plot_range / 10.0)
        
        ax.text(
            x + scaled_dx,
            y + scaled_dy,
            generic_name,
            fontsize=9,
            fontweight='bold',
            color=colors[i],
            ha='center',
            va='center',
            zorder=4
        )
        placed_positions.append((x, y))

    if "dispersão" in str(opcao).lower() or opcao in ["3.2.2", "3.2.3", "3.2.5", "3.2.6"]:
        if alunos:
            for i, aluno in enumerate(alunos):
                ax.scatter(aluno[:, 0], aluno[:, 1], alpha=0.1, c=colors)

    if "elipse" in str(opcao).lower() or opcao in ["3.2.3", "3.2.6"]:
        from matplotlib.patches import Ellipse
        if aluno_std is not None:
            for i in range(num_concepts):
                e = Ellipse(xy=alunos_centroid[i], width=aluno_std[i, 0] * 4, height=aluno_std[i, 1] * 4,
                            edgecolor=colors[i], fc='none', linewidth=1.5, alpha=0.60)
                ax.add_patch(e)

    if opcao in ["3.2.4", "3.2.5", "3.2.6"] and professores_centroid is not None:
        ax.scatter(professores_centroid[:, 0], professores_centroid[:, 1], c=colors, marker='x', label='Professor')
        for i in range(num_concepts):
            ax.plot(
                [alunos_centroid[i, 0], professores_centroid[i, 0]],
                [alunos_centroid[i, 1], professores_centroid[i, 1]],
                color='gray', linestyle='--', linewidth=1, alpha=0.5, zorder=1
            )
            
    if ui_config.var_evolucao.get() and phase == "pos":
        pre_centroid = data.centroids.get("students_pre")
        if pre_centroid is not None:
            for i in range(num_concepts):
                ax.plot(
                    [pre_centroid[i, 0], alunos_centroid[i, 0]],
                    [pre_centroid[i, 1], alunos_centroid[i, 1]],
                    color='green', linestyle='-', linewidth=1.5, alpha=0.6, zorder=2
                )

    ax.set_title(f"Análise Coletiva - Média da Turma ({phase.upper()})")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(limite)
    ax.set_ylim(limite)
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    return buf.getvalue()