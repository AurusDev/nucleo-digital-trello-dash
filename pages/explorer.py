import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timezone
from src.services.trello_service import TrelloService
from src.ui.styles import apply_custom_styles
from src.ui.components import render_explorer_table, render_card_detail_dialog

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Explorer | Núcleo Digital",
    page_icon="assets/pie-chart.png",
    layout="wide"
)
apply_custom_styles()

# --- INITIALIZATION ---
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.getenv("TRELLO_API_KEY")
if "token" not in st.session_state:
    st.session_state["token"] = os.getenv("TRELLO_TOKEN")

trello_service = TrelloService(st.session_state["api_key"], st.session_state["token"])
BOARD_ID = os.getenv("TRELLO_BOARD_ID")
# --- SIDEBAR (CONFIGURATIONS) ---
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    
    # Carregando ícones da sidebar
    try:
        def get_b64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        
        icon_settings = get_b64("assets/settings.png")
        icon_cloud = get_b64("assets/cloud.png")
        icon_back = get_b64("assets/back.png")
    except:
        icon_settings = icon_cloud = icon_back = ""

    # Header Configurações
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <img src="data:image/png;base64,{icon_settings}" style="width: 24px; height: 24px;">
        <span style="font-weight: 700; font-size: 1.1rem; color: #fff;">Configurações</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão Sincronizar (com ícone injetado via CSS ou próximo)
    # Como st.button não aceita img, vamos usar uma gambiarra elegante de colunas ou apenas o label limpo
    # Para Antigravity, vamos usar um container com o ícone flutuante ou apenas markdown se preferir.
    # Vou usar colunas dentro do sidebar para alinhar o ícone ao lado do botão ou simplesmente no label.
    # Mas o usuário quer NO botão. Vou usar a técnica de markdown + CSS para os botões da sidebar.
    
    if st.button("Sincronizar Agora", use_container_width=True, help="Recarrega dados do Trello"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    
    if st.button("Painel Principal", use_container_width=True):
        st.switch_page("app.py")

    # Injeção de CSS para colocar os ícones nos botões da sidebar
    st.markdown(f"""
    <style>
        /* Sincronizar Agora */
        section[data-testid="stSidebar"] button[kind="secondary"]:nth-of-type(1) div[data-testid="stMarkdownContainer"] p::before {{
            content: "";
            background-image: url('data:image/png;base64,{icon_cloud}');
            background-size: contain;
            background-repeat: no-repeat;
            display: inline-block;
            width: 16px;
            height: 16px;
            margin-right: 10px;
            vertical-align: middle;
        }}
        /* Painel Principal */
        section[data-testid="stSidebar"] button[kind="secondary"]:nth-of-type(2) div[data-testid="stMarkdownContainer"] p::before {{
            content: "";
            background-image: url('data:image/png;base64,{icon_back}');
            background-size: contain;
            background-repeat: no-repeat;
            display: inline-block;
            width: 16px;
            height: 16px;
            margin-right: 10px;
            vertical-align: middle;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- UI HEADER ---
try:
    with open("assets/search.png", "rb") as f:
        search_encoded = base64.b64encode(f.read()).decode()
    header_html = f"""
    <div class="title-container" style="margin-bottom: 10px;">
        <img src="data:image/png;base64,{search_encoded}" class="title-icon-img">
        <h1 style="margin: 0;">Card Explorer</h1>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
except:
    st.markdown("<h1>🔍 Card Explorer</h1>", unsafe_allow_html=True)

# --- FILTROS EM LINHA ---
c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
with c_f1:
    search_query = st.text_input("", placeholder="🔍 Buscar por nome ou descrição...", label_visibility="collapsed")

# Busca de dados
board_data = trello_service.get_board_data(BOARD_ID)
if not board_data:
    st.error("Erro ao carregar dados do Board.")
    st.stop()

all_lists = {l['id']: l['name'] for l in board_data['lists']}
all_members = {m['id']: m['fullName'] for m in board_data['members']}

with st.expander("🎛️ Filtros Avançados & Ordenação", expanded=False):
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        sel_lists = st.multiselect("Listas:", options=all_lists.values())
    with col_e2:
        sel_members = st.multiselect("Responsáveis:", options=all_members.values())
    with col_e3:
        sort_by = st.selectbox("Ordenar por:", ["Última Atividade", "Nome (A-Z)", "Prazo"])

    col_e4, col_e5, col_e6 = st.columns(3)
    with col_e4:
        only_overdue = st.checkbox("Apenas Atrasados")
    with col_e5:
        if st.button("Limpar Todos os Filtros", use_container_width=True):
            st.rerun()

# --- DATA PROCESSING ---
df_cards = pd.DataFrame(board_data['cards'])
df_cards['list_name'] = df_cards['idList'].map(all_lists)

# Aplicar Filtros
if search_query:
    df_cards = df_cards[
        df_cards['name'].str.contains(search_query, case=False, na=False) |
        df_cards['desc'].str.contains(search_query, case=False, na=False)
    ]

if sel_lists:
    df_cards = df_cards[df_cards['list_name'].isin(sel_lists)]

if sel_members:
    name_to_id = {v: k for k, v in all_members.items()}
    selected_ids = [name_to_id[name] for name in sel_members]
    df_cards = df_cards[df_cards['idMembers'].apply(lambda x: any(mid in selected_ids for mid in x))]

if only_overdue:
    now = datetime.now(timezone.utc)
    df_cards['due_date'] = pd.to_datetime(df_cards['due'], utc=True, errors='coerce')
    df_cards = df_cards[(df_cards['due_date'] < now) & (~df_cards['dueComplete'])]

# Ordenação
if sort_by == "Nome (A-Z)":
    df_cards = df_cards.sort_values("name")
elif sort_by == "Prazo":
    df_cards = df_cards.sort_values("due", na_position='last')
else:
    df_cards = df_cards.sort_values("dateLastActivity", ascending=False)

# --- PAGINAÇÃO ---
ITEMS_PER_PAGE = 20
total_items = len(df_cards)
num_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)

# Resumo de busca
st.markdown(f"<small style='color:#777'>Exibindo <b>{len(df_cards)}</b> cartões</small>", unsafe_allow_html=True)

# --- RENDER TABLE ---
# Callback para abrir o modal
def handle_card_click(card_id):
    # Busca detalhes extras (checklists, actions)
    with st.spinner("Carregando detalhes..."):
        card_details = trello_service.get_card_details(card_id)
        # Pega os dados básicos do card do dataframe original
        basic_data = df_cards[df_cards['id'] == card_id].iloc[0].to_dict()
        render_card_detail_dialog(basic_data, card_details)

if total_items > 0:
    # Sidebar paginação (ou footer)
    page_col1, page_col2 = st.columns([1, 1])
    with page_col2:
        current_page = st.number_input("Página", min_value=1, max_value=max(1, num_pages), step=1, label_visibility="collapsed")
    
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    render_explorer_table(df_cards.iloc[start_idx:end_idx], handle_card_click)
else:
    st.info("Nenhum card corresponde aos critérios selecionados.")
