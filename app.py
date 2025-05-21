import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Formulário PPGAIG", layout="wide")

# Abas do formulário
aba1, aba2, aba3 = st.tabs(["Inscrição", "Seleção da Linha de Pesquisa", "Pontuação do Currículo"])

# Código das abas permanece igual até aqui...

# Após a subheader da Pontuação Final
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

    subarea_table = Table(
        [["Ordem", "Subárea selecionada"]] +
        [[str(i + 1), Paragraph(sub, styles['Normal'])] for i, (_, sub) in enumerate(sorted(zip(ordem_pref, subareas)))],
        colWidths=[40, 380],
        hAlign='LEFT')
    subarea_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))
    elements.append(Spacer(1, 12))
    elements.append(subarea_table)

    elements.append(PageBreak())

    # Seção 3: Pontuação do Currículo
    elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
    elements.append(Spacer(1, 12))
    pont_table = Table(
        [["Item", "Quantidade"]] + [[item, qtd] for item, qtd in dados if qtd > 0],
        colWidths=[350, 100]
    )
    pont_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)
    ]))
    elements.append(pont_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Média do Histórico Escolar:</b> {historico_media:.2f}", styles['Normal']))
    elements.append(Paragraph(f"<b>Pontuação Total do Currículo:</b> {pontuacao_total:.2f} pontos", styles['Normal']))

    doc.build(elements)

    # Agora mesclar anexos usando PyPDF2
    buffer.seek(0)
    merger = PdfMerger()
    merger.append(PdfReader(buffer))

    # Documentos de inscrição
    for label, pdf_file in [
        ("Documento de identidade", identidade_pdf),
        ("Registro civil", registro_civil_pdf),
        ("Comprovante de quitação eleitoral", quitacao_pdf),
        ("Diploma ou Certificado", diploma_pdf),
        ("Certificado de reservista", reservista_pdf),
        ("Comprovante de quota", quota_pdf)
    ]:
        if pdf_file is not None:
            capa_buffer = BytesIO()
            capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
            capa_elements = [Spacer(1, 250), Paragraph(label, styles['Title'])]
            capa_doc.build(capa_elements)
            capa_buffer.seek(0)
            merger.append(PdfReader(capa_buffer))
            merger.append(PdfReader(BytesIO(pdf_file.read())))

    # Histórico Escolar
    if historico_pdf is not None:
        capa_buffer = BytesIO()
        capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
        capa_elements = [Spacer(1, 250), Paragraph("Histórico Escolar", styles['Title'])]
        capa_doc.build(capa_elements)
        capa_buffer.seek(0)
        merger.append(PdfReader(capa_buffer))
        historico_pdf.seek(0)
        merger.append(PdfReader(historico_pdf))

    # Comprovantes da pontuação
    for item, qtd in dados:
        if qtd > 0 and comprovantes[item] is not None:
            capa_buffer = BytesIO()
            capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
            capa_elements = [Spacer(1, 250), Paragraph(f"Comprovante: {item}", styles['Title'])]
            capa_doc.build(capa_elements)
            capa_buffer.seek(0)
            merger.append(PdfReader(capa_buffer))
            merger.append(PdfReader(BytesIO(comprovantes[item].read())))

    final_output = BytesIO()
    merger.write(final_output)
    merger.close()

    st.success("✅ PDF gerado com sucesso!")
    st.download_button("⬇️ Baixar PDF Consolidado", final_output.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
