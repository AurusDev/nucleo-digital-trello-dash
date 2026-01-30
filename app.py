import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone, timedelta
import os
from src.services.trello_service import TrelloService
from src.ui.styles import apply_custom_styles
import base64
# Force Reload v2
from src.ui.components import render_kpi_card_new, render_plotly_bar, render_plotly_pie, render_insight_card
from src.insights import generate_insights

# --- CONFIGURAÇÃO INICIAL ---
# Force Reload Fix
st.set_page_config(page_title="Núcleo Digital | Projetos & Cases", page_icon="assets/favicon.png", layout="wide", initial_sidebar_state="expanded")
apply_custom_styles()

# --- SERVICES ---
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.getenv("TRELLO_API_KEY")
if "token" not in st.session_state:
    st.session_state["token"] = os.getenv("TRELLO_TOKEN")

trello_service = TrelloService(st.session_state["api_key"], st.session_state["token"])
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

# --- SIDEBAR (FILTROS & CONFIG) ---
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("### 🎛️ Filtros Avançados")
    
    if not trello_service.validate_auth():
        st.warning("⚠️ Autenticação incompleta")
        
        api_key_input = st.text_input("API Key", value=st.session_state["api_key"] or "", type="password")
        token_input = st.text_input("Token", value=st.session_state["token"] or "", type="password")
        
        if st.button("Conectar"):
            trello_service.api_key = api_key_input
            trello_service.token = token_input
            
            if trello_service.validate_auth():
                 st.session_state["api_key"] = api_key_input
                 st.session_state["token"] = token_input
                 st.success("Conectado! Recarregando...")
                 st.rerun()
            else:
                 st.error("Credenciais inválidas")
        st.stop()

    # Load Data
    board_data = trello_service.get_board_data(BOARD_ID)
    if not board_data:
        st.stop()

    # Prepare Filter Options
    all_members = {m['id']: m['fullName'] for m in board_data['members']}
    all_lists = {l['id']: l['name'] for l in board_data['lists']}
    
    # Filters
    selected_lists = st.multiselect("Filtrar por Lista:", options=all_lists.values(), default=[l for l in all_lists.values() if "Backlog" not in l])
    selected_members = st.multiselect("Filtrar por Membro:", options=all_members.values())
    
    st.divider()
    
    # Botão de refresh com ícone customizado (arrow.png)
    import base64
    try:
        with open("assets/arrow.png", "rb") as f:
            arrow_b64 = base64.b64encode(f.read()).decode()
            
        st.markdown(f"""
        <style>
        /* Estiliza o botão APENAS na sidebar para incluir o ícone */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        section[data-testid="stSidebar"] div[data-testid="stButton"] button::before {{
            content: "";
            width: 18px;
            height: 18px;
            background-image: url("data:image/png;base64,{arrow_b64}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            filter: brightness(0) invert(1); /* Garante ícone branco */
            opacity: 0.9;
        }}
        </style>
        """, unsafe_allow_html=True)
    except:
        pass
    
    if st.button("Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    if st.button("🔍 Abrir Card Explorer", use_container_width=True, help="Exploração detalhada de cartões com busca e filtros"):
        st.switch_page("pages/explorer.py")

# --- DATA PROCESSING ---
df_cards = pd.DataFrame(board_data['cards'])
df_cards['list_name'] = df_cards['idList'].map(all_lists)

# Fetch Actions (Needed for Throughput AND Insights)
actions = trello_service.get_actions(BOARD_ID)

# Filter Logic
if selected_lists:
    df_cards_filtered = df_cards[df_cards['list_name'].isin(selected_lists)]
else:
    df_cards_filtered = df_cards # If nothing selected (or default), show all? sidebar default handles it.

if selected_members:
    name_to_id = {v: k for k, v in all_members.items()}
    selected_ids = [name_to_id[name] for name in selected_members]
    df_cards_filtered = df_cards_filtered[df_cards_filtered['idMembers'].apply(lambda x: any(mid in selected_ids for mid in x))]

# KPI Data
total_cards = len(df_cards_filtered)
wip_count = df_cards_filtered[~df_cards_filtered['list_name'].str.contains('Done|Concluído|Backlog|Arquivado', case=False, na=False)].shape[0]

now = datetime.now(timezone.utc)
df_cards_filtered['due_date'] = pd.to_datetime(df_cards_filtered['due'], utc=True, errors='coerce')
overdue_count = df_cards_filtered[(df_cards_filtered['due_date'] < now) & (~df_cards_filtered['dueComplete'])].shape[0]
unassigned_count = df_cards_filtered[df_cards_filtered['idMembers'].apply(len) == 0].shape[0]

# --- INSIGHTS ENGINE ---
# Gera insights com base nos dados filtrados e ações
insights_list = generate_insights(df_cards_filtered, actions, all_lists)

# --- MAIN DASHBOARD ---
# Title with Target Icon
try:
    with open("assets/target.png", "rb") as f:
        target_encoded = base64.b64encode(f.read()).decode()
    title_html = f"""
    <div class="title-container">
        <img src="data:image/png;base64,{target_encoded}" class="title-icon-img">
        <h2 style="margin:0; padding:0;">Visão Geral do Board</h2>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
except:
    st.markdown("## 🦁 Visão Geral do Board")

# KPIs (New Style)
k1, k2, k3, k4 = st.columns(4)
with k1: 
    # Use HTML wrapper from components
    render_kpi_card_new("Total Registros", total_cards, "Volume total filtrado", "edit.png")
with k2: 
    render_kpi_card_new("Em Execução", wip_count, "Cards ativos (WIP)", "gear.png")
with k3: 
    render_kpi_card_new("Atrasados", overdue_count, "Vencidos e pendentes", "siren.png")
with k4: 
    render_kpi_card_new("Sem Dono", unassigned_count, "Aguardando atribuição", "user.png")

st.markdown("---")

# --- ROW 1: STATUS, DISTRIBUTION & INSIGHTS ---
st.markdown("### 📊 Status, Distribuição & Insights")

# Layout: 3 colunas (Bar | Donut | Insights)
# Ajustando proporção para dar destaque aos charts mas manter insights visíveis
c1, c2, c3 = st.columns([1.8, 1.2, 1.5])

with c1:
    st.caption("Volume por Fase")
    list_counts = df_cards_filtered['list_name'].value_counts().reset_index()
    render_plotly_bar(list_counts, 'list_name', 'count', "") # Titulo removido para usar caption externa

with c2:
    st.caption("Distribuição do WIP")
    # Restored "WIP Donut" - showing distribution of active cards
    wip_df = df_cards_filtered[~df_cards_filtered['list_name'].str.contains('Done|Concluído|Backlog', case=False, na=False)]
    if not wip_df.empty:
        wip_counts = wip_df['list_name'].value_counts().reset_index()
        render_plotly_pie(wip_counts, 'count', 'list_name', "", hole=0.6) # Titulo removido
    else:
        st.info("Sem cards em 'WIP' para exibir gráfico.")

with c3:
    st.caption("🧠 Insights Automáticos")
    if insights_list:
        # Mostrar max 2-3 insights por vez para não poluir
        for insight in insights_list[:3]:
            render_insight_card(insight)
        
        if len(insights_list) > 3:
            with st.expander(f"Ver mais {len(insights_list)-3} insights"):
                for insight in insights_list[3:]:
                    render_insight_card(insight)
    else:
        st.success("Tudo certo! Nenhuma anomalia detectada no momento.")

# --- ROW 2: THROUGHPUT & TEAM ---
st.markdown("---")
r2_c1, r2_c2 = st.columns([2, 1])

with r2_c1:
    st.markdown("### 📈 Produtividade (Throughput)")
    # actions já foi carregado lá em cima
    if actions:
        done_list_ids = [lid for lid, name in all_lists.items() if 'Done' in name or 'Concluído' in name]
        throughput_dates = []
        for action in actions:
            if action['type'] == 'updateCard' and action['data'].get('listAfter', {}).get('id') in done_list_ids:
                throughput_dates.append(action['date'])
        
        if throughput_dates:
            df_tp = pd.DataFrame({'date': throughput_dates})
            df_tp['date'] = pd.to_datetime(df_tp['date'], utc=True)
            df_tp['week'] = df_tp['date'].dt.to_period('W').apply(lambda r: r.start_time)
            weekly_tp = df_tp['week'].value_counts().sort_index().reset_index()
            weekly_tp.columns = ['Semana', 'Entregas']
            
            # FIXED: px.area handles fill automatically. Removed invalid 'fill_color' param.
            fig_tp = px.area(weekly_tp, x='Semana', y='Entregas', template="plotly_dark")
            fig_tp.update_traces(line_color='#d4af37') 
            fig_tp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="#ccc",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_tp, use_container_width=True)
        else:
            st.info("Sem dados históricos de conclusão suficientes.")

with r2_c2:
    st.markdown("### 👥 Equipe")
    df_exp = df_cards_filtered.explode('idMembers')
    df_exp['member_name'] = df_exp['idMembers'].map(all_members).fillna('N/A')
    member_counts = df_exp['member_name'].value_counts().reset_index()
    render_plotly_pie(member_counts, 'count', 'member_name', "Cards por Membro", hole=0.4)
