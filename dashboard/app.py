import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import time
import os

# Configuração
DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "neurocnc_secret")

def get_data():
    conn = psycopg2.connect(
        host=DB_HOST, database="neurocnc", user="postgres", password=DB_PASS
    )
    # Query SQL para pegar últimos 500 pontos
    query = "SELECT time, spindle_load, spindle_temp FROM telemetry ORDER BY time DESC LIMIT 500"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Neuro-CNC Dashboard", layout="wide")

st.title("🎛️ Neuro-CNC: Monitoramento em Tempo Real")

col1, col2 = st.columns(2)

placeholder = st.empty()

while True:
    try:
        df = get_data()
        
        with placeholder.container():
            # Métricas rápidas (KPIs)
            latest = df.iloc[0]
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Carga Spindle", f"{latest['spindle_load']:.1f}%")
            kpi2.metric("Temperatura", f"{latest['spindle_temp']:.1f}°C")
            kpi3.metric("Status IA", "Ativa", delta_color="normal")

            # Gráficos
            fig_load = px.line(df, x='time', y='spindle_load', title='Histórico de Carga')
            fig_temp = px.line(df, x='time', y='spindle_temp', title='Estabilidade Térmica')
            
            st.plotly_chart(fig_load, use_container_width=True)
            st.plotly_chart(fig_temp, use_container_width=True)

        time.sleep(2) # Atualiza a cada 2 segundos
        
    except Exception as e:
        st.error(f"Aguardando dados do Banco... ({e})")
        time.sleep(5)