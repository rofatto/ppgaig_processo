import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Formulário PPGAIG", layout="wide")

# Abas do formulário
aba1, aba2, aba3 = st.tabs(["Inscrição", "Seleção da Linha de Pesquisa", "Pontuação do Currículo"])

# Inscrição
with aba1:
    st.header("Inscrição")
    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    sexo = st.radio("Sexo", ["Masculino", "Feminino", "Prefiro não identificar"])
    modalidade = st.radio("Modalidade", ["Regular", "Especial"])
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos, Pardos, Indígenas", 
                                            "Pessoas com Deficiência", 
                                            "Pessoas sob políticas humanitárias no Brasil"])

    identidade_pdf = st.file_uploader("Documento de identidade (com CPF ou RG e CPF separados, mas mesclados em um único PDF) *", type="pdf")
    registro_civil_pdf = st.file_uploader("Registro civil (nascimento ou casamento) *", type="pdf")
    quitacao_pdf = st.file_uploader("Comprovante de quitação eleitoral *", type="pdf")
    diploma_pdf = st.file_uploader("Diploma ou Certificado de Conclusão da Graduação *", type="pdf")

    reservista_pdf = None
    if sexo == "Masculino":
        reservista_pdf = st.file_uploader("Certificado de reservista *", type="pdf")

    quota_pdf = None
    if quota != "Ampla Concorrência":
        quota_pdf = st.file_uploader("Comprovante para quotas *", type="pdf")

