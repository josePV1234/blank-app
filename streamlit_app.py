import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Terminal Pro IA - Estrategia", page_icon="💹", layout="wide")

# --- FUNCIONES DE LOGICA ---
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        return 1 / yf.Ticker("EURUSD=X").fast_info.last_price
    except:
        return 0.92

def obtener_recomendacion(precio, target, rec_key):
    # Lógica de decisión multicriterio
    if rec_key in ['strong_buy', 'buy'] and precio < target:
        return "COMPRAR ✅", "El precio está en zona de descuento respecto al objetivo de analistas.", "green"
    elif precio > target * 1.1:
        return "VENDER 🚨", "El valor ha superado su precio objetivo; riesgo de corrección alto.", "red"
    else:
        return "MANTENER ⚖️", "Precio en equilibrio. Esperar a nuevas señales de volumen.", "orange"

# --- INTERFAZ ---
ticker_input = st.text_input("Introduce Ticker:", "NVDA").upper()
cambio = get_exchange_rate()

if ticker_input:
    with st.spinner('Procesando señales horarias y consenso...'):
        try:
            accion = yf.Ticker(ticker_input)
            info = accion.info
            precio_actual = info.get('currentPrice', info.get('regularMarketPrice'))
            target_mean = info.get('targetMeanPrice', 0)
            
            # 1. BLOQUE DE DECISIÓN (COMPRAR/VENDER)
            st.subheader("🎯 Recomendación Estratégica")
            rec_text, motivo, color = obtener_recomendacion(precio_actual, target_mean, info.get('recommendationKey'))
            
            c1, c2 = st.columns([1, 2])
            c1.markdown(f"<h1 style='color:{color}; text-align:center;'>{rec_text}</h1>", unsafe_allow_html=True)
            c2.info(f"**Análisis:** {motivo}")

            st.markdown("---")

            # 2. COMPORTAMIENTO PARA MAÑANA Y HORARIOS CLAVE
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("📅 Predicción Próxima Sesión")
                hist = accion.history(period="5d")
                vol_medio = hist['Volume'].mean()
                ultimo_vol = hist['Volume'].iloc[-1]
                
                if ultimo_vol > vol_medio and precio_actual > hist['Close'].iloc[-2]:
                    st.success("🔮 **PREVISIÓN:** ALCISTA. Fuerte acumulación detectada al cierre.")
                elif ultimo_vol > vol_medio and precio_actual < hist['Close'].iloc[-2]:
                    st.error("🔮 **PREVISIÓN:** BAJISTA. Distribución institucional detectada.")
                else:
                    st.warning("🔮 **PREVISIÓN:** LATERAL. Baja convicción en el mercado.")

            with col_b:
                st.subheader("⏰ Mapa de Calor Horario (España)")
                st.write("Basado en patrones de liquidez y volatilidad:")
                # Horarios recomendados por expertos
                st.markdown("""
                - **15:30 - 16:30:** 🚀 **Máxima Subida/Bajada** (Apertura USA).
                - **17:00 - 19:00:** 🧊 **Estabilidad** (Bajo volumen, movimientos lentos).
                - **21:30 - 22:00:** ⚡ **Cierre Crítico** (Ajuste de carteras institucionales).
                """)

            # 3. DATOS DE RESPALDO
            with st.expander("Ver Datos Técnicos Completos"):
                st.write(f"Precio Objetivo: {target_mean * cambio:.2f} €")
                st.write(f"Rango 52 semanas: {info.get('fiftyTwoWeekLow', 0) * cambio:.2f}€ - {info.get('fiftyTwoWeekHigh', 0) * cambio:.2f}€")

        except Exception as e:
            st.error("Error al conectar con la base de datos bursátil.")

st.sidebar.caption(f"Cambio actual: 1 USD = {cambio:.4f} EUR")
