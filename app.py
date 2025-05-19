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
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos ou Pardos e Indígenas", 
                                            "Pessoas com Deficiência", 
                                            "Políticas Humanitárias"])

    identidade_pdf = st.file_uploader("Documento de identidade (com CPF ou RG e CPF mesclados em um único PDF) *", type="pdf")
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

    data = [
        ["1.1 Artigo com percentil ≥ 75", 10.0, 0],
        ["1.2 Artigo com 50 ≤ percentil < 75", 8.0, 0],
        ["1.3 Artigo com 25 ≤ percentil < 50", 6.0, 12.0],
        ["1.4 Artigo com percentil < 25", 2.0, 4.0],
        ["1.5 Artigo sem percentil", 1.0, 2.0],
        ["2.1 Trabalhos completos em eventos (≥2p)", 0.6, 3.0],
        ["2.2 Resumos publicados (<2p)", 0.3, 1.5],
        ["3.1 Capítulo de livro ou boletim técnico", 1.0, 4.0],
        ["3.2 Livro na íntegra", 4.0, 4.0],
        ["4. Curso de especialização (min 320h)", 1.0, 1.0],
        ["5. Monitoria de disciplina", 0.6, 2.4],
        ["6.1 Iniciação científica com bolsa", 0.4, 16.0],
        ["6.2 Iniciação científica sem bolsa", 0.2, 8.0],
        ["7.1 Software/Aplicativo (INPI)", 1.0, 5.0],
        ["7.2 Patente (INPI)", 1.0, 5.0],
        ["7.3 Registro de cultivar (MAPA)", 1.0, 5.0],
        ["8. Orientação de alunos (IC/TCC/extensão)", 1.0, 2.0],
        ["9. Participação em bancas (TCC/especialização)", 0.25, 1.0],
        ["10.1 Docência no Ensino Superior", 1.0, 8.0],
        ["10.2 Docência no Fundamental/Médio", 0.3, 3.0],
        ["10.3 Atuação em EAD", 0.2, 2.0],
        ["10.4 Atividades profissionais relacionadas", 0.25, 4.0],
    ]

    df = pd.DataFrame(data, columns=["Item", "Pontuação por Item", "Pontuação Máxima"])
    df["Quantidade"] = 0
    df["Total"] = 0.0
    comprovantes = {}

    for i in range(len(df)):
        item = df.at[i, "Item"]
        ponto = df.at[i, "Pontuação por Item"]
        maximo = df.at[i, "Pontuação Máxima"]
        if maximo > 0:
            max_qtd = round(maximo / ponto)
        else:
            max_qtd = 999
        col1, col2 = st.columns([3, 2])
        with col1:
            df.at[i, "Quantidade"] = st.number_input(f"{item}", min_value=0, max_value=max_qtd, step=1, key=f"qtd_{i}")
        with col2:
            comprovantes[item] = st.file_uploader(f"Comprovante único em PDF de '{item}'", type="pdf", key=f"file_{i}")

    for i in range(len(df)):
        if df.at[i, "Quantidade"] > 0 and comprovantes[df.at[i, "Item"]] is None:
            st.warning(f"Você preencheu o item '{df.at[i, 'Item']}', mas não anexou o comprovante correspondente. Isso é obrigatório.")

    df["Total"] = df["Quantidade"] * df["Pontuação por Item"]
    pontuacao_total = df["Total"].sum()
    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

    if st.button("📄 Gerar Relatório Final em PDF"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elements = []

        # Seção 1: Inscrição
        elements.append(Paragraph("Inscrição", styles['Title']))
        elements.append(Spacer(1, 12))
        elements += [
            Paragraph(f"<b>Nome:</b> {nome}", styles['Normal']),
            Paragraph(f"<b>CPF:</b> {cpf}", styles['Normal']),
            Paragraph(f"<b>Sexo:</b> {sexo}", styles['Normal']),
            Paragraph(f"<b>Modalidade:</b> {modalidade}", styles['Normal']),
            Paragraph(f"<b>Quota:</b> {quota}", styles['Normal']),
        ]

        elements.append(PageBreak())

        # Seção 2: Linha de Pesquisa
        elements.append(Paragraph("Seleção da Linha de Pesquisa", styles['Title']))
        elements.append(Spacer(1, 12))
        elements += [
            Paragraph(f"<b>Email:</b> {email}", styles['Normal']),
            Paragraph(f"<b>Data de Nascimento:</b> {data_nascimento.strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"<b>Ano de Conclusão:</b> {ano_conclusao}", styles['Normal']),
            Paragraph(f"<b>Linha Selecionada:</b> {linha}", styles['Normal']),
        ]
        subarea_table = Table([["Subárea", "Ordem"]] + list(zip(subareas, ordem_pref)), colWidths=[440, 60])
        subarea_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (1,1), (-1,-1), 'CENTER')
        ]))
        elements.append(Spacer(1, 12))
        elements.append(subarea_table)

        elements.append(PageBreak())

        # Seção 3: Pontuação
        elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
        elements.append(Spacer(1, 12))
        pont_table = Table(
            [["Item", "Quantidade", "Total"]] + df[df["Quantidade"] > 0][["Item", "Quantidade", "Total"]].values.tolist(),
            colWidths=[350, 70, 70]
        )
        pont_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke)
        ]))
        elements.append(pont_table)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Média do Histórico Escolar:</b> {historico_media:.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Pontuação Total do Currículo:</b> {pontuacao_total:.2f} pontos", styles['Normal']))

        doc.build(elements)
        st.success("✅ PDF gerado com sucesso!")
        st.download_button("⬇️ Baixar PDF Consolidado", buffer.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
