import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import time
import os
import requests

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PASS = os.getenv("DB_PASS", "neurocnc_secret")
API_URL = os.getenv("API_URL", "http://backend-brain:8000")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database="neurocnc", user="postgres", password=DB_PASS)

st.set_page_config(page_title="Neuro-CNC Ops", layout="wide", page_icon="⚙️")

st.title("⚙️ Neuro-CNC: Centro de Comando")

# Layout
col_kpi, col_actions = st.columns([2, 1])

def approve_correction(action_id):
    try:
        r = requests.post(f"{API_URL}/approve_action/{action_id}")
        if r.status_code == 200:
            st.success(f"Comando enviado para CNC! ID: {action_id}")
        else:
            st.error("Erro na API")
    except Exception as e:
        st.error(f"Falha de conexão: {e}")

while True:
    # 1. Coluna da Esquerda: Dados
    with col_kpi:
        try:
            conn = get_db_connection()
            df = pd.read_sql("SELECT time, spindle_load, spindle_temp FROM telemetry ORDER BY time DESC LIMIT 200", conn)
            conn.close()

            if not df.empty:
                k1, k2 = st.columns(2)
                latest = df.iloc[0]
                k1.metric("Carga Spindle", f"{latest['spindle_load']:.1f}%", delta_color="inverse")
                k2.metric("Temp. Eixo", f"{latest['spindle_temp']:.1f}°C")
                
                fig = px.area(df, x='time', y='spindle_load', title="Assinatura de Carga em Tempo Real")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning("Conectando ao banco de dados...")

    # 2. Coluna da Direita: Ações Pendentes
    with col_actions:
        st.subheader("🤖 Sugestões da IA")
        try:
            conn = get_db_connection()
            # Pega a ultima ação não aplicada (simplificado)
            actions = pd.read_sql("SELECT * FROM ai_actions ORDER BY id DESC LIMIT 1", conn)
            conn.close()

            if not actions.empty:
                act = actions.iloc[0]
                st.info(f"Peça Recente Detectada")
                st.write(f"**Sugestão:** Ajuste Eixo X (VC100)")
                st.write(f"**Valor:** {act['suggested_offset_vc']} mm")
                st.write(f"**Confiança:** {act['confidence_score']*100:.0f}%")
                
                if st.button("APLICAR CORREÇÃO NA MÁQUINA", key=f"btn_{act['id']}"):
                    approve_correction(act['id'])
            else:
                st.write("Nenhuma correção pendente.")
                
        except:
            pass

    time.sleep(2)
    st.rerun()