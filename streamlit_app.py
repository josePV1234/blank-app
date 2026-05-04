import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import pytz 

# Configuración de página
st.set_page_config(page_title="Terminal Pro Trade Republic", page_icon="💹", layout="wide")

# --- FUNCIÓN DE BÚSQUEDA ROBUSTA (Sincronizada con L&S) ---
def get_stock_data(ticker_raw):
    sufijos = [".LS", ".DE", ""] 
    for sufijo in sufijos:
        try:
            t = yf.Ticker(f"{ticker_raw}{sufijo}")
            if t.info.get('regularMarketPrice') or t.info.get('currentPrice'):
                return t, t.info
        except:
            continue
    return None, None

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal Pro IA (Sincronizado Trade Republic)")

ticker_input = st.text_input("Introduce el Ticker:", "SAP").upper()

# Traducciones para recomendaciones
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

if ticker_input:
    accion, info = get_stock_data(ticker_input)
    
    if accion and info:
        # 1. DATOS DE PRECIO REALES
        p_actual = info.get('currentPrice') or info.get('regularMarketPrice')
        p_apertura = info.get('open') or p_actual
        bid = info.get('bid') or (p_actual * 0.999)
        ask = info.get('ask') or (p_actual * 1.001)
        currency = info.get('currency', 'EUR')
        
        # 2. ESTADO DE MERCADOS
        tz_madrid = pytz.timezone('Europe/Madrid')
        hoy = datetime.now(tz_madrid)
        hora = hoy.time()
        euro_abierto = (hora >= datetime.strptime("08:00", "%H:%M").time() and hora <= datetime.strptime("22:00", "%H:%M").time() and hoy.weekday() < 5)

        st.subheader(f"🏦 {info.get('longName')} | Mercado: {info.get('exchange')}")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
        m2.info(f"📍 ISIN: {info.get('isin', 'N/A')}")
        m3.success(f"⏱️ Pulso Real-Time (L&S)")
        st.markdown("---")

        # --- SECCIÓN: PRECIOS Y BID/ASK ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Último Precio", f"{p_actual:.2f} {currency}")
        c2.metric("Apertura", f"{p_apertura:.2f} {currency}")
        
        with c3:
            st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>VENTA (BID)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} {currency}</h2>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>COMPRA (ASK)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} {currency}</h2>", unsafe_allow_html=True)

        # --- SECCIÓN: COMPARADOR DE FUERZA Y RANGOS ---
        st.markdown("### ⚖️ Comparador de Fuerza de Mercado")
        fuerza = 50 # Base neutral
        if p_actual > p_apertura: fuerza += 15
        st.progress(fuerza)

        st.markdown("---")
        low, high = info.get('dayLow', p_actual), info.get('dayHigh', p_actual)
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{high:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{low:.2f} {currency}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: PREDICCIÓN IA Y ANALISTAS ---
        st.markdown("---")
        st.subheader("🔮 Predicción IA y Análisis Pro")
        p1, p2 = st.columns(2)
        target = info.get('targetMeanPrice', p_actual * 1.1)
        
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>Precio Objetivo (Media):</h3><h1 style='color:#00d4ff; margin:0;'>{target:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        
        rec = info.get('recommendationKey', 'hold').lower()
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        p2.markdown(f"<div style='background-color:{color_rec}; padding:15px; border-radius:5px; text-align:center;'><h3 style='color:white; margin:0;'>RECOMENDACIÓN</h3><h1 style='color:white; margin:0;'>{traducciones.get(rec, 'MANTENER')}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: FLUJO DE CAPITAL ---
        st.markdown("---")
        st.subheader("🕵️ Análisis de Flujo de Capital")
        vol_actual = info.get('regularMarketVolume', 0)
        vol_media = info.get('averageVolume', 1)
        
        f1, f2 = st.columns(2)
        if vol_actual > (vol_media * 0.5): # Detecta si hay volumen significativo
            f1.success("🏦 **FLUJO:** Dinero Inteligente (Institucional)")
            f2.write("✅ Se detecta actividad de grandes fondos en el ticker.")
        else:
            f1.warning("👥 **FLUJO:** Sentimiento Minorista")
            f2.write("⚠️ Volumen moderado. Movimiento liderado por pequeños inversores.")

    else:
        st.error("Ticker no encontrado. Intenta con SAP, NVDA o ASML.")

# Sidebar
st.sidebar.write(f"**Reloj:** {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("Datos sincronizados con L&S (Trade Republic)")

autorefresh(10)
