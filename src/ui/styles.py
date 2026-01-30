import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* === KPI CARD PREMIUM === */
        .kpi-card-premium {
            background: linear-gradient(135deg, #1a1c24 0%, #14161d 100%);
            border-radius: 10px;
            border-left: 4px solid #d4af37;
            padding: 22px 24px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            position: relative;
            overflow: hidden;
        }

        .kpi-card-premium::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 10px;
            padding: 2px;
            background: linear-gradient(135deg, transparent, transparent);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .kpi-card-premium:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(212, 175, 55, 0.25), 0 0 20px rgba(212, 175, 55, 0.15);
            border-left-color: #ffd700;
        }

        .kpi-card-premium:hover::before {
            background: linear-gradient(135deg, #d4af37, #ffd700);
            opacity: 0.4;
        }

        /* Header: Título + Ícone */
        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }

        .kpi-title {
            color: #999;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            line-height: 1.3;
        }

        .kpi-icon {
            color: #d4af37;
            font-size: 1.5rem;
            opacity: 0.85;
            transition: all 0.3s ease;
        }

        .kpi-icon-img {
            width: 34px;
            height: 34px;
            object-fit: contain;
            opacity: 0.9;
            transition: all 0.3s ease;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }

        .kpi-card-premium:hover .kpi-icon-img {
            transform: scale(1.15) rotate(8deg);
            opacity: 1;
            filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.7));
        }

        .kpi-card-premium:hover .kpi-icon {
            transform: scale(1.1);
            opacity: 1;
        }

        /* Valor Grande */
        .kpi-value {
            color: #f8f9fa;
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 10px;
            line-height: 1;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        /* Footer */
        .kpi-footer {
            color: #666;
            font-size: 0.78rem;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 10px;
            margin-top: auto;
            font-weight: 500;
        }

        /* === TITLE WITH ICON === */
        .title-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
        }

        .title-icon-img {
            width: 44px;
            height: 44px;
            object-fit: contain;
            transition: transform 0.3s ease;
            filter: drop-shadow(0 2px 6px rgba(212, 175, 55, 0.4));
        }

        .title-icon-img:hover {
            transform: scale(1.12) rotate(-5deg);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0e1117 !important;
            border-right: 1px solid rgba(212, 175, 55, 0.12);
        }

        /* Titles */
        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
    </style>
    """, unsafe_allow_html=True)
