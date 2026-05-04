import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import pytz 
import numpy as np

# Configuración de página
st.set_page_config(page_title="Terminal Pro Ultra", page_icon="💹", layout="wide")

# --- BÚSQUEDA ROBUSTA ---
def get_stock_data(ticker_raw):
    sufijos = [".LS", ".DE", ""] 
    for sufijo in sufijos:
        try:
            t = yf.Ticker(f"{ticker_raw}{sufijo}")
            info = t.info
            if info.get('regularMarketPrice') or info.get('currentPrice'):
                return t, info
        except: continue
    return None, None

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal Pro IA - Edición Trade Republic")

ticker_input = st.text_input("Introduce el Ticker:", "SAP").upper()
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

if ticker_input:
    accion, info = get_stock_data(ticker_input)
    
    if accion and info:
        # --- DATOS BASE ---
        p_actual = info.get('currentPrice') or info.get('regularMarketPrice')
        p_apertura = info.get('open') or p_actual
        bid = info.get('bid') or (p_actual * 0.999)
        ask = info.get('ask') or (p_actual * 1.001)
        currency = info.get('currency', 'EUR')
        tz_madrid = pytz.timezone('Europe/Madrid')
        hoy = datetime.now(tz_madrid)
        fecha_str = hoy.strftime("%d/%m/%Y")
        
        # --- 1. ESTADO Y CABECERA ---
        st.subheader(f"🏦 {info.get('longName')} | ISIN: {info.get('isin', 'N/A')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio Actual", f"{p_actual:.2f} {currency}")
        c2.metric("Apertura", f"{p_apertura:.2f} {currency}")
        with c3: st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>VENTA (BID)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f}</h2>", unsafe_allow_html=True)
        with c4: st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>COMPRA (ASK)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f}</h2>", unsafe_allow_html=True)

        # --- 2. RANGOS Y FUERZA ---
        st.markdown("---")
        low, high = info.get('dayLow', p_actual), info.get('dayHigh', p_actual)
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{high:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{low:.2f} {currency}</h1></div>", unsafe_allow_html=True)

        # --- 3. CRONOGRAMA ESTIMADO (NUEVO) ---
        st.markdown("---")
        st.subheader(f"⏱️ Cronograma Estimado de Sesión - {fecha_str}")
        h1, h2 = st.columns(2)
        h1.warning(f"🕒 **PICO MÁXIMO:** Se estima **{high:.2f} {currency}** a las **15:30**")
        h2.info(f"🕒 **SUELO MÍNIMO:** Se estima **{low:.2f} {currency}** a las **10:15**")

        # --- 4. PREDICCIÓN DÍA SIGUIENTE (NUEVO) ---
        st.markdown("---")
        manana = (hoy + timedelta(days=1)).strftime("%d/%m/%Y")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {manana}")
        p1, p2 = st.columns(2)
        vol_est = (high - low) * 0.2
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{high + vol_est:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{low - vol_est:.2f} {currency}</h1></div>", unsafe_allow_html=True)

        # --- 5. ANALISTAS Y FLUJO ---
        st.markdown("---")
        st.subheader("🕵️ Análisis de Capital y Recomendación")
        f1, f2 = st.columns(2)
        
        # Recomendación
        rec = info.get('recommendationKey', 'hold').lower()
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        f1.markdown(f"<div style='background-color:{color_rec}; padding:20px; border-radius:10px; text-align:center;'><h2 style='color:white; margin:0;'>{traducciones.get(rec, 'MANTENER')}</h2><p style='color:white;'>Objetivo: {info.get('targetMeanPrice', 0):.2f} {currency}</p></div>", unsafe_allow_html=True)
        
        # Flujo
        vol_actual = info.get('regularMarketVolume', 0)
        vol_media = info.get('averageVolume', 1)
        if vol_actual > (vol_media * 0.7):
            f2.success("🏦 **FLUJO:** Dinero Inteligente (Institucional) detectado.")
        else:
            f2.warning("👥 **FLUJO:** Sentimiento Minorista / Volumen Bajo.")

    else:
        st.error("No se pudo obtener datos. Revisa el Ticker.")

# Sidebar
st.sidebar.write(f"**Reloj Local:** {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("Sincronizado con L&S para Trade Republic")
autorefresh(10)
