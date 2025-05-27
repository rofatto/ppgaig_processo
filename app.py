import streamlit as st
import pandas as pd
import json
from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Formulário PPGAIG", layout="wide")

# ➡️ Carregar progresso
uploaded_progress = st.file_uploader("📂 Carregar Progresso (JSON)", type="json")
if uploaded_progress:
    saved_data = json.load(uploaded_progress)
    st.session_state.update(saved_data)
    st.warning("⚠️ Progresso carregado! Por favor, **reenvie os arquivos PDF** antes de gerar o relatório.")

# Abas do formulário
aba1, aba2, aba3 = st.tabs(["Inscrição", "Seleção da Linha de Pesquisa", "Pontuação do Currículo"])

# Inscrição
with aba1:
    st.header("Inscrição")
    nome = st.text_input("Nome completo", st.session_state.get('nome', ''))
    cpf = st.text_input("CPF", st.session_state.get('cpf', ''))
    sexo = st.radio("Sexo", ["Masculino", "Feminino", "Prefiro não identificar"], index=["Masculino", "Feminino", "Prefiro não identificar"].index(st.session_state.get('sexo', "Masculino")))
    modalidade = st.radio("Modalidade", ["Regular", "Especial"], index=["Regular", "Especial"].index(st.session_state.get('modalidade', "Regular")))
    quota = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"], index=["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"].index(st.session_state.get('quota', "Ampla Concorrência")))
# Campo adicional: Candidato a bolsa
    if modalidade == "Regular":
    candidato_bolsa = st.radio(
        "Deseja concorrer à bolsa?",
        ["Sim", "Não"],
        index=["Sim", "Não"].index(st.session_state.get('candidato_bolsa', "Sim"))
    )
else:
    candidato_bolsa = "Não"  # Aluno especial não pode concorrer a bolsa
    st.session_state['candidato_bolsa'] = candidato_bolsa  # Garante que sempre fique "Não"

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
    email = st.text_input("Email", st.session_state.get('email', ''))
    from datetime import date
    data_nascimento = st.date_input("Data de Nascimento (ANO/MÊS/DIA)", value=pd.to_datetime(st.session_state.get('data_nascimento', '1990-01-01')), min_value=date(1900, 1, 1), max_value=date.today())
    ano_conclusao = st.number_input("Ano de Conclusão do Curso de Graduação", 1950, 2100, value=st.session_state.get('ano_conclusao', 2024))

    linha = st.radio("Selecione apenas 1 (uma) linha de pesquisa:", ["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"], index=["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"].index(st.session_state.get('linha', "Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais")))

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

    # ➡️ Carregar ordem das subáreas
    saved_ordem_list = st.session_state.get('ordem_pref', [])
    saved_ordem = {sub: ordem for ordem, sub in saved_ordem_list}
    
    ordem_pref = []
    ordem_usada = set()
    for sub in subareas:
        ordem = st.number_input(sub, 1, len(subareas), key=f"sub_{sub}", value=saved_ordem.get(sub, 1))
        if ordem in ordem_usada:
            st.warning(f"Ordem {ordem} já usada. Escolha uma ordem única para cada subárea.")
        ordem_usada.add(ordem)
        ordem_pref.append((ordem, sub))

