import streamlit as st
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Formulário PPGAIG", layout="wide")

# Abas
aba1, aba2, aba3 = st.tabs(["Inscrição", "Seleção da Linha de Pesquisa", "Pontuação do Currículo"])

# Inscrição
with aba1:
    st.header("Inscrição")
    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    sexo = st.radio("Sexo", ["Masculino", "Feminino", "Prefiro não identificar"])
    modalidade = st.radio("Modalidade", ["Regular", "Especial"])
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"])

    identidade_pdf = st.file_uploader("Documento de identidade *", type="pdf")
    registro_civil_pdf = st.file_uploader("Registro civil *", type="pdf")
    quitacao_pdf = st.file_uploader("Comprovante de quitação eleitoral *", type="pdf")
    diploma_pdf = st.file_uploader("Diploma ou Certificado *", type="pdf")

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
    data_nascimento = st.date_input("Data de Nascimento", value=date(1990,1,1))
    ano_conclusao = st.number_input("Ano de Conclusão", 1950, 2100)

    linha = st.radio("Linha de Pesquisa:", ["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"])

    subareas_l1 = [
        "Sensoriamento Remoto de Sistemas Agrícolas",
        "Desenvolvimento de sistemas de mapeamento móvel. Utilização de aeronaves remotamente pilotadas na Fitotecnia",
        "Sistemas computacionais inteligentes na agricultura e informações geoespaciais",
        "Posicionamento por GNSS. Modelagem e análise de dados geoespaciais. Controle de qualidade de informações geoespaciais",
        "Sensores Aplicados a Agricultura de Precisão"
    ]
    subareas_l2 = [
        "Biotecnologia na agricultura", "Recursos florestais", "Nutrição, Manejo e cultura de tecidos em hortaliças e plantas medicinais",
        "Micologia Aplicada. Patologia Florestal. Patologia de Sementes. Sensoriamento remoto aplicado à Patologia Florestal",
        "Nutrição mineral e metabolismo de plantas", "Manejo integrado de plantas daninhas. Uso de herbicidas na Agricultura. Sistemas de informação para controle de plantas",
        "Microbiologia agrícola", "Controle biológico de doenças de plantas. Controle biológico de plantas daninhas. Sensoriamento remoto aplicado à Fitopatologia",
        "Mecanização agrícola. Tecnologia de aplicação de precisão", "Manejo da água em sistemas agrícolas irrigados",
        "Melhoramento genético de hortaliças e fenotipagem de alto desempenho", "Entomologia agrícola: manejo integrado, controle biológico, controle microbiano",
        "Tecnologias aplicadas à cafeicultura"
    ]
    subareas = subareas_l1 if "Linha 1" in linha else subareas_l2

    ordem_pref = []
    ordem_usada = set()
    for sub in subareas:
        ordem = st.number_input(sub, 1, len(subareas), key=f"sub_{sub}")
        if ordem in ordem_usada:
            st.warning(f"Ordem {ordem} já usada.")
        ordem_usada.add(ordem)
        ordem_pref.append((ordem, sub))