# Seleção da Linha de Pesquisa
with aba2:
    st.header("Seleção da Linha de Pesquisa")
    email = st.text_input("Email")
    from datetime import date

    data_nascimento = st.date_input("Data de Nascimento (ANO/MÊS/DIA)", value=date(1990, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
    ano_conclusao = st.number_input("Ano de Conclusão do Curso de Graduação", 1950, 2100)

    linha = st.radio("Selecione apenas 1 (uma) linha de pesquisa:", [
        "Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais",
        "Linha 2: Sistemas integrados de produção vegetal"
    ])

    st.markdown("""
    📝 **Classifique as subáreas por ordem de preferência:**
    - Utilize os botões “+” e “–” para atribuir uma ordem de **1 (maior interesse)** a **5 (menor interesse)** – *caso tenha selecionado a Linha 1*.
    - Caso tenha selecionado a Linha 2, a ordem vai de **1 (maior interesse) a 13 (menor interesse)**.
    - Cada número de ordem só pode ser usado uma vez.
    """)
    subareas_l1 = [
        "Sensoriamento Remoto de Sistemas Agrícolas",
        "Desenvolvimento de sistemas de mapeamento móvel. Utilização de aeronaves remotamente pilotadas na Fitotecnia",
        "Sistemas computacionais inteligentes na agricultura e informações geoespaciais",
        "Posicionamento por GNSS. Modelagem e análise de dados geoespaciais. Controle de qualidade de informações geoespaciais",
        "Sensores Aplicados a Agricultura de Precisão"
    ]

    subareas_l2 = [
        "Biotecnologia na agricultura",
        "Recursos florestais",
        "Nutrição, Manejo e cultura de tecidos em hortaliças e plantas medicinais",
        "Micologia Aplicada. Patologia Florestal. Patologia de Sementes. Sensoriamento remoto aplicado à Patologia Florestal",
        "Nutrição mineral e metabolismo de plantas",
        "Manejo integrado de plantas daninhas. Uso de herbicidas na Agricultura. Sistemas de informação para controle de plantas",
        "Microbiologia agrícola",
        "Controle biológico de doenças de plantas. Controle biológico de plantas daninhas. Sensoriamento remoto aplicado à Fitopatologia",
        "Mecanização agrícola. Tecnologia de aplicação de precisão",
        "Manejo da água em sistemas agrícolas irrigados",
        "Melhoramento genético de hortaliças e fenotipagem de alto desempenho",
        "Entomologia agrícola: manejo integrado, controle biológico, controle microbiano",
        "Tecnologias aplicadas à cafeicultura"
    ]

    subareas = subareas_l1 if "Linha 1" in linha else subareas_l2

    ordem_pref = []
    ordem_usada = set()
    for sub in subareas:
        ordem = st.number_input(sub, 1, len(subareas), key=f"sub_{sub}")
        if ordem in ordem_usada:
            st.warning(f"Ordem {ordem} já usada. Escolha uma ordem única para cada subárea.")
        ordem_usada.add(ordem)
        ordem_pref.append(ordem)

# Pontuação do Currículo
with aba3:
    st.header("Pontuação do Currículo")

    st.markdown("📝 **Atenção:** Os comprovantes de um dado item devem ser enviados em **um único arquivo PDF**. Por exemplo, se você tem dois artigos referentes ao item 1.1, estes devem ser mesclados em **um único arquivo PDF** a ser enviado para o item 1.1.")
    st.markdown("### Histórico Escolar do(a) Candidato(a)")
    historico_media = st.number_input("Média aritmética das disciplinas cursadas na graduação:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
    historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

    # Lista detalhada de itens com instruções específicas para cada um
    itens = [
        ("1.1 Artigo com percentil ≥ 75", "Informar a quantidade de artigos. Pontuação: 10,00 pontos/artigo. Anexar o artigo completo com nome dos autores, periódico, ano, volume, número e páginas. Artigos em prelo ou first view não são aceitos."),
        ("1.2 Artigo com 50 ≤ percentil < 75", "Informar a quantidade de artigos. Pontuação: 8,00 pontos/artigo."),
        ("1.3 Artigo com 25 ≤ percentil < 50", "Informar a quantidade de artigos. Pontuação: 6,00 pontos/artigo. Pontuação máxima: 12,00 pontos."),
        ("1.4 Artigo com percentil < 25", "Informar a quantidade de artigos. Pontuação: 2,00 pontos/artigo. Pontuação máxima: 4,00 pontos."),
        ("1.5 Artigo sem percentil", "Informar a quantidade de artigos. Pontuação: 1,00 ponto/artigo. Pontuação máxima: 2,00 pontos."),
        ("2.1 Trabalhos completos em eventos (≥2p)", "Informar a quantidade. Pontuação: 0,6 ponto/unidade. Anexar trabalho, nome do evento, ano, título, autores e numeração das páginas."),
        ("2.2 Resumos publicados (<2p)", "Informar a quantidade. Pontuação: 0,3 ponto/unidade. Anexar certificado de apresentação."),
        ("3.1 Capítulo de livro ou boletim técnico", "Informar a quantidade. Pontuação: 1,0 ponto/unidade. Anexar capa, ficha catalográfica, autores, ano e páginas."),
        ("3.2 Livro na íntegra", "Informar a quantidade. Pontuação: 4,0 pontos/unidade. Anexar os mesmos elementos do item anterior."),
        ("4. Curso de especialização", "Informar a quantidade. Pontuação: 1,0 ponto/unidade. Curso com no mínimo 320h nas áreas de Ciências Agrárias ou Geociências. Anexar certificado contendo instituição, nome do curso, carga horária e ano de conclusão."),
        ("5. Monitoria de disciplina", "Informar a quantidade. Pontuação: 0,6 ponto por semestre letivo (mínimo 2 meses). Anexar comprovante com período e ano, emitido pela Pró-reitoria ou órgão equivalente."),
        ("6.1 Iniciação científica com bolsa", "Informar a quantidade de meses. Pontuação: 0,4 ponto/mês. Anexar comprovante com período e ano, emitido por Pró-reitoria ou agência de fomento."),
        ("6.2 Iniciação científica sem bolsa", "Informar a quantidade de meses. Pontuação: 0,2 ponto/mês. Mesma orientação de comprovação do item anterior."),
        ("7.1 Software/Aplicativo", "Informar a quantidade. Pontuação: 1,0 ponto/unidade. Anexar registro no INPI."),
        ("7.2 Patente", "Informar a quantidade. Pontuação: 1,0 ponto/unidade. Anexar registro no INPI."),
        ("7.3 Registro de cultivar", "Informar a quantidade. Pontuação: 1,0 ponto/unidade. Anexar registro no MAPA."),
        ("8. Orientação de alunos", "Informar a quantidade. Pontuação: 1,0 ponto por orientação concluída. Anexar formalização da orientação ou carta do coordenador de curso."),
        ("9. Participação em bancas", "Informar a quantidade. Pontuação: 0,25 ponto/unidade. Anexar comprovação da composição da banca, título do trabalho e ano da defesa."),
        ("10.1 Docência no Ensino Superior", "Informar a quantidade de semestres. Pontuação: 1,0 ponto/semestre. Anexar certificado ou registro em carteira de trabalho."),
        ("10.2 Docência no Fundamental/Médio", "Informar a quantidade de semestres. Pontuação: 0,3 ponto/semestre."),
        ("10.3 Atuação em EAD", "Informar a quantidade de semestres. Pontuação: 0,2 ponto/semestre."),
        ("10.4 Atividades profissionais relacionadas", "Informar a quantidade de semestres. Pontuação: 0,25 ponto/semestre. Não serão pontuadas atividades de estágio. Anexar certificado ou registro em carteira de trabalho.")
    ]

    dados = []
    comprovantes = {}

    for item, descricao in itens:
        st.markdown(f"**{item}**")
        st.markdown(f"ℹ️ {descricao}")
        qtd = st.number_input(f"Quantidade de '{item}'", min_value=0, step=1)
        comprovantes[item] = st.file_uploader(f"Anexe o comprovante único em PDF para '{item}'", type="pdf", key=f"file_{item}")
        dados.append((item, qtd))

    pontuacao_total = 0
    for item, qtd in dados:
        st.write(f"{item}: {qtd} unidades")

    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")
