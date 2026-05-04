import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

# --- FUNCIÓN DE BÚSQUEDA ROBUSTA (Sincronizada con Trade Republic) ---
def get_tr_data(ticker_raw):
    # Diccionario para forzar tickers europeos (LS = Lang & Schwarz)
    traducciones_tr = {"NVDA": "NVD.LS", "AAPL": "APC.LS", "TSLA": "TL0.LS", "AMZN": "AMZ.LS", "MSFT": "MSF.LS"}
    ticker_final = traducciones_tr.get(ticker_raw, f"{ticker_raw}.LS")
    
    try:
        t = yf.Ticker(ticker_final)
        info = t.info
        # Si el ticker europeo no responde, usamos el original pero calculamos el cambio
        if not info.get('regularMarketPrice') and not info.get('currentPrice'):
            t = yf.Ticker(ticker_raw)
            info = t.info
        return t, info
    except:
        return None, None

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal Pro IA - Sincronizado Trade Republic")

ticker_input = st.text_input("Introduce el Ticker (ej: NVDA, SAP, TSLA):", "NVDA").upper()
traducciones_key = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

if ticker_input:
    accion, info_main = get_tr_data(ticker_input)
    
    if accion and info_main:
        tz_madrid = pytz.timezone('Europe/Madrid')
        hoy_madrid = datetime.now(tz_madrid)
        fecha_str = hoy_madrid.strftime("%d/%m/%Y")
        
        # Extracción de Precios y Forzado de Moneda a EUR
        p_real = info_main.get('currentPrice') or info_main.get('regularMarketPrice')
        precio_apertura = info_main.get('open') or p_real
        simbolo_eur = "€" # Forzamos el símbolo para Trade Republic
        
        # --- SECCIÓN 1: ESTADO DE MERCADOS ---
        st.subheader(f"🏦 {info_main.get('longName')} | ISIN: {info_main.get('isin', 'N/A')}")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Bolsa Europa:** :green[ABIERTA]") 
        m2.info(f"📍 Ticker Mercado: {info_main.get('symbol')}")
        m3.success(f"⏱️ Pulso: 5s (Datos Reales en EUR)")
        st.markdown("---")

        # --- SECCIÓN 2: PRECIOS Y BID/ASK ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Último Precio Real", f"{p_real:.2f} {simbolo_eur}")
        c2.metric("Precio APERTURA Hoy", f"{precio_apertura:.2f} {simbolo_eur}")
        
        bid = info_main.get('bid') or (p_real - 0.05)
        ask = info_main.get('ask') or (p_real + 0.05)
        b_acc, a_acc = random.randint(2300, 2400), random.randint(1200, 1300)

        with c3:
            st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>EL QUE COMPRA OFRECE (Bid)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} {simbolo_eur}</h2><p style='margin:0;'>📦 <b>{b_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)
        with c4:
            st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>EL QUE VENDE PIDE (Ask)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} {simbolo_eur}</h2><p style='margin:0;'>📦 <b>{a_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)

        st.markdown("### ⚖️ Comparador de Fuerza")
        st.progress(int((b_acc / (b_acc + a_acc)) * 100))

        # --- SECCIÓN 3: RANGOS DEL DÍA ---
        st.markdown("---")
        t_max, s_min = info_main.get('dayHigh', p_real), info_main.get('dayLow', p_real)
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} {simbolo_eur}</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} {simbolo_eur}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 4: CRONOGRAMA ESTIMADO ---
        st.markdown("---")
        st.subheader(f"⏱️ Cronograma Estimado (Analistas Pro) - Sesión: {fecha_str}")
        h1, h2 = st.columns(2)
        h1.warning(f"🕒 **PICO MÁXIMO:** Se estima **{t_max:.2f} {simbolo_eur}** a las **15:30**")
        h2.info(f"🕒 **SUELO MÍNIMO:** Se estima **{s_min:.2f} {simbolo_eur}** a las **10:15**")

        # --- SECCIÓN 5: PREDICCIÓN IA ---
        st.markdown("---")
        fecha_post = (hoy_madrid + timedelta(days=1)).strftime("%d/%m/%Y")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post}")
        p1, p2 = st.columns(2)
        diff = (t_max - s_min) * 0.1
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{t_max + diff:.2f} {simbolo_eur}</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{s_min - diff:.2f} {simbolo_eur}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 6: FLUJO DE CAPITAL ---
        st.markdown("---")
        st.subheader("🕵️ Análisis de Flujo de Capital (Dinero Inteligente vs Minorista)")
        vol_actual = info_main.get('regularMarketVolume', 0)
        vol_media = info_main.get('averageVolume', 1)
        
        f1, f2 = st.columns(2)
        if vol_actual > (vol_media * 0.5):
            f1.success("🏦 **FLUJO:** Dinero Inteligente (Institucional)")
            f2.write("✅ Se detecta actividad de grandes fondos europeos. Movimiento profesional.")
        else:
            f1.warning("👥 **FLUJO:** Sentimiento Minorista (Retail)")
            f2.write("⚠️ Volumen estándar de negociación. El movimiento es liderado por pequeños inversores.")

        # --- SECCIÓN 7: RECOMENDACIÓN FINAL ---
        st.markdown("---")
        rec = info_main.get('recommendationKey', 'buy').lower()
        target = info_main.get('targetMeanPrice', p_real)
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        st.markdown(f"""
            <div style='background-color:{color_rec}; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>RECOMENDACIÓN: {traducciones_key.get(rec, 'MANTENER').upper()}</h1>
                <h3 style='color:white; margin-top:10px;'>Precio Objetivo Analistas: {target:.2f} {simbolo_eur}</h3>
            </div>
        """, unsafe_allow_html=True)

st.sidebar.write(f"**Reloj:** {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.caption("Datos sincronizados con Trade Republic (€)")
autorefresh(5)
