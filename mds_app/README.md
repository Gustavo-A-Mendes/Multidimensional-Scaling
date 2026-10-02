# Analisador MDS Educacional (mds_app)

Este aplicativo desktop desenvolvido em Python realiza a análise de **Escalonamento Multidimensional (Multidimensional Scaling - MDS)** de matrizes de dissimilaridade cognitivas (mapas conceituais). Ele permite avaliar o alinhamento de aprendizagem entre alunos e professores por meio de análises geométricas de grupo ou individuais.

---

## 📌 Sumário

- [🔍 Como o Programa Funciona](#-como-o-programa-funciona)
  - [1. O que é Escalonamento Multidimensional (MDS)?](#1-o-que-é-escalonamento-multidimensional-mds)
  - [2. O que é o Stress-1 (Kruskal)?](#2-o-que-é-o-stress-1-kruskal)
  - [3. Critério de Classificação e Métrica de Alinhamento](#3-critério-de-classificação-e-métrica-de-alinhamento)
- [📖 Modo de Análise de Grupo](#-modo-de-análise-de-grupo)
  - [Funcionalidades de Visualização do Painel](#funcionalidades-de-visualização-do-painel)
  - [Como Usar (Passo a Passo)](#como-usar-passo-a-passo)
- [📖 Modo de Análise de Matriz Única](#-modo-de-análise-de-matriz-única)
  - [Planilha Interativa (tksheet)](#planilha-interativa-tksheet)
  - [Como Usar (Passo a Passo)](#como-usar-passo-a-passo-1)
- [🛠️ Guia do Desenvolvedor](#%EF%B8%8F-guia-do-desenvolvedor)
  - [📋 Pré-requisitos](#-pré-requisitos)
  - [🚀 Executando Localmente](#-executando-localmente)
  - [📦 Compilando para um Executável (.exe)](#-compilando-para-um-executável-exe)

---

## 🔍 Como o Programa Funciona

O programa converte dados numéricos de proximidade conceitual (matrizes de correlação/distância) em coordenadas espaciais bidimensionais, plotando-os de forma geométrica para revelar a estrutura mental dos participantes.

### 1. O que é Escalonamento Multidimensional (MDS)?
O MDS é um conjunto de técnicas estatísticas de visualização de dados de similaridade ou dissimilaridade. O algoritmo recebe como entrada a distância entre $N$ conceitos e tenta encontrar uma representação em baixa dimensão (2D) onde a distância geométrica (euclidiana) entre os pontos no gráfico corresponda o mais fielmente possível às dissimilaridades originais.

### 2. O que é o Stress-1 (Kruskal)?
O valor de **Stress** é um indicador de qualidade de projeção que mede a discrepância matemática entre as distâncias originais (em alta dimensão) e as distâncias projetadas em 2D.
- **Stress < 0.10**: Excelente projeção, o gráfico é altamente confiável.
- **Stress entre 0.10 e 0.20**: Projeção aceitável, com distorções toleráveis.
- **Stress > 0.20**: Projeção fraca, o que indica que os conceitos têm relações complexas que não se adaptam bem a apenas 2 dimensões.

### 3. Critério de Classificação e Métrica de Alinhamento
No modo de Grupo, o sistema calcula a distância de cada aluno em relação ao centróide dos professores (mapa de referência/gabarito).
- **Distância (Alinhamento)**: Soma das distâncias euclidianas das coordenadas dos conceitos do aluno em relação ao gabarito do professor. Quanto menor a distância, mais alinhado cognitivamente o aluno está com o professor.
- **Evolução**: Diferença entre a distância no Pré-teste e no Pós-teste ($\text{Distância}_{\text{pré}} - \text{Distância}_{\text{pós}}$). Um valor positivo (ex: `+3.15`) indica aproximação dos conceitos em relação aos professores (ganho de aprendizagem).

---

## 📖 Modo de Análise de Grupo

O modo de **Análise de Grupo** é projetado para cruzar e comparar dados coletados de múltiplos respondentes (geralmente alunos e professores).

### Funcionalidades de Visualização do Painel
*   **Filtros de Ranking (Treeview)**: Exibe a lista ordenada de estudantes segundo critérios analíticos:
    *   *Todos os Alunos*: Lista completa com a ordem original de importação.
    *   *Top Alinhados*: Mostra apenas os $N$ alunos com a menor distância geométrica (maior convergência de conceitos) em relação aos professores.
    *   *Top Divergentes*: Mostra os $N$ alunos com a maior distância em relação aos professores.
    *   *Top Evolução*: Mostra os $N$ alunos que mais se aproximaram conceitualmente dos professores entre o pré e o pós-teste.
*   **Exibição das Métricas**: A coluna **Metrica** da tabela exibe dinamicamente o valor calculado da *Distância* ou *Evolução* de cada respondente.
*   **Controles Gráficos**:
    *   *Destaque*: Destaca o participante selecionado na tabela com cores fortes no gráfico MDS.
    *   *Média Alunos/Professores*: Plota os centróides da turma e do corpo docente para comparação macro.
    *   *Elipse de Dispersão*: Desenha uma elipse que delimita a dispersão espacial padrão (desvio-padrão) dos conceitos da turma.
    *   *Exibir Evolução*: Desenha linhas que ligam a posição pré-teste e pós-teste de cada conceito para o aluno selecionado, ilustrando a trajetória cognitiva dele.
    *   *Visibilidade de Conceitos*: Checkboxes para isolar a visualização de conceitos específicos e remover ruídos do gráfico.

### Como Usar (Passo a Passo)
1.  Selecione **Análise de Grupo** na barra de ferramentas superior.
2.  Clique em **Importar Dados**. No diálogo modal, escolha **Pré-teste** e selecione o arquivo CSV exportado (com colunas correspondentes aos conceitos e linhas por participante).
3.  Após a carga, o programa perguntará automaticamente se deseja importar os dados de **Pós-teste**. Se tiver, clique em "Sim" e carregue o arquivo de pós-teste correspondente.
4.  O gráfico de visualização gerará os pontos.
5.  Use a barra lateral esquerda (Treeview) para selecionar alunos e visualizar os dados e trajetória de evolução individualmente no gráfico 2D.
6.  Clique em **Exportar Resultados** na barra de ferramentas superior para salvar os gráficos gerados e os dados calculados de stress e distância em formato de imagem e planilha Excel.

---

## 📖 Modo de Análise de Matriz Única

O modo de **Análise de Matriz Única** serve para analisar dados de um único indivíduo de forma rápida, sendo ideal para modelagem teórica ou testes rápidos.

### Planilha Interativa (tksheet)
Esta ferramenta embutida na aba **Dados** simula o funcionamento de uma planilha eletrônica tradicional, facilitando o preenchimento de matrizes de dissimilaridade:
- **Diagonal Principal Travada**: A diagonal principal é fixada em `0` e colorida em cinza, pois a distância de um conceito para ele mesmo é nula.
- **Triângulo Superior Somente Leitura**: Como a matriz de dissimilaridade é simétrica (a distância entre A e B é igual à distância entre B e A), o programa trava o triângulo superior como somente leitura e copia automaticamente o valor inserido no triângulo inferior para a sua posição correspondente.
- **Navegação Otimizada**: Ao apertar `Enter` ou `Tab` na célula, o cursor se move pulando automaticamente as células travadas de somente leitura.
- **Copiar e Colar**: Suporta as teclas de atalho padrão do sistema para copiar e colar dados.

### Como Usar (Passo a Passo)
1.  Selecione **Análise de Matriz Única** na barra de ferramentas superior.
2.  Para carregar dados prontos: Clique em **Importar Matriz** e selecione o arquivo CSV da sua matriz de dissimilaridade.
3.  Para preencher manualmente: Clique em **Criar Nova Matriz** na barra lateral. Digite o número de conceitos (de 2 a 50) e defina seus nomes. Uma planilha em branco será gerada na aba **Dados**.
4.  Insira os valores na planilha. O gráfico na aba **MDS view** se atualizará dinamicamente em tempo real à medida que você insere os dados.

---

## 🛠️ Guia do Desenvolvedor

### 📋 Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado no seu sistema. As dependências primárias são:
```text
numpy
scipy
pandas
matplotlib
tksheet
```

### 🚀 Executando Localmente
Abra o terminal na pasta raiz do repositório (onde o `requirements.txt` está localizado) e instale as dependências:
```bash
pip install -r requirements.txt
```
Em seguida, execute o programa principal localizado em `mds_app/run.py`:
```bash
python -m mds_app.run
```

### 📦 Compilando para um Executável (.exe)
O projeto pode ser empacotado em um executável independente que roda no Windows sem necessidade do Python instalado. Para fazer a compilação utilizando o PyInstaller, execute:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "mds_app;mds_app" mds_app/run.py
```
O executável compilado será gerado na pasta `dist/run/run.exe`.
