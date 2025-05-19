import streamlit as st
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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

    historico_media = st.number_input("Média das disciplinas", min_value=0.0, max_value=10.0, step=0.01)
    historico_pdf = st.file_uploader("Histórico Escolar (obrigatório)", type="pdf")

    data_curriculo = [
        ["Artigo percentil ≥ 75", 10.0, 0], ["Artigo 50 ≤ percentil < 75", 8.0, 0],
        ["Artigo 25 ≤ percentil < 50", 6.0, 12.0], ["Artigo percentil < 25", 2.0, 4.0],
    ]

    df_curriculo = pd.DataFrame(data_curriculo, columns=["Item", "Pontuação por Item", "Pontuação Máxima"])
    df_curriculo["Quantidade"] = [st.number_input(i, 0, 10, key=f"curriculo_{i}") for i in df_curriculo["Item"]]

# Geração do PDF Único
if st.button("📥 Gerar PDF Completo"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Inscrição
    elements.append(Paragraph("Inscrição", styles['Title']))
    elements.append(Spacer(1, 6))
    elements += [Paragraph(f"<b>Nome:</b> {nome}", styles['Normal']),
                 Paragraph(f"<b>CPF:</b> {cpf}", styles['Normal']),
                 Paragraph(f"<b>Sexo:</b> {sexo}", styles['Normal']),
                 Paragraph(f"<b>Modalidade:</b> {modalidade}", styles['Normal']),
                 Paragraph(f"<b>Quota:</b> {quota}", styles['Normal'])]

    elements.append(PageBreak())
    elements.append(Paragraph("Seleção da Linha de Pesquisa", styles['Title']))
    elements.append(Spacer(1, 6))
    elements += [Paragraph(f"<b>Email:</b> {email}", styles['Normal']),
                 Paragraph(f"<b>Data de Nascimento:</b> {data_nascimento.strftime('%d/%m/%Y')}", styles['Normal']),
                 Paragraph(f"<b>Ano de Conclusão:</b> {ano_conclusao}", styles['Normal']),
                 Paragraph(f"<b>Linha Selecionada:</b> {linha}", styles['Normal'])]

    tabela_selecao = [["Subárea", "Ordem"]] + list(zip(subareas, ordem_pref))
    table = Table(tabela_selecao, hAlign='LEFT', colWidths=[320, 60])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ]))
    elements.append(table)

    elements.append(PageBreak())
    elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
    elements.append(Spacer(1, 6))

    tabela_curriculo = [["Item", "Quantidade"]] + df_curriculo[["Item", "Quantidade"]].values.tolist()
    table2 = Table(tabela_curriculo, hAlign='LEFT', colWidths=[350, 50])
    table2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ]))
    elements.append(table2)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>Média do Histórico Escolar:</b> {historico_media:.2f}", styles['Normal']))

    doc.build(elements)

    st.success("✅ PDF completo gerado!")
    st.download_button("⬇️ Baixar PDF", buffer.getvalue(), "inscricao_completa.pdf", "application/pdf")
