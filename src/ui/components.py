import streamlit as st 
import pandas as pd
import plotly.express as px
import base64
import os
import urllib.parse
import textwrap
from datetime import datetime, timezone, timedelta

def render_kpi_card_new(label, value, footer="Dados atualizados", icon="📊"):
    """
    Renderiza um card KPI premium com layout flexbox:
    - Header: título + ícone alinhados
    - Valor destacado
    - Footer com borda superior
    - Hover: lift + glow + borda dourada
    """

    # Lógica para ícones emoji ou PNG
    if icon.endswith(".png"):
        try:
            with open(f"assets/{icon}", "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
                icon_html = f'<img src="data:image/png;base64,{encoded}" class="kpi-icon-img" alt="icon">'
        except Exception:
            icon_html = '<span class="kpi-icon">⚠️</span>'
    else:
        icon_html = f'<span class="kpi-icon">{icon}</span>'

    st.markdown(f"""
    <div class="kpi-card-premium">
        <div class="kpi-header">
            <span class="kpi-title">{label}</span>
            {icon_html}
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">{footer}</div>
    </div>
    """, unsafe_allow_html=True)


def render_plotly_bar(df, x, y, title, color="#d4af37"):
    """
    Gráfico de barras com tooltip humanizado.
    """
    fig = px.bar(df, x=x, y=y, title=title if title else None, template="plotly_dark")
    
    fig.update_traces(
        marker_color=color,
        hovertemplate="<b>Fase:</b> %{x}<br><b>Cards:</b> %{y}<extra></extra>"
    )
    
    layout_args = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=45 if title else 20, b=20),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        hoverlabel=dict(
            bgcolor="#1a1c24",
            font_size=13,
            font_family="Inter",
            font_color="#f8f9fa",
            bordercolor="#d4af37"
        )
    )
    
    if title:
        layout_args['title_font'] = dict(size=16, color="#d4af37", family='Inter', weight=600)
    
    fig.update_layout(**layout_args)
    
    st.plotly_chart(fig, use_container_width=True)

