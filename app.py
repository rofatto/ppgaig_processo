import streamlit as st
import pandas as pd
from io import BytesIO
import json
from PyPDF2 import PdfMerger, PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Formulário PPGAIG", layout="wide")

# Carregar progresso
uploaded_json = st.file_uploader("📤 Carregar Progresso (.json)", type="json")
if uploaded_json:
    st.session_state.form_data = json.load(uploaded_json)
    st.success("✅ Progresso carregado com sucesso!")
else:
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

form_data = st.session_state.form_data

# Abas
aba1, aba2, aba3 = st.tabs(["Inscrição", "Seleção da Linha de Pesquisa", "Pontuação do Currículo"])

# Inscrição
with aba1:
    st.header("Inscrição")
    form_data['nome'] = st.text_input("Nome completo", form_data.get('nome', ''))
    form_data['cpf'] = st.text_input("CPF", form_data.get('cpf', ''))
    form_data['sexo'] = st.radio("Sexo", ["Masculino", "Feminino", "Prefiro não identificar"], index=["Masculino", "Feminino", "Prefiro não identificar"].index(form_data.get('sexo', "Masculino")))
    form_data['modalidade'] = st.radio("Modalidade", ["Regular", "Especial"], index=["Regular", "Especial"].index(form_data.get('modalidade', "Regular")))
    form_data['quota'] = st.selectbox("Tipo de Quota", ["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"], index=["Ampla Concorrência", "Pretos, Pardos, Indígenas", "Pessoas com Deficiência", "Pessoas sob políticas humanitárias no Brasil"].index(form_data.get('quota', "Ampla Concorrência")))

# Seleção da Linha de Pesquisa
with aba2:
    st.header("Seleção da Linha de Pesquisa")
    form_data['email'] = st.text_input("Email", form_data.get('email', ''))
    from datetime import date
    default_date = pd.to_datetime(form_data.get('data_nascimento', '1990-01-01')).date()
    form_data['data_nascimento'] = st.date_input("Data de Nascimento (ANO/MÊS/DIA)", value=default_date, min_value=date(1900,1,1), max_value=date.today()).strftime('%Y-%m-%d')
    form_data['ano_conclusao'] = st.number_input("Ano de Conclusão do Curso de Graduação", 1950, 2100, int(form_data.get('ano_conclusao', 2024)))

    form_data['linha'] = st.radio("Selecione apenas 1 (uma) linha de pesquisa:", ["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"], index=["Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais", "Linha 2: Sistemas integrados de produção vegetal"].index(form_data.get('linha', "Linha 1: Desenvolvimento e aplicações de métodos em informações geoespaciais")))

    st.markdown("""
    📝 **Classifique as subáreas por ordem de preferência:**  
    - Linha 1: 1 a 5.  
    - Linha 2: 1 a 13.  
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

    subareas = subareas_l1 if "Linha 1" in form_data['linha'] else subareas_l2

    form_data['ordem_pref'] = []
    for i, sub in enumerate(subareas):
        ordem_key = f"sub_{sub}"
        form_data[ordem_key] = st.number_input(f"{sub}", 1, len(subareas), int(form_data.get(ordem_key, i+1)))
        form_data['ordem_pref'].append((form_data[ordem_key], sub))

# Pontuação
with aba3:
    st.header("Pontuação do Currículo")
    form_data['historico_media'] = st.number_input("Média aritmética das disciplinas cursadas na graduação:", min_value=0.0, max_value=10.0, step=0.01, format="%.2f", value=float(form_data.get('historico_media', 7.0)))

# Salvar progresso
json_data = json.dumps(form_data)
st.download_button("💾 Salvar Progresso", json_data, file_name="formulario_progresso.json", mime="application/json")
