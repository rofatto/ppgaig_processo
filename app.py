import streamlit as st
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
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
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"])

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

    linha = st.radio("Selecione apenas 1 (uma) linha de pesquisa:", ["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"])

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
        ordem_pref.append((ordem, sub))

    if ordem_pref:
        st.subheader("Tabela de Preferência das Subáreas")
        pref_table = pd.DataFrame(sorted(ordem_pref), columns=["Preferência", "Subárea"])
        st.table(pref_table)

# ABA 3 - PONTUAÇÃO DO CURRÍCULO
with aba3:
    st.header("Pontuação do Currículo")
    st.markdown("📝 **Atenção:** Os comprovantes de um dado item devem ser enviados em **um único arquivo PDF**. Por exemplo, se você tem dois artigos referentes ao item 1.1, estes devem ser mesclados em **um único arquivo PDF** a ser enviado para o item 1.1.")

    historico_media = st.number_input("Média aritmética das disciplinas cursadas na graduação:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
    historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

    st.write("\n🚧 A geração completa do relatório PDF consolidado e a mesclagem dos comprovantes será implementada conforme a estrutura validada anteriormente, incluindo validação de anexos obrigatórios, cálculo de totais e criação do arquivo final para download.")
