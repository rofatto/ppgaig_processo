import streamlit as st
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos ou Pardos e Indígenas", 
                                            "Pessoas com Deficiência", 
                                            "Políticas Humanitárias"])

    identidade_pdf = st.file_uploader("Documento de identidade (com CPF ou CPF separado mesclado)", type="pdf")
    registro_civil_pdf = st.file_uploader("Registro civil (nascimento ou casamento)", type="pdf")
    quitacao_pdf = st.file_uploader("Comprovante de quitação eleitoral", type="pdf")

    reservista_pdf = None
    if sexo == "Masculino":
        reservista_pdf = st.file_uploader("Certificado de reservista", type="pdf")

    quota_pdf = None
    if quota != "Ampla Concorrência":
        quota_pdf = st.file_uploader("Comprovante para quotas", type="pdf")

# Seleção da Linha de Pesquisa
with aba2:
    st.header("Seleção da Linha de Pesquisa")
    email = st.text_input("Email")
    data_nascimento = st.date_input("Data de Nascimento")
    ano_conclusao = st.number_input("Ano de Conclusão", 1950, 2100)

    linha = st.radio("Selecione apenas 1 (uma) linha de pesquisa:", [
        "Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais",
        "Linha 2: Sistemas integrados de produção vegetal"
    ])

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
    ordem_pref = [st.number_input(sub, 1, len(subareas), key=f"sub_{sub}") for sub in subareas]

# Pontuação do Currículo
with aba3:
    st.header("Pontuação do Currículo")

    historico_media = st.number_input("Média das disciplinas", min_value=0.0, max_value=10.0, step=0.01)
    historico_pdf = st.file_uploader("Histórico Escolar (obrigatório)", type="pdf")

    data_curriculo = [
        ["Artigo percentil ≥ 75", 10.0, 0], ["Artigo 50 ≤ percentil < 75", 8.0, 0],
        ["Artigo 25 ≤ percentil < 50", 6.0, 12.0], ["Artigo percentil < 25", 2.0, 4.0],
    ]

    df_curriculo = pd.DataFrame(data_curriculo, columns=["Item", "Pontuação por Item", "Pontuação Máxima"])
    df_curriculo["Quantidade"] = [st.number_input(i, 0, 10, key=f"curriculo_{i}") for i in df_curriculo["Item"]]

# Gerar PDF Completo
if st.button("📥 Gerar PDF Completo"):
    merger = PdfMerger()

    buffer_inscricao = BytesIO()
    doc_inscricao = SimpleDocTemplate(buffer_inscricao, pagesize=A4)
    elements_inscricao = [Paragraph("Inscrição", getSampleStyleSheet()['Title'])]
    elements_inscricao += [Paragraph(f"Nome: {nome}"), Paragraph(f"CPF: {cpf}"), Paragraph(f"Sexo: {sexo}"),
                 Paragraph(f"Modalidade: {modalidade}"), Paragraph(f"Quota: {quota}")]
    doc_inscricao.build(elements_inscricao)
    merger.append(buffer_inscricao)

    for pdf in [identidade_pdf, registro_civil_pdf, quitacao_pdf, reservista_pdf, quota_pdf]:
        if pdf: merger.append(pdf)

    buffer_selecao = BytesIO()
    doc_selecao = SimpleDocTemplate(buffer_selecao, pagesize=A4)
    elements_selecao = [Paragraph("Seleção da Linha de Pesquisa", getSampleStyleSheet()['Title'])]
    elements_selecao += [Paragraph(f"Email: {email}"), Paragraph(f"Data de Nascimento: {data_nascimento}"), Paragraph(f"Ano de Conclusão: {ano_conclusao}"), Paragraph(f"Linha: {linha}")]
    tabela_selecao = [["Subárea", "Ordem"]] + list(zip(subareas, ordem_pref))
    elements_selecao.append(Table(tabela_selecao, style=[('GRID', (0,0), (-1,-1), 1, colors.black)]))
    doc_selecao.build(elements_selecao)
    merger.append(buffer_selecao)

    buffer_curriculo = BytesIO()
    doc_curriculo = SimpleDocTemplate(buffer_curriculo, pagesize=A4)
    elements_curriculo = [Paragraph("Pontuação do Currículo", getSampleStyleSheet()['Title'])]
    tabela = [["Item", "Quantidade"]] + df_curriculo[["Item", "Quantidade"]].values.tolist()
    elements_curriculo.append(Table(tabela, style=[('GRID', (0,0), (-1,-1), 1, colors.black)]))
    doc_curriculo.build(elements_curriculo)
    merger.append(buffer_curriculo)

    if historico_pdf: merger.append(historico_pdf)

    final_pdf = BytesIO()
    merger.write(final_pdf)
    merger.close()

    st.success("✅ PDF completo gerado!")
    st.download_button("⬇️ Baixar PDF", final_pdf.getvalue(), "inscricao_completa.pdf", "application/pdf")
