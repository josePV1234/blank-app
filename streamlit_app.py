import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Terminal Pro IA - Analistas", page_icon="💹", layout="wide")

# Estilo personalizado para parecer un terminal Bloomberg/Reuters
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-label { font-size: 1.2rem !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💹 Terminal de Análisis Avanzado")

ticker_input = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, AAPL):", "NVDA").upper()

# --- LÓGICA DE CONVERSIÓN ---
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        data = yf.Ticker("EURUSD=X").fast_info
        return 1 / data.last_price
    except:
        return 0.92

cambio = get_exchange_rate()

if ticker_input:
    with st.spinner(f'Analizando datos institucionales para {ticker_input}...'):
        try:
            accion = yf.Ticker(ticker_input)
            info = accion.info
            hist = accion.history(period="1mo")
            
            # --- 1. CABECERA Y ESTADO ---
            nombre = info.get('longName', ticker_input)
            st.header(f"{nombre} ({ticker_input})")
            
            # --- 2. MÉTRICAS DE PRECIO REAL ---
            col1, col2, col3, col4 = st.columns(4)
            precio_actual = info.get('currentPrice', info.get('regularMarketPrice'))
            if not precio_actual: precio_actual = accion.fast_info.last_price

            col1.metric("Precio Actual (EUR)", f"{precio_actual * cambio:.2f} €")
            col2.metric("Apertura", f"{info.get('open', 0) * cambio:.2f} €")
            col3.metric("Máx. Día", f"{info.get('dayHigh', 0) * cambio:.2f} €")
            col4.metric("Volumen", f"{info.get('volume', 0):,}")

            st.markdown("---")

            # --- 3. EL PANEL DE LOS ANALISTAS (LA CLAVE) ---
            st.subheader("🕵️‍♂️ Consenso de los Mejores Analistas")
            
            # Datos de Wall Street
            target_high = info.get('targetHighPrice', 0)
            target_mean = info.get('targetMeanPrice', 0)
            rec_consensus = info.get('recommendationKey', 'N/A').replace('_', ' ').upper()
            num_analistas = info.get('numberOfAnalystOpinions', 'N/A')

            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("**Sentimiento Global**")
                color = "green" if "BUY" in rec_consensus else "orange"
                st.markdown(f"<h2 style='color:{color};'>{rec_consensus}</h2>", unsafe_allow_html=True)
                st.caption(f"Basado en {num_analistas} analistas institucionales")

            with c2:
                st.markdown("**Precio Objetivo (Target)**")
                upside = ((target_mean / precio_actual) - 1) * 100 if target_mean else 0
                st.write(f"Promedio: **{target_mean * cambio:.2f} €**")
                st.write(f"Potencial: **{upside:+.2f}%**")

            with c3:
                st.markdown("**Riesgo / Recompensa**")
                if precio_actual < target_mean:
                    st.success("INFRAVALORADA: El precio está por debajo del objetivo analista.")
                else:
                    st.warning("SOBREVALORADA: El precio ha superado el objetivo promedio.")

            # --- 4. ANÁLISIS TÉCNICO IA ---
            st.markdown("---")
            st.subheader("🔬 Análisis de Tendencia de Corto Plazo")
            
            # Lógica de cruce de medias simple
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ultimo_cierre = hist['Close'].iloc[-1]

            t1, t2 = st.columns(2)
            
            with t1:
                if ultimo_cierre > sma_20:
                    st.info("📈 **TENDENCIA:** Alcista. El precio se mantiene sobre la media de 20 días.")
                else:
                    st.error("📉 **TENDENCIA:** Bajista. Presión vendedora detectada.")

            with t2:
                vol_medio = hist['Volume'].mean()
                vol_hoy = info.get('volume', 0)
                if vol_hoy > vol_medio:
                    st.warning("⚠️ **VOLUMEN:** Inusual. Los 'peces gordos' están moviendo ficha.")
                else:
                    st.write("📊 **VOLUMEN:** Normal. Sin movimientos institucionales agresivos.")

        except Exception as e:
            st.error(f"Ticker no encontrado o error en la conexión. Revisa que sea correcto (ej: NVDA).")

st.sidebar.markdown(f"""
    **Configuración de Terminal**  
    Última actualización: `{datetime.now().strftime('%H:%M:%S')}`  
    Cambio aplicado: `1 USD = {cambio:.4f} EUR`
""")
