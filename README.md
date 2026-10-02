# Escalonamento Multidimensional (MDS) - Ferramentas Cognitivas

Este repositório contém um conjunto de ferramentas integradas para coleta, modelagem e análise de dados cognitivos utilizando **Escalonamento Multidimensional (Multidimensional Scaling - MDS)**. Ele foi desenvolvido com o objetivo de apoiar a pesquisa e avaliação educacional por meio de mapas conceituais e dissimilaridades.

O repositório é composto por dois aplicativos principais:

1.  **`formGenerator_app`**: Gerador automático de questionários no Google Forms via API do Google Cloud para coleta par a par de dissimilaridades.
2.  **`mds_app`**: Analisador estatístico desktop para projeção 2D das distâncias conceituais, cálculo de Stress de Kruskal, alinhamento de turmas e avaliação de evolução cognitiva (Pré vs Pós-teste).

---

## 📂 Estrutura do Repositório

```text
Multidimensional-Scaling/
├── formGenerator_app/       # Gerador de Formulários Google (Coleta)
│   ├── app/                 # Código-fonte da interface e serviços Google
│   ├── credentials/         # Diretório para credenciais da API do Google
│   └── README.md            # Documentação e guia de uso do gerador
├── mds_app/                 # Analisador MDS Desktop (Análise e Modelagem)
│   ├── analysis/            # Motores de cálculo MDS e métricas
│   ├── ui/                  # Telas e janelas de visualização (Tkinter/tksheet)
│   └── README.md            # Documentação e guia de uso do analisador
├── requirements.txt         # Dependências compartilhadas do Python
└── README.md                # Esta documentação geral do repositório
```

---

## 🛠️ Visão Geral dos Projetos

### 1. Gerador de Formulários (`formGenerator_app`)
Projetado para automatizar a criação manual de dezenas ou centenas de perguntas de escala linear para comparações par a par.
*   **Como funciona**: A partir de uma lista de conceitos digitada pelo usuário, o app gera todas as combinações matemáticas possíveis de pares de conceitos, cria dois formulários espelhados (Pré-aulas e Pós-aulas), divide as questões em seções dinâmicas para evitar a fadiga do respondente e envia tudo direto para a conta Google do usuário logado via autenticação OAuth2.
*   👉 Para mais detalhes sobre configuração do Google Cloud e instruções passo a passo, veja o [README do Gerador de Formulários](formGenerator_app/README.md).

### 2. Analisador MDS Desktop (`mds_app`)
Responsável pelo processamento estatístico dos dados coletados, permitindo uma representação espacial 2D interativa da estrutura cognitiva dos participantes.
*   **Como funciona**:
    *   *Análise de Grupo*: Importa dados de turmas e professores, calcula o centróide docente, ordena os alunos segundo sua proximidade/alinhamento com os professores e traça trajetórias individuais de evolução conceitual entre as fases de pré e pós-teste.
    *   *Matriz Única*: Fornece uma planilha eletrônica interativa (`tksheet`) com células de entrada inteligentes e triângulo superior travado automaticamente para entrada rápida e individual de dados com plotagem em tempo real.
*   👉 Para compreender as métricas de Kruskal Stress e regras de uso das ferramentas de visualização, consulte o [README do Analisador MDS](mds_app/README.md).

---

## 🚀 Como Executar o Repositório Localmente

### Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado no computador.

### Passo 1: Instalação das Dependências
Abra o prompt de comando ou terminal na pasta raiz deste repositório e execute:
```bash
pip install -r requirements.txt
```

### Passo 2: Executar os Aplicativos

*   **Para executar o Gerador de Formulários**:
    ```bash
    python formGenerator_app/run_form_generator.py
    ```
    *(Nota: É necessário inserir o arquivo `credentials.json` gerado no console do Google Cloud na pasta `formGenerator_app/credentials/` antes do primeiro uso)*.

*   **Para executar o Analisador MDS**:
    ```bash
    python -m mds_app.run
    ```

---

## 📦 Empacotamento / Compilação (.exe)
Ambos os aplicativos podem ser compilados de forma independente em arquivos executáveis para Windows utilizando o **PyInstaller**. Os comandos e especificações estão detalhados em seus respectivos arquivos README internos.
