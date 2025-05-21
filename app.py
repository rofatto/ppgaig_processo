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
        ordem_pref.append(ordem)

    if ordem_pref:
        st.subheader("Tabela de Preferência das Subáreas")
        pref_table = pd.DataFrame({"Subárea": subareas, "Preferência": ordem_pref})
        pref_table = pref_table.sort_values("Preferência")
        st.table(pref_table)

# ABA 3 - PONTUAÇÃO DO CURRÍCULO
with aba3:
    st.header("Pontuação do Currículo")
    st.markdown("📝 **Atenção:** Os comprovantes de um dado item devem ser enviados em **um único arquivo PDF**. Por exemplo, se você tem dois artigos referentes ao item 1.1, estes devem ser mesclados em **um único arquivo PDF** a ser enviado para o item 1.1.")

    historico_media = st.number_input("Média aritmética das disciplinas cursadas na graduação:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f")
    historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

    itens = [
        ("1.1 Artigo com percentil ≥ 75", 10.0, 0, "Anexar o artigo completo com nome dos autores, periódico, ano, volume, número e páginas."),
        ("1.2 Artigo com 50 ≤ percentil < 75", 8.0, 0, "Anexar o artigo completo."),
        ("1.3 Artigo com 25 ≤ percentil < 50", 6.0, 12.0, "Pontuação máxima: 12,00 pontos."),
        ("1.4 Artigo com percentil < 25", 2.0, 4.0, "Pontuação máxima: 4,00 pontos."),
        ("1.5 Artigo sem percentil", 1.0, 2.0, "Pontuação máxima: 2,00 pontos."),
        ("2.1 Trabalhos completos em eventos (≥2p)", 0.6, 3.0, "Anexar trabalho completo com identificação do evento."),
        ("2.2 Resumos publicados (<2p)", 0.3, 1.5, "Anexar certificado de apresentação."),
        ("3.1 Capítulo de livro ou boletim técnico", 1.0, 4.0, "Anexar capa, ficha catalográfica e conteúdo."),
        ("3.2 Livro na íntegra", 4.0, 4.0, "Anexar capa, ficha catalográfica e conteúdo."),
        ("4. Curso de especialização", 1.0, 1.0, "Anexar certificado contendo instituição, curso e carga horária."),
        ("5. Monitoria de disciplina", 0.6, 2.4, "Anexar comprovante com período e ano."),
        ("6.1 Iniciação científica com bolsa", 0.4, 16.0, "Anexar comprovante com período e ano."),
        ("6.2 Iniciação científica sem bolsa", 0.2, 8.0, "Anexar comprovante com período e ano."),
        ("7.1 Software/Aplicativo", 1.0, 5.0, "Anexar registro no INPI."),
        ("7.2 Patente", 1.0, 5.0, "Anexar registro no INPI."),
        ("7.3 Registro de cultivar", 1.0, 5.0, "Anexar registro no MAPA."),
        ("8. Orientação de alunos", 1.0, 2.0, "Anexar formalização da orientação."),
        ("9. Participação em bancas", 0.25, 1.0, "Anexar comprovação da composição da banca."),
        ("10.1 Docência no Ensino Superior", 1.0, 8.0, "Anexar certificado ou registro em carteira."),
        ("10.2 Docência no Fundamental/Médio", 0.3, 3.0, "Anexar certificado ou registro."),
        ("10.3 Atuação em EAD", 0.2, 2.0, "Anexar certificado ou registro."),
        ("10.4 Atividades profissionais relacionadas", 0.25, 4.0, "Anexar certificado ou registro.")
    ]

    comprovantes = {}
    resultados = []

    for item, ponto, maximo, instrucao in itens:
        st.markdown(f"**{item}**")
        st.markdown(f"ℹ️ {instrucao}")
        max_qtd = int(maximo / ponto) if maximo else 999
        qtd = st.number_input(f"Quantidade de '{item}'", min_value=0, max_value=max_qtd, step=1, key=f"qtd_{item}")
        comprovante = st.file_uploader(f"Anexe o comprovante único em PDF para '{item}'", type="pdf", key=f"file_{item}")
        comprovantes[item] = comprovante
        resultados.append((item, ponto, qtd))

    pontuacao_total = sum(p * q for _, p, q in resultados)
    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

    if st.button("📄 Gerar Relatório Final em PDF"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Relatório de Inscrição", styles['Title']))
        elements.append(Spacer(1, 12))
        elements += [
            Paragraph(f"Nome: {nome}", styles['Normal']),
            Paragraph(f"CPF: {cpf}", styles['Normal']),
            Paragraph(f"Sexo: {sexo}", styles['Normal']),
            Paragraph(f"Modalidade: {modalidade}", styles['Normal']),
            Paragraph(f"Quota: {quota}", styles['Normal']),
            Paragraph(f"Email: {email}", styles['Normal']),
            Paragraph(f"Data de Nascimento: {data_nascimento.strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"Ano de Conclusão: {ano_conclusao}", styles['Normal']),
            Paragraph(f"Linha Selecionada: {linha}", styles['Normal']),
        ]

        elements.append(PageBreak())

        elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
        data_table = [["Item", "Quantidade", "Pontuação"]] + [[item, str(qtd), f"{ponto*qtd:.2f}"] for item, ponto, qtd in resultados if qtd > 0]
        table = Table(data_table, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (1,1), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(table)
        elements.append(Paragraph(f"Média do Histórico Escolar: {historico_media:.2f}", styles['Normal']))
        elements.append(Paragraph(f"Pontuação Total: {pontuacao_total:.2f} pontos", styles['Normal']))

        doc.build(elements)

        buffer.seek(0)
        merger = PdfMerger()
        merger.append(PdfReader(buffer))

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
                merger.append(PdfReader(pdf_file))

        for item, _, qtd in resultados:
            if qtd > 0 and comprovantes[item] is not None:
                capa_buffer = BytesIO()
                capa_doc = SimpleDocTemplate(capa_buffer, pagesize=A4)
                capa_elements = [Spacer(1, 250), Paragraph(f"Comprovante: {item}", styles['Title'])]
                capa_doc.build(capa_elements)
                capa_buffer.seek(0)
                merger.append(PdfReader(capa_buffer))
                merger.append(PdfReader(comprovantes[item]))

        final_output = BytesIO()
        merger.write(final_output)
        merger.close()

        st.success("✅ PDF gerado com sucesso!")
        st.download_button("⬇️ Baixar PDF Consolidado", final_output.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