# Pontuação do Currículo
with aba3:
    st.header("Pontuação do Currículo")
    historico_media = st.number_input("Média do Histórico Escolar:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
    historico_pdf = st.file_uploader("Histórico Escolar (PDF obrigatório)", type="pdf")

    itens = [
        ("1.1 Artigo com percentil ≥ 75", "10,00 pts/art.", 10.0, 0),
        ("1.2 Artigo com 50 ≤ p < 75", "8,00 pts/art.", 8.0, 0),
        ("1.3 Artigo com 25 ≤ p < 50", "6,00 pts/art. Máx: 12,00 pts", 6.0, 12.0),
        ("1.4 Artigo com p < 25", "2,00 pts/art. Máx: 4,00 pts", 2.0, 4.0),
        ("1.5 Artigo sem percentil", "1,00 pt/art. Máx: 2,00 pts", 1.0, 2.0),
        ("2.1 Trabalhos completos", "0,6 pt/unid. Máx: 3,0 pts", 0.6, 3.0),
        ("2.2 Resumos publicados", "0,3 pt/unid. Máx: 1,5 pts", 0.3, 1.5),
        ("3.1 Capítulo de livro", "1,0 pt/unid. Máx: 4,0 pts", 1.0, 4.0),
        ("3.2 Livro na íntegra", "4,0 pts/unid. Máx: 4,0 pts", 4.0, 4.0),
        ("4. Curso de especialização", "1,0 pt/unid.", 1.0, 1.0),
        ("5. Monitoria", "0,6 pt/sem. Máx: 2,4 pts", 0.6, 2.4),
        ("6.1 Iniciação c/ bolsa", "0,4 pt/mês. Máx: 16,0 pts", 0.4, 16.0),
        ("6.2 Iniciação s/ bolsa", "0,2 pt/mês. Máx: 8,0 pts", 0.2, 8.0),
        ("7.1 Software", "1,0 pt/unid. Máx: 5,0 pts", 1.0, 5.0),
        ("7.2 Patente", "1,0 pt/unid. Máx: 5,0 pts", 1.0, 5.0),
        ("7.3 Cultivar", "1,0 pt/unid. Máx: 5,0 pts", 1.0, 5.0),
        ("8. Orientação", "1,0 pt/orient. Máx: 2,0 pts", 1.0, 2.0),
        ("9. Bancas", "0,25 pt/unid. Máx: 1,0 pt", 0.25, 1.0),
        ("10.1 Docência Sup.", "1,0 pt/sem. Máx: 8,0 pts", 1.0, 8.0),
        ("10.2 Docência Fund/Médio", "0,3 pt/sem. Máx: 3,0 pts", 0.3, 3.0),
        ("10.3 EAD", "0,2 pt/sem. Máx: 2,0 pts", 0.2, 2.0),
        ("10.4 Ativ. profissionais", "0,25 pt/sem. Máx: 4,0 pts", 0.25, 4.0)
    ]

    comprovantes = {}
    dados = []

    for item, desc, ponto, maximo in itens:
        st.markdown(f"**{item}** — {desc}")
        qtd = st.number_input(f"Quantidade '{item}'", min_value=0, step=1)
        comprovantes[item] = st.file_uploader(f"Comprovante '{item}'", type="pdf", key=f"file_{item}")
        total = min(qtd * ponto, maximo) if maximo > 0 else qtd * ponto
        dados.append((item, qtd, total))

    pontuacao_total = sum(total for _, _, total in dados)
    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

    if st.button("📄 Gerar Relatório Final em PDF"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Inscrição e Seleção", styles['Title']))
        elements += [
            Paragraph(f"<b>Nome:</b> {nome}", styles['Normal']),
            Paragraph(f"<b>CPF:</b> {cpf}", styles['Normal']),
            Paragraph(f"<b>Sexo:</b> {sexo}", styles['Normal']),
            Paragraph(f"<b>Modalidade:</b> {modalidade}", styles['Normal']),
            Paragraph(f"<b>Quota:</b> {quota}", styles['Normal']),
            Paragraph(f"<b>Email:</b> {email}", styles['Normal']),
            Paragraph(f"<b>Nascimento:</b> {data_nascimento.strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"<b>Conclusão:</b> {ano_conclusao}", styles['Normal']),
            Paragraph(f"<b>Linha:</b> {linha}", styles['Normal']),
            Spacer(1, 12),
            Paragraph("<b>Subáreas Selecionadas:</b>", styles['Heading2'])
        ]

        sub_data = [["Ordem", "Subárea"]]
        for ordem, sub in sorted(ordem_pref, key=lambda x: x[0]):
            sub_data.append([str(ordem), Paragraph(sub, ParagraphStyle(name='sub', fontSize=8))])

        sub_table = Table(sub_data, colWidths=[30, 450])
        sub_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black), ('FONTSIZE', (0,0), (-1,-1), 8)]))
        elements.append(KeepTogether(sub_table))
        elements.append(PageBreak())

        elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
        pont_data = [["Item", "Qtd", "Total"]]
        for item, qtd, total in dados:
            pont_data.append([item, str(qtd), f"{total:.2f}"])

        pont_table = Table(pont_data, colWidths=[250, 50, 70])
        pont_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black), ('FONTSIZE', (0,0), (-1,-1), 8)]))
        elements.append(KeepTogether(pont_table))

        elements.append(Spacer(1,12))
        elements.append(Paragraph(f"<b>Média do Histórico:</b> {historico_media:.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Pontuação Total:</b> {pontuacao_total:.2f}", styles['Normal']))

        doc.build(elements)

        buffer.seek(0)
        merger = PdfMerger()
        merger.append(PdfReader(buffer))
        final_output = BytesIO()
        merger.write(final_output)
        merger.close()

        st.success("✅ PDF gerado com sucesso!")
        st.download_button("⬇️ Baixar PDF Consolidado", final_output.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
