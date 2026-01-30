import streamlit as st
import plotly.express as px

def render_kpi_card_new(label, value, footer="Dados atualizados", icon="📊"):
    """
    Renderiza um card KPI premium com layout flexbox:
    - Header: título + ícone alinhados
    - Valor destacado
    - Footer com borda superior
    - Hover: lift + glow + borda dourada
    """
    import base64
    import os

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
    import urllib.parse
    
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
    import textwrap
    
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
