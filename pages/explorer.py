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
    page_icon="🔍",
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

# --- UI HEADER ---
try:
    with open("assets/search.png", "rb") as f:
        search_encoded = base64.b64encode(f.read()).decode()
    header_html = f"""
    <div class="title-container">
        <img src="data:image/png;base64,{search_encoded}" class="title-icon-img">
        <h1 style="margin: 0;">Card Explorer</h1>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
except:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 20px;'>
            <h1 style='margin: 0;'>🔍 Card Explorer</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR (FILTROS) ---
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("### 🎛️ Filtros do Explorer")
    
    # Campo de Busca Global
    search_query = st.text_input("Buscar por nome ou descrição:", placeholder="Digite algo...")
    
    # Busca de dados básica
    board_data = trello_service.get_board_data(BOARD_ID)
    if not board_data:
        st.error("Erro ao carregar dados do Board.")
        st.stop()
        
    all_lists = {l['id']: l['name'] for l in board_data['lists']}
    all_members = {m['id']: m['fullName'] for m in board_data['members']}
    
    selected_lists = st.multiselect("Filtrar por Lista:", options=all_lists.values())
    selected_members = st.multiselect("Filtrar por Membro:", options=all_members.values())
    
    show_overdue_only = st.checkbox("Apenas Atrasados")
    
    if st.button("Limpar Filtros", use_container_width=True):
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

if selected_lists:
    df_cards = df_cards[df_cards['list_name'].isin(selected_lists)]

if selected_members:
    name_to_id = {v: k for k, v in all_members.items()}
    selected_ids = [name_to_id[name] for name in selected_members]
    df_cards = df_cards[df_cards['idMembers'].apply(lambda x: any(mid in selected_ids for mid in x))]

if show_overdue_only:
    now = datetime.now(timezone.utc)
    df_cards['due_date'] = pd.to_datetime(df_cards['due'], utc=True, errors='coerce')
    df_cards = df_cards[(df_cards['due_date'] < now) & (~df_cards['dueComplete'])]

# Atualizar contador no header
st.caption(f"Exibindo {len(df_cards)} cartões encontrados.")

# --- RENDER TABLE ---
# Callback para abrir o modal
def handle_card_click(card_id):
    # Busca detalhes extras (checklists, actions)
    with st.spinner("Carregando detalhes..."):
        card_details = trello_service.get_card_details(card_id)
        # Pega os dados básicos do card do dataframe original
        basic_data = df_cards[df_cards['id'] == card_id].iloc[0].to_dict()
        render_card_detail_dialog(basic_data, card_details)

render_explorer_table(df_cards, handle_card_click)

# --- BOTÃO VOLTAR ---
st.markdown("---")
if st.button("⬅️ Voltar para o Dashboard Principal"):
    st.switch_page("app.py")
