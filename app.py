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

    identidade_pdf = st.file_uploader("Documento de identidade (mesclado em um único PDF) *", type="pdf")
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

    data_nascimento = st.date_input("Data de Nascimento (ANO/MÊS/DIA)", value=date(1990, 1, 1))
    ano_conclusao = st.number_input("Ano de Conclusão do Curso de Graduação", 1950, 2100)

    linha = st.radio("Selecione a linha de pesquisa:", [
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
        ordem_pref.append((ordem, sub))

# Pontuação do Currículo
with aba3:
    st.header("Pontuação do Currículo")
    historico_media = st.number_input("Média aritmética das disciplinas cursadas:", min_value=0.0, max_value=10.0, step=0.01)
    historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

    itens = [
        ("1.1 Artigo com percentil ≥ 75", "10,00 pontos/artigo. Anexar o artigo completo.", 10.0, 0),
        ("1.2 Artigo com 50 ≤ percentil < 75", "8,00 pontos/artigo.", 8.0, 0),
        ("1.3 Artigo com 25 ≤ percentil < 50", "6,00 pontos/artigo. Máx: 12,00", 6.0, 12.0),
        ("1.4 Artigo com percentil < 25", "2,00 pontos/artigo. Máx: 4,00", 2.0, 4.0),
        ("1.5 Artigo sem percentil", "1,00 ponto/artigo. Máx: 2,00", 1.0, 2.0),
        ("2.1 Trabalhos completos em eventos (≥2p)", "0,6 ponto/unidade. Anexar trabalho completo.", 0.6, 3.0),
        ("2.2 Resumos publicados (<2p)", "0,3 ponto/unidade. Anexar certificado.", 0.3, 1.5),
        ("3.1 Capítulo de livro ou boletim técnico", "1,0 ponto/unidade.", 1.0, 4.0),
        ("3.2 Livro na íntegra", "4,0 pontos/unidade.", 4.0, 4.0),
        ("4. Curso de especialização", "1,0 ponto/unidade.", 1.0, 1.0),
        ("5. Monitoria de disciplina", "0,6 ponto por semestre.", 0.6, 2.4),
        ("6.1 Iniciação científica com bolsa", "0,4 ponto/mês.", 0.4, 16.0),
        ("6.2 Iniciação científica sem bolsa", "0,2 ponto/mês.", 0.2, 8.0),
        ("7.1 Software/Aplicativo", "1,0 ponto/unidade.", 1.0, 5.0),
        ("7.2 Patente", "1,0 ponto/unidade.", 1.0, 5.0),
        ("7.3 Registro de cultivar", "1,0 ponto/unidade.", 1.0, 5.0),
        ("8. Orientação de alunos", "1,0 ponto por orientação.", 1.0, 2.0),
        ("9. Participação em bancas", "0,25 ponto/unidade.", 0.25, 1.0),
        ("10.1 Docência no Ensino Superior", "1,0 ponto/semestre.", 1.0, 8.0),
        ("10.2 Docência no Fundamental/Médio", "0,3 ponto/semestre.", 0.3, 3.0),
        ("10.3 Atuação em EAD", "0,2 ponto/semestre.", 0.2, 2.0),
        ("10.4 Atividades profissionais relacionadas", "0,25 ponto/semestre.", 0.25, 4.0),
    ]

    comprovantes = {}
    dados = []

    for item, desc, ponto, maximo in itens:
        st.markdown(f"**{item}** — {desc}")
        qtd = st.number_input(f"Quantidade '{item}'", min_value=0, step=1)
        comprovantes[item] = st.file_uploader(f"Comprovante '{item}'", type="pdf", key=f"file_{item}")
        # Verificação obrigatória
        if qtd > 0 and comprovantes[item] is None:
            st.warning(f"Você preencheu o item '{item}' com quantidade {qtd}, mas não anexou o comprovante correspondente.")
        total = min(qtd * ponto, maximo) if maximo > 0 else qtd * ponto
        dados.append((item, qtd, total))

    pontuacao_total = sum(total for _, _, total in dados)

    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

    if st.button("📄 Gerar Relatório Final em PDF"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Seção: Inscrição e Linha de Pesquisa
        elements.append(Paragraph("Inscrição e Linha de Pesquisa", styles['Title']))
        elements += [
            Paragraph(f"<b>Nome:</b> {nome}", styles['Normal']),
            Paragraph(f"<b>CPF:</b> {cpf}", styles['Normal']),
            Paragraph(f"<b>Sexo:</b> {sexo}", styles['Normal']),
            Paragraph(f"<b>Modalidade:</b> {modalidade}", styles['Normal']),
            Paragraph(f"<b>Quota:</b> {quota}", styles['Normal']),
            Paragraph(f"<b>Email:</b> {email}", styles['Normal']),
            Paragraph(f"<b>Data de Nascimento:</b> {data_nascimento.strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"<b>Ano de Conclusão:</b> {ano_conclusao}", styles['Normal']),
            Paragraph(f"<b>Linha Selecionada:</b> {linha}", styles['Normal']),
            Spacer(1, 12),
            Paragraph("Subáreas selecionadas:", styles['Normal'])
        ]

        subareas_ordenadas = sorted(ordem_pref)
        for ordem, sub in subareas_ordenadas:
            elements.append(Paragraph(f"{ordem} - {sub}", styles['Normal']))

        elements.append(PageBreak())

        # Tabela de Pontuação
        elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
        table_data = [["Item", "Quantidade", "Total"]]
        for item, qtd, total in dados:
            table_data.append([item, str(qtd), f"{total:.2f}"])

        table = Table(table_data, colWidths=[200, 100, 100])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(1,1),(-1,-1),'CENTER')
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Média do Histórico Escolar:</b> {historico_media:.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Pontuação Total do Currículo:</b> {pontuacao_total:.2f}", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        merger = PdfMerger()
        merger.append(PdfReader(buffer))

        # Anexos
        for label, pdf_file in [
            ("Documento de identidade", identidade_pdf),
            ("Registro civil", registro_civil_pdf),
            ("Comprovante de quitação eleitoral", quitacao_pdf),
            ("Diploma ou Certificado", diploma_pdf),
            ("Certificado de reservista", reservista_pdf),
            ("Comprovante de quota", quota_pdf),
            ("Histórico Escolar", historico_pdf)
        ]:
            if pdf_file is not None:
                capa_buffer = BytesIO()
                capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
                capa_elements = [Spacer(1, 250), Paragraph(label, styles['Title'])]
                capa_doc.build(capa_elements)
                capa_buffer.seek(0)
                merger.append(PdfReader(capa_buffer))
                pdf_file.seek(0)
                merger.append(PdfReader(pdf_file))

        # Comprovantes de pontuação
        for item, qtd, _ in dados:
            if qtd > 0 and comprovantes[item] is not None:
                capa_buffer = BytesIO()
                capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
                capa_elements = [Spacer(1, 250), Paragraph(f"Comprovante: {item}", styles['Title'])]
                capa_doc.build(capa_elements)
                capa_buffer.seek(0)
                merger.append(PdfReader(capa_buffer))
                comprovantes[item].seek(0)
                merger.append(PdfReader(comprovantes[item]))

        final_output = BytesIO()
        merger.write(final_output)
        merger.close()

        st.success("✅ PDF gerado com sucesso!")
        st.download_button("⬇️ Baixar PDF Consolidado", final_output.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
