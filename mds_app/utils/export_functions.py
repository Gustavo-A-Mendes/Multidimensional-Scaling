import matplotlib.pyplot as plt
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


def exportar_tudo_para_zip(zip_path, data, ui_config, progress_callback=None):
    alunos = data.participants["students"]
    alunos_mean = data.mean["students"]
    alunos_centroid = data.centroids["students"]
    professores = data.participants["professors"]
    professores_mean = data.mean["professors"]
    professores_centroid = data.centroids["professors"]
    total_participant = professores + alunos

    headers = data.headers

    total_steps = 0

    if ui_config.var_matrizes.get():
        total_steps += 1

    if ui_config.var_coords.get():
        total_steps += 1

    if ui_config.var_plot_indiv.get():
        total_steps += len(alunos)

    if ui_config.var_plot_media.get():
        total_steps += 1

    current_step = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:

        # --- EXPORTAÇÃO DE MATRIZES ---
        if ui_config.var_matrizes.get():
            if progress_callback:
                progress_callback(current_step, total_steps, "Gerando matrizes...")

            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # info sheet:
                # create info dataframe:
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

                # Matriz Média Professores:
                df_media = pd.DataFrame(professores_mean, index=headers, columns=headers)
                df_media.to_excel(writer, sheet_name="Gabarito")

                # Matriz Média Turma:
                df_media = pd.DataFrame(alunos_mean, index=headers, columns=headers)
                df_media.to_excel(writer, sheet_name="Média_Turma")

                # Matrizes Individuais
                for participant in total_participant:
                    df = participant.dataframe
                    # Nome da aba limitado a 31 caracteres (regra do Excel)
                    if participant.group.upper() == "PROFESSOR":
                        nome = f"Professor_{participant.pid:02}"[:31]
                    elif participant.group.upper() == "ALUNO":
                        nome =  f"Aluno_{participant.pid:02}"[:31]
                    df.to_excel(writer, sheet_name=nome)

            zf.writestr("matrizes_dissimilaridade.xlsx", output.getvalue())

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        # --- EXPORTAÇÃO DE COORDENADAS ---
        if ui_config.var_coords.get():
            if progress_callback:
                progress_callback(current_step, total_steps, "Gerando coordenadas...")

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

                # Coordenada Média Professores
                df_media = pd.DataFrame(professores_centroid, index=headers, columns=['X', 'Y'])
                df_media.to_excel(writer, sheet_name="Gabarito")

                # Coordenada Média turma
                df_media = pd.DataFrame(alunos_centroid, index=headers, columns=['X', 'Y'])
                df_media.to_excel(writer, sheet_name="Média_Turma")

                # Matrizes Individuais
                for participant in total_participant:
                    df = pd.DataFrame(participant.mds_result.X_aligned, index=headers, columns=['X', 'Y'])
                    # Nome da aba limitado a 31 caracteres (regra do Excel)
                    if participant.group.upper() == "PROFESSOR":
                        nome = f"Professor_{participant.pid:02}"[:31]
                    elif participant.group.upper() == "ALUNO":
                        nome = f"Aluno_{participant.pid:02}"[:31]
                    df.to_excel(writer, sheet_name=nome)

            zf.writestr("coordenadas_mds.xlsx", output.getvalue())

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        limite = data.get_global_limits()
        # --- EXPORTAÇÃO DE PLOTS ---
        if ui_config.var_plot_indiv.get():
            if progress_callback:
                progress_callback(current_step, total_steps, f"Gerando gráfico de alunos...")

            for aluno in alunos:
                img_data = gerar_imagem_mds(aluno, professores_centroid, headers, limite, ui_config.var_gabarito_indiv.get())
                zf.writestr(f"plots_individuais/mds_{aluno.pid}.png", img_data)

                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps)

        if ui_config.var_plot_media.get():
            if progress_callback:
                progress_callback(current_step, total_steps, "Gerando média da turma...")

            img_media = gerar_imagem_media(data, limite, ui_config.opt_media.get())
            zf.writestr(f"plot_turma/mds_media_turma.png", img_media)

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)