# Pontuação do Currículo
with aba3:
    st.header("Pontuação do Currículo")
    st.markdown("📝 **Atenção:** Os comprovantes de um dado item devem ser enviados em **um único arquivo PDF**.")
    historico_media = st.number_input("Média aritmética das disciplinas cursadas na graduação (obrigatório):", min_value=0.01, max_value=10.0, step=0.01, format="%.2f", value=st.session_state.get('historico_media', 1.00))  # ou outro valor padrão
    historico_pdf = st.file_uploader("Anexe o Histórico Escolar (PDF obrigatório)", type="pdf", key="historico")

    itens = [
        ("1.1 Artigo com percentil ≥ 75", "10,00 pontos/artigo.", 10.0, 0),
        ("1.2 Artigo com 50 ≤ percentil < 75", "8,00 pontos/artigo.", 8.0, 0),
        ("1.3 Artigo com 25 ≤ percentil < 50", "6,00 pontos/artigo. Máx: 12,00 pontos.", 6.0, 12.0),
        ("1.4 Artigo com percentil < 25", "2,00 pontos/artigo. Máx: 4,00 pontos.", 2.0, 4.0),
        ("1.5 Artigo sem percentil", "1,00 ponto/artigo. Máx: 2,00 pontos.", 1.0, 2.0),
        ("2.1 Trabalhos completos em eventos (≥ 2 páginas)", "0,6 ponto/unidade. Máx: 3,0 pontos.", 0.6, 3.0),
        ("2.2 Resumos publicados (< 2 páginas)", "0,3 ponto/unidade. Máx: 1,5 pontos.", 0.3, 1.5),
        ("3.1 Capítulo de livro ou boletim técnico", "1,0 ponto/unidade. Máx: 4,0 pontos.", 1.0, 4.0),
        ("3.2 Livro na íntegra", "4,0 pontos/unidade. Máx: 4,0 pontos.", 4.0, 4.0),
        ("4. Curso de especialização", "1,0 ponto/unidade. Máx: 1,0 ponto.", 1.0, 1.0),
        ("5. Monitoria de disciplina", "0,6 ponto/semestre. Máx: 2,4 pontos.", 0.6, 2.4),
        ("6.1 Iniciação científica com bolsa", "0,4 ponto/mês. Máx: 16,0 pontos.", 0.4, 16.0),
        ("6.2 Iniciação científica sem bolsa", "0,2 ponto/mês. Máx: 8,0 pontos.", 0.2, 8.0),
        ("7.1 Software/Aplicativo", "1,0 ponto/unidade. Máx: 5,0 pontos.", 1.0, 5.0),
        ("7.2 Patente", "1,0 ponto/unidade. Máx: 5,0 pontos.", 1.0, 5.0),
        ("7.3 Registro de cultivar", "1,0 ponto/unidade. Máx: 5,0 pontos.", 1.0, 5.0),
        ("8. Orientação de alunos", "1,0 ponto por orientação. Máx: 2,0 pontos.", 1.0, 2.0),
        ("9. Participação em bancas", "0,25 ponto/unidade. Máx: 1,0 ponto.", 0.25, 1.0),
        ("10.1 Docência no Ensino Superior", "1,0 ponto/semestre. Máx: 8,0 pontos.", 1.0, 8.0),
        ("10.2 Docência no Fundamental/Médio", "0,3 ponto/semestre. Máx: 3,0 pontos.", 0.3, 3.0),
        ("10.3 Atuação em EAD", "0,2 ponto/semestre. Máx: 2,0 pontos.", 0.2, 2.0),
        ("10.4 Atividades profissionais relacionadas", "0,25 ponto/semestre. Máx: 4,0 pontos.", 0.25, 4.0)
    ]

    saved_pontuacao = st.session_state.get('pontuacao', {})
    
    comprovantes = {}
    dados = []

    for item, desc, ponto, maximo in itens:
        st.markdown(f"**{item}** — {desc}")
        qtd = st.number_input(f"Quantidade de '{item}'", min_value=0, step=1, value=saved_pontuacao.get(item, 0))
        comprovantes[item] = st.file_uploader(f"Anexe o comprovante único em PDF para '{item}'", type="pdf", key=f"file_{item}")
        if qtd > 0 and comprovantes[item] is None:
            st.warning(f"Preencheu '{item}' com quantidade {qtd}, mas não anexou o comprovante.")
        total = min(qtd * ponto, maximo) if maximo > 0 else qtd * ponto
        dados.append((item, qtd, total))

    pontuacao_total = sum(total for _, _, total in dados)

    st.subheader(f"📈 Pontuação Final: {pontuacao_total:.2f} pontos")

      # ✅ Botão salvar progresso COMPLETO
    save_data = {
        'nome': nome,
        'cpf': cpf,
        'sexo': sexo,
        'modalidade': modalidade,
        'quota': quota,
        'candidato_bolsa': candidato_bolsa,
        'email': email,
        'data_nascimento': str(data_nascimento),
        'ano_conclusao': ano_conclusao,
        'linha': linha,
        'ordem_pref': ordem_pref,
        'historico_media': historico_media,
        'pontuacao': {item: qtd for item, qtd, _ in dados}
    }

    b = BytesIO()
    b.write(json.dumps(save_data, indent=2, ensure_ascii=False).encode('utf-8'))
    st.download_button("💾 Salvar Progresso", b.getvalue(), "progresso_ppgaig.json", mime="application/json")


    # ✅ Validação das ordens antes do botão PDF
    ordens = [ordem for ordem, _ in ordem_pref]
    if len(ordens) != len(set(ordens)):
        st.error("❗ Há ordens repetidas nas subáreas! Por favor, atribua uma ordem única para cada subárea.")
    else:
        if st.button("📄 Gerar Relatório Final em PDF"):
            if not historico_pdf:
                st.error("❗ Histórico Escolar obrigatório não foi anexado.")
            elif not all([identidade_pdf, registro_civil_pdf, quitacao_pdf, diploma_pdf]):
                st.error("❗ Todos documentos obrigatórios da inscrição devem ser anexados.")
            else:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(Paragraph("Inscrição", styles['Title']))
                elements += [Paragraph(f"<b>{label}:</b> {valor}", styles['Normal']) for label, valor in [
                    ("Nome", nome), ("CPF", cpf), ("Sexo", sexo), ("Modalidade", modalidade), ("Quota", quota), ("Candidato à Bolsa", candidato_bolsa),
                    ("Email", email), ("Data de Nascimento", data_nascimento.strftime('%d/%m/%Y')),
                    ("Ano de Conclusão", ano_conclusao), ("Linha Selecionada", linha)
                ]]

                elements.append(Spacer(1, 12))
                elements.append(Paragraph("Subáreas Selecionadas", styles['Heading2']))
                subareas_tab = sorted(ordem_pref, key=lambda x: x[0])
                table_data = [["Ordem", "Subárea"]] + [
                    [ordem, Paragraph(sub, ParagraphStyle('subarea', fontSize=9))] for ordem, sub in subareas_tab
                ]
                table = Table(table_data, colWidths=[50, 400])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('WORDWRAP', (1, 1), (-1, -1), 'CJK'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                elements.append(table)
                elements.append(PageBreak())

                elements.append(Paragraph("Pontuação do Currículo", styles['Title']))
                table_data = [["Item", "Quantidade", "Total"]] + [
                    [Paragraph(item, ParagraphStyle('item', fontSize=8)), qtd, f"{total:.2f}"] for item, qtd, total in dados
                ]
                pont_table = Table(table_data, colWidths=[300, 70, 70])
                pont_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('WORDWRAP', (0, 1), (0, -1), 'CJK')
                ]))
                elements.append(pont_table)

                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Média do Histórico Escolar: {historico_media:.2f}", styles['Normal']))
                elements.append(Paragraph(f"Pontuação Total do Currículo: {pontuacao_total:.2f}", styles['Normal']))

                doc.build(elements)
                buffer.seek(0)
                merger = PdfMerger()
                merger.append(PdfReader(buffer))

                for label, pdf_file in [
                    ("Documento de identidade", identidade_pdf), ("Registro civil", registro_civil_pdf),
                    ("Comprovante de quitação eleitoral", quitacao_pdf), ("Diploma ou Certificado", diploma_pdf),
                    ("Certificado de reservista", reservista_pdf), ("Comprovante de quota", quota_pdf),
                    ("Histórico Escolar", historico_pdf)
                ]:
                    if pdf_file:
                        capa_buffer = BytesIO()
                        SimpleDocTemplate(capa_buffer, pagesize=A4).build(
                            [Spacer(1, 250), Paragraph(label, styles['Title'])]
                        )
                        capa_buffer.seek(0)
                        merger.append(PdfReader(capa_buffer))
                        pdf_file.seek(0)
                        merger.append(PdfReader(pdf_file))

                for item, qtd, _ in dados:
                    if qtd > 0 and comprovantes[item]:
                        capa_buffer = BytesIO()
                        SimpleDocTemplate(capa_buffer, pagesize=A4).build(
                            [Spacer(1, 250), Paragraph(f"Comprovante: {item}", styles['Title'])]
                        )
                        capa_buffer.seek(0)
                        merger.append(PdfReader(capa_buffer))
                        comprovantes[item].seek(0)
                        merger.append(PdfReader(comprovantes[item]))

                final_output = BytesIO()
                merger.write(final_output)
                merger.close()
                st.success("✅ PDF gerado com sucesso!")
                st.download_button("⬇️ Baixar PDF Consolidado", final_output.getvalue(), file_name="formulario_ppgaig.pdf", mime="application/pdf")
