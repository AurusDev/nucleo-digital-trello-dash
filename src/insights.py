from datetime import datetime, timezone, timedelta
import pandas as pd

def generate_insights(df_cards, df_actions, list_names_map):
    """
    Gera insights determinísticos baseados nos dados do board.
    Retorna uma lista de dicionários com: type, severity, title, metric, description, recommendation.
    """
    insights = []
    
    if df_cards.empty:
        return insights

    # Helper: Garantir datas UTC
    now = datetime.now(timezone.utc)
    if 'due_date' not in df_cards.columns:
         df_cards['due_date'] = pd.to_datetime(df_cards['due'], utc=True, errors='coerce')
    
    # ---------------------------------------------------------
    # 1. RISCO (Critical): Cards Vencidos
    # ---------------------------------------------------------
    overdue_df = df_cards[
        (df_cards['due_date'] < now) & 
        (~df_cards['dueComplete']) & 
        (df_cards['due_date'].notna())
    ]
    overdue_count = len(overdue_df)
    
    if overdue_count > 0:
        insight = {
            "type": "risk",
            "severity": "critical",  # critical, attention, info
            "title": "Prazos Expirados",
            "metric": f"{overdue_count} cards",
            "description": f"Existem {overdue_count} atividades com data de entrega passada que ainda não foram concluídas.",
            "recommendation": "Priorizar imediatamente ou renegociar prazos para evitar gargalos em cascata.",
            "details": overdue_df[['name', 'list_name', 'due_date']].to_dict('records')
        }
        insights.append(insight)

    # ---------------------------------------------------------
    # 2. GESTÃO (Attention): Cards Sem Dono (Unassigned)
    # ---------------------------------------------------------
    # Filtra apenas listas que não são de "Done" ou "Backlog" para ser mais relevante
    active_lists_df = df_cards[
        ~df_cards['list_name'].str.contains('Done|Concluído|Backlog|Arquivado|Model', case=False, na=False)
    ]
    
    unassigned_df = active_lists_df[active_lists_df['idMembers'].apply(len) == 0]
    unassigned_count = len(unassigned_df)
    
    if unassigned_count > 0:
        insight = {
            "type": "management",
            "severity": "attention",
            "title": "Atividades Órfãs",
            "metric": f"{unassigned_count} cards",
            "description": "Existem atividades em progresso sem nenhum responsável atribuído.",
            "recommendation": "Atribuir membros responsáveis para garantir accountability e execução.",
            "details": unassigned_df[['name', 'list_name']].to_dict('records')
        }
        insights.append(insight)

    # ---------------------------------------------------------
    # 3. GARGALO (Warning): Lista com Acúmulo Anormal
    # ---------------------------------------------------------
    # Conta cards por lista (apenas ativas e que não sejam de conclusão)
    bottleneck_lists_df = active_lists_df[
        ~active_lists_df['list_name'].str.contains('Done|Concluído|Concluded', case=False, na=False)
    ]
    
    if not bottleneck_lists_df.empty:
        list_counts = bottleneck_lists_df['list_name'].value_counts()
        if not list_counts.empty:
            max_list = list_counts.idxmax()
            max_count = list_counts.max()
            avg_count = list_counts.mean()
            
            # Se a maior lista tiver 50% mais cards que a média (e tiver pelo menos 3 cards)
            if max_count > 2 and max_count > (avg_count * 1.5):
                insight = {
                    "type": "bottleneck",
                    "severity": "attention",
                    "title": f"Gargalo em '{max_list}'",
                    "metric": f"{max_count} cards",
                    "description": f"A etapa '{max_list}' concentra um volume desproporcional de atividades ({int(max_count/active_lists_df.shape[0]*100)}% do WIP).",
                    "recommendation": "Verificar impedimentos nesta etapa ou redistribuir força de trabalho.",
                    "details": [] 
                }
                insights.append(insight)

    # ---------------------------------------------------------
    # 4. PERFORMANCE (Info): Tendência de Throughput
    # ---------------------------------------------------------
    # Analisa ações de conclusão nas últimas 2 semanas
    if df_actions:
        # Filtrar ações de conclusão (mover para done)
        done_list_ids = [lid for lid, name in list_names_map.items() 
                         if 'Done' in name or 'Concluído' in name]
        
        dates = []
        for action in df_actions:
            if (action['type'] == 'updateCard' and 
                action['data'].get('listAfter', {}).get('id') in done_list_ids):
                dates.append(pd.to_datetime(action['date']))
        
        if dates:
            df_dates = pd.DataFrame({'date': dates})
            df_dates['date'] = pd.to_datetime(df_dates['date'], utc=True)
            
            # Definir semana atual e anterior
            this_week_start = now - timedelta(days=now.weekday())
            last_week_start = this_week_start - timedelta(days=7)
            
            count_this_week = len(df_dates[df_dates['date'] >= this_week_start])
            count_last_week = len(df_dates[
                (df_dates['date'] >= last_week_start) & 
                (df_dates['date'] < this_week_start)
            ])
            
            trend = "Estável"
            severity = "info"
            
            # Só gera insight se tiver dados comparáveis
            if count_last_week > 0:
                delta = count_this_week - count_last_week
                pct_change = (delta / count_last_week) * 100
                
                if pct_change >= 20:
                    trend = "Alta Produtividade"
                    desc = f"O time entregou {int(pct_change)}% mais cards que na semana passada."
                    rec = "Investigar o que funcionou bem e replicar as boas práticas."
                    severity = "success" # Special case for color
                    icon = "🚀"
                elif pct_change <= -20:
                    trend = "Queda de Ritmo"
                    desc = f"Redução de {abs(int(pct_change))}% nas entregas comparado à semana anterior."
                    rec = "Checar se houve bloqueios externos ou redução de capacidade da equipe."
                    severity = "attention"
                    icon = "📉"
                else:
                    trend = "Ritmo Estável"
                    desc = "A produtividade se mantém consistente com a média recente."
                    rec = "Manter o ritmo e monitorar qualidade das entregas."
                    icon = "📊"
                
                insight = {
                    "type": "performance",
                    "severity": severity,
                    "title": trend,
                    "metric": f"{count_this_week} entregas",
                    "description": desc,
                    "recommendation": rec,
                    "details": []
                }
                insights.append(insight)
            elif count_this_week > 0:
                 # Primeira semana com dados
                 insight = {
                    "type": "performance",
                    "severity": "info",
                    "title": "Ritmo Inicial",
                    "metric": f"{count_this_week} entregas",
                    "description": "Primeiros registros de conclusão contabilizados nesta semana.",
                    "recommendation": "Continuar registrando para gerar histórico de tendências.",
                    "details": []
                }
                 insights.append(insight)

    return insights