def render_plotly_pie(df, values, names, title, hole=0.5):
    """
    Donut chart com:
    - Paleta clara e contrastante (6 tons)
    - Tooltips humanizados em PT-BR
    - Números destacados com bom contraste
    - Contorno discreto
    """
    # Última atualização: 2026-01-30 11:13 - Paleta com cinza prateado
    # Paleta otimizada: tons claros e vibrantes que se destacam no dark theme
    # Mantendo harmonia com a identidade visual dourada (#d4af37, #ffd700)
    PALETTE_PREMIUM = [
        '#FFEB3B',  # Amarelo claro vibrante
        '#FFD700',  # Dourado brilhante
        '#FFB74D',  # Laranja suave
        '#CFD8DC',  # Cinza claro prateado (Blue Grey 100)
        '#81C784',  # Verde menta
        '#CE93D8',  # Roxo claro
    ]
    
    fig = px.pie(
        df, 
        values=values, 
        names=names, 
        title=title if title else None, 
        hole=hole, 
        template="plotly_dark",
        color_discrete_sequence=PALETTE_PREMIUM
    )
    
    # Tooltips humanizados
    fig.update_traces(
        textposition='inside',
        texttemplate='<b>%{percent}</b>',  # Bold nos números
        textfont=dict(size=16, color='#000', family='Inter'),
        marker=dict(
            line=dict(color='rgba(14, 17, 23, 0.6)', width=1.5)  # Contorno discreto
        ),
        hovertemplate="<b>%{label}</b><br>Cards: %{value}<br>Participação: %{percent}<extra></extra>"
    )
    
    layout_args = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.15, 
            xanchor="center", 
            x=0.5,
            font=dict(size=11, color='#ccc')
        ),
        margin=dict(l=20, r=20, t=45 if title else 20, b=20),
        hoverlabel=dict(
            bgcolor="#1a1c24",
            font_size=13,
            font_family="Inter",
            font_color="#f8f9fa",
            bordercolor="#d4af37"
        )
    )
    
    if title:
         layout_args['title_font'] = dict(size=16, color="#d4af37", family='Inter', weight=600)

    fig.update_layout(**layout_args)
    
    
    # Adicionar ícone SVG animado no centro do donut (fundo transparente garantido)
    
    # SVG de relógio dourado com fundo transparente
    clock_svg = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#d4af37" stroke-width="4"/>
        <line x1="50" y1="50" x2="50" y2="20" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
        <line x1="50" y1="50" x2="70" y2="65" stroke="#d4af37" stroke-width="3" stroke-linecap="round"/>
        <circle cx="50" cy="50" r="4" fill="#d4af37"/>
    </svg>
    '''
    
    # Codificar SVG para data URI
    svg_encoded = urllib.parse.quote(clock_svg)
    svg_data_uri = f"data:image/svg+xml,{svg_encoded}"
    
    # Adicionar imagem no centro usando layout image
    fig.add_layout_image(
        dict(
            source=svg_data_uri,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=0.18, sizey=0.18,
            xanchor="center", yanchor="middle",
            opacity=0.8
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar CSS para animação de rotação do ícone
    
    st.markdown("""
    <style>
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Animar imagens dentro do gráfico Plotly */
    .js-plotly-plot .plotly image {
        animation: spin 3s linear infinite;
        transform-origin: center;
    }
    </style>
    """, unsafe_allow_html=True)

def render_insight_card(insight):
    """
    Renderiza um card de insight com visual premium.
    insight: dict com keys {type, severity, title, metric, description, recommendation, details}
    """
    
    # Mapeamento de cores e ícones por severidade
    styles = {
        "critical": {"color": "#FF5252", "icon": "🚨", "bg": "rgba(255, 82, 82, 0.1)"},
        "attention": {"color": "#FFA726", "icon": "⚠️", "bg": "rgba(255, 167, 38, 0.1)"},
        "info": {"color": "#29B6F6", "icon": "💡", "bg": "rgba(41, 182, 246, 0.1)"},
        "success": {"color": "#66BB6A", "icon": "🚀", "bg": "rgba(102, 187, 106, 0.1)"}
    }
    
    s = styles.get(insight.get("severity", "info"), styles["info"])
    
    # HTML do Card - Minificado para evitar interpretação de bloco de código pelo Markdown
    html_content = f"""<div style="background: linear-gradient(145deg, #1e2029, #14161d); border-left: 4px solid {s['color']}; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: transform 0.2s;"><div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;"><div style="display: flex; align-items: center; gap: 8px;"><span style="font-size: 1.2rem;">{s['icon']}</span><span style="color: {s['color']}; font-weight: 700; font-size: 0.9rem; text-transform: uppercase;">{insight['title']}</span></div><span style="background: {s['bg']}; color: {s['color']}; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{insight['metric']}</span></div><p style="color: #e0e0e0; font-size: 0.95rem; margin-bottom: 8px; line-height: 1.4;">{insight['description']}</p><div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); display: flex; gap: 8px; align-items: center;"><span style="font-size: 1rem;">👉</span><span style="color: #bbb; font-size: 0.85rem; font-style: italic;">{insight['recommendation']}</span></div></div>"""
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Detalhes (st.expander fora do HTML para usar componentes nativos se quiser, ou texto simples)
    if insight.get('details'):
        with st.expander("Ver detalhes e evidências"):
            for item in insight['details']:
                # Formata detalhes dependendo do conteúdo
                if 'name' in item:
                    # É um card
                    st.markdown(f"- **{item.get('list_name', '')}**: {item['name']} " + 
                                (f"*(Venceu: {item['due_date'].strftime('%d/%m')})*" if 'due_date' in item and hasattr(item['due_date'], 'strftime') else ""))
                else:
                    st.write(item)

def get_relative_time(dt):
    """Retorna uma string humanizada do tempo decorrido."""
    if not dt: return "--"
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    if diff.days > 30: return dt.strftime('%d/%m/%y')
    if diff.days > 0: return f"há {diff.days}d"
    if diff.seconds > 3600: return f"há {diff.seconds // 3600}h"
    return "agora"

def render_explorer_table(df_cards, on_card_click):
    """
    Renderiza uma tabela premium de cartões com suporte a busca e filtros aplicados.
    """
    if df_cards.empty:
        st.info("Nenhum cartão encontrado com os filtros aplicados.")
        return

    # Estilo CSS para a tabela explorer (Sticky Header + Hover + Zebra)
    st.markdown("""
    <style>
    .explorer-container {
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 8px;
        overflow: hidden;
        background: #14161d;
    }
    .explorer-header-row {
        background: rgba(212, 175, 55, 0.05);
        color: #d4af37;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px;
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1.2fr 0.8fr 0.5fr;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }
    .explorer-row {
        padding: 10px 12px;
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1.2fr 0.8fr 0.5fr;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        transition: all 0.2s;
        cursor: pointer;
    }
    .explorer-row:hover {
        background: rgba(212, 175, 55, 0.08);
        box-shadow: inset 2px 0 0 #d4af37;
    }
    .explorer-row:nth-child(even) { background: rgba(255,255,255,0.01); }
    
    .label-badge {
        font-size: 0.65rem;
        padding: 1px 6px;
        border-radius: 10px;
        margin-right: 4px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .list-badge { 
        background: rgba(255,255,255,0.08); 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.7rem;
        color: #ccc;
    }
    .age-indicator {
        font-size: 0.7rem;
        color: #888;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .status-vencido { color: #ff5252; font-weight: 600; }
    .status-vencendo { color: #ffa726; font-weight: 600; }
    .status-ok { color: #66bb6a; }

    /* Reduzir botões de ação na tabela */
    [data-testid="column"] button {
        height: 30px !important;
        min-height: 30px !important;
        padding: 0 !important;
        line-height: 30px !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Headers
    st.markdown("""
    <div class="explorer-header-row">
        <div>Card / Labels</div>
        <div>Lista</div>
        <div>Prazo</div>
        <div>Última Ativ.</div>
        <div>Idade</div>
        <div style="text-align:center;">Ações</div>
    </div>
    """, unsafe_allow_html=True)

    now = datetime.now(timezone.utc)

    for _, card in df_cards.iterrows():
        # 1. Prazos
        due_html = '<span class="status-ok">--</span>'
        if card['due']:
            due_dt = pd.to_datetime(card['due'], utc=True)
            due_str = due_dt.strftime('%d/%m')
            if card['dueComplete']: 
                due_html = f'<span class="status-ok">✅ {due_str}</span>'
            elif due_dt < now: 
                due_html = f'<span class="status-vencido">🚨 {due_str}</span>'
            elif (due_dt - now).days < 2: 
                due_html = f'<span class="status-vencendo">⏳ {due_str}</span>'
            else:
                due_html = f'<span>📅 {due_str}</span>'
        
        # 2. Labels
        labels_html = '<div>'
        for lbl in card.get('labels', [])[:3]:
            color = lbl.get('color', 'gray')
            labels_html += f'<span class="label-badge" style="background: {color}44; color: white; border-color: {color}">{lbl.get("name","")}</span>'
        if len(card.get('labels', [])) > 3:
            labels_html += f'<span class="label-badge">+{len(card["labels"])-3}</span>'
        labels_html += '</div>'

        # 3. Idade (Calculada ou Placeholder)
        # O Trello API não envia common creation date no card objeto base, mas podemos usar o ID como aproximação
        # ou apenas omitir se não tivermos a data de criação carregada. Usaremos dateLastActivity como 'Idade' visual aqui simplificada.
        age_days = (now - pd.to_datetime(card['dateLastActivity'], utc=True)).days
        age_icon = "🟢" if age_days < 5 else "🟡" if age_days < 15 else "🔴"

        with st.container():
            # Usando grid layout via markdown para precisão visual, mas os botões precisam ser Streamlit
            col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1, 1, 1.2, 0.8, 0.5])
            
            with col1:
                st.markdown(f"**{card['name']}**{labels_html}", unsafe_allow_html=True)
            with col2:
                st.markdown(f'<span class="list-badge">{card["list_name"]}</span>', unsafe_allow_html=True)
            with col3:
                st.markdown(due_html, unsafe_allow_html=True)
            with col4:
                last_dt = pd.to_datetime(card['dateLastActivity'], utc=True)
                st.markdown(f"**{last_dt.strftime('%d/%m')}** <br><small style='color:#777'>{get_relative_time(last_dt)}</small>", unsafe_allow_html=True)
            with col5:
                st.markdown(f"<div class='age-indicator'>{age_icon} {age_days}d</div>", unsafe_allow_html=True)
            with col6:
                if st.button("👁️", key=f"exp_btn_{card['id']}", help="Ver detalhes completos"):
                    on_card_click(card['id'])

@st.dialog("Detalhes do Card", width="large")
def render_card_detail_dialog(card_data, details):
    """
    Modal premium com informações completas do cartão.
    """
    # Header Estilizado
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(212,175,55,0.1) 0%, rgba(0,0,0,0) 100%); 
                padding: 15px; border-left: 4px solid #d4af37; border-radius: 4px; margin-bottom: 25px;">
        <h2 style="margin:0; color: #fff; font-size: 1.5rem;">{card_data['name']}</h2>
        <div style="margin-top: 8px;">
            <span style="background: rgba(255,255,255,0.1); color: #ccc; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem;">
                📍 {card_data['list_name']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([2, 1])

    with col_m1:
        # Descrição
        st.markdown("### 📝 Descrição")
        desc = card_data.get('desc') or "*Este cartão não possui descrição.*"
        st.info(desc)
        
        # Checklists com progresso real
        st.markdown("### ✅ Checklists")
        if not details.get('checklists'):
            st.write("Nenhum checklist disponível.")
        else:
            for ck in details['checklists']:
                items = ck.get('checkItems', [])
                total = len(items)
                completed = len([i for i in items if i['state'] == 'complete'])
                progress = (completed / total) if total > 0 else 0
                
                # Barra de progresso premium
                st.markdown(f"**{ck['name']}** <small>({completed}/{total})</small>", unsafe_allow_html=True)
                st.progress(progress)
                
                with st.expander("Ver itens do checklist"):
                    for item in items:
                        icon = "✅" if item['state'] == 'complete' else "⬜"
                        color = "#66BB6A" if item['state'] == 'complete' else "#bbb"
                        st.markdown(f"<span style='color:{color}'>{icon} {item['name']}</span>", unsafe_allow_html=True)

        # Anexos (Novo)
        if details.get('attachments'):
            st.markdown("### 📎 Anexos")
            for att in details['attachments'][:5]:
                dt_att = pd.to_datetime(att['date']).strftime('%d/%m')
                st.markdown(f"[{att['name']}]({att['url']}) <small>({dt_att})</small>", unsafe_allow_html=True)

    with col_m2:
        # Prazos e Metadados
        st.markdown("### ℹ️ Detalhes")
        due_dt = pd.to_datetime(card_data['due']) if card_data['due'] else None
        due_str = due_dt.strftime('%d/%m/%Y %H:%M') if due_dt else "Não definido"
        
        st.markdown(f"**📅 Entrega:**\n{due_str}")
        
        # Atividade Recente (Timeline)
        st.markdown("### 🕒 Atividade")
        if not details.get('actions'):
            st.caption("Sem atividades recentes.")
        else:
            for act in details['actions'][:8]:
                dt = pd.to_datetime(act['date']).strftime('%d/%m %H:%M')
                member = act.get('memberCreator', {}).get('fullName', 'Membro')
                
                # Tradução básica de ações
                msg = act['type']
                if act['type'] == 'commentCard':
                    msg = f"comentou: *\"{act['data']['text'][:100]}...\"*"
                elif act['type'] == 'updateCard' and 'listAfter' in act['data']:
                    msg = f"moveu para **{act['data']['listAfter']['name']}**"
                elif act['type'] == 'createCard':
                    msg = "criou o card"
                
                st.markdown(f"<p style='font-size:0.8rem; margin-bottom:4px; color:#aaa;'><b>{member}</b> {msg}<br><small>{dt}</small></p>", unsafe_allow_html=True)

        st.divider()
        st.link_button("Abrir no Trello ↗️", card_data.get('url', card_data.get('shortUrl', '#')), use_container_width=True)