def gerar_imagem_mds(aluno_data, professor_data, headers, limite, mostrar_gabarito):
    # Criamos a figura sem usar o pyplot.show() para não abrir janela
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    aluno_mds = aluno_data.mds_result.X_aligned
    num_concepts = len(aluno_mds)
    cmap = plt.get_cmap('tab10')

    # Criamos a lista de cores
    colors = [cmap(i % 10) for i in range(num_concepts)]

    # 1. Plotar os pontos do aluno (passando c=colors funciona se for lista de tuplas)
    ax.scatter(aluno_mds[:, 0], aluno_mds[:, 1], c=colors, marker='o', label='Aluno', zorder=3)

    # 2. CORREÇÃO DO TEXTO: Precisa ser um loop!
    for i in range(num_concepts):
        ax.text(
            aluno_mds[i, 0],
            aluno_mds[i, 1] + 0.10,  # Pequeno offset em Y
            headers[i],
            fontsize=9,
            fontweight='bold',
            color=colors[i],  # Cor específica deste conceito
            ha='center',
            va='bottom',
            zorder=4
        )

    if mostrar_gabarito:
        ax.scatter(professor_data[:, 0], professor_data[:, 1], c=colors, marker='x', label='Gabarito')

        # Desenhar linhas de conexão
        for i in range(num_concepts):
            ax.plot(
                [aluno_mds[i, 0], professor_data[i, 0]],
                [aluno_mds[i, 1], professor_data[i, 1]],
                color='gray', linestyle='--', linewidth=1, alpha=0.5, zorder=1
            )
        # Adicione aqui o loop das linhas de conexão se desejar

    ax.set_title(f"MDS - Aluno {aluno_data.pid}")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(limite)
    ax.set_ylim(limite)
    ax.legend()

    # Transforma o plot em bytes PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120)
    plt.close(fig)  # Limpeza de memória
    return buf.getvalue()


def gerar_imagem_media(data, limite, opcao):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    alunos = data.alinhados["students"]
    alunos_centroid = data.centroids["students"]
    headers = data.headers
    professores_centroid = data.centroids["professors"]
    aluno_std = data.stds["students"]
    num_concepts = len(alunos_centroid)
    cmap = plt.get_cmap('tab10')
    colors = [cmap(i % 10) for i in range(num_concepts)]

    # 1. Plotar Médias (Centroides)
    ax.scatter(alunos_centroid[:, 0], alunos_centroid[:, 1], c=colors, marker='o', label='Média Turma')
    for i in range(num_concepts):
        ax.text(
            alunos_centroid[i, 0],
            alunos_centroid[i, 1] + 0.10,  # Pequeno offset em Y
            headers[i],
            fontsize=9,
            fontweight='bold',
            color=colors[i],  # Cor específica deste conceito
            ha='center',
            va='bottom',
            zorder=4
        )

    # 2. Aplicar condicionais das sub-opções
    if "dispersão" in str(opcao).lower() or "3.2.2" in str(opcao).lower() or "3.2.3" in str(opcao).lower() or "3.2.5" in str(opcao).lower() or "3.2.6" in str(opcao).lower():
        # Loop para plotar todos os pontos de todos os alunos com alpha baixo
        for i, aluno in enumerate(alunos):
            ax.scatter(aluno[:, 0], aluno[:, 1], alpha=0.1, c=colors)

    if "elipse" in str(opcao).lower() or "3.2.3" in str(opcao).lower() or "3.2.6" in str(opcao).lower():
        # Lógica da elipse (multiplicador 4 que discutimos)
        from matplotlib.patches import Ellipse
        for i in range(len(data.headers)):
            e = Ellipse(xy=alunos_centroid[i], width=aluno_std[i, 0] * 4, height=aluno_std[i, 1] * 4,
                        edgecolor=colors[i], fc='none', linewidth=1.5, alpha=0.60)
            ax.add_patch(e)

    # 3. Adicionar Gabarito se solicitado (3.2.4 a 3.2.6)
    if opcao in ["3.2.4", "3.2.5", "3.2.6"]:
        ax.scatter(professores_centroid[:, 0], professores_centroid[:, 1], c=colors, marker='x', label='Professor')
        # Desenhar linhas de conexão
        for i in range(num_concepts):
            ax.plot(
                [alunos_centroid[i, 0], professores_centroid[i, 0]],
                [alunos_centroid[i, 1], professores_centroid[i, 1]],
                color='gray', linestyle='--', linewidth=1, alpha=0.5, zorder=1
            )
        # Adicione aqui o loop das linhas de conexão se desejar

    ax.set_title("Análise Coletiva - Média da Turma")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(limite)
    ax.set_ylim(limite)
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    return buf.getvalue()