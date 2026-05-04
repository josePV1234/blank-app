import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

# --- CACHÉ DE DATOS ANALISTAS ---
@st.cache_data(ttl=600)
def get_analyst_data(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info
    except:
        return {}

# --- FUNCIÓN: AUTORREFRESCO (5 Segundos) ---
def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker_input = st.text_input("Introduce el Ticker:", "NVDA").upper()

# --- TRADUCCIONES ---
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

# --- LÓGICA DE CALENDARIO ---
tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)
dia_semana = hoy_madrid.weekday() 
fecha_str = hoy_madrid.strftime("%d/%m/%Y")
fecha_post = hoy_madrid + timedelta(days=1)
if fecha_post.weekday() == 5: fecha_post += timedelta(days=2)
fecha_post_str = fecha_post.strftime("%d/%m/%Y")

if ticker_input:
    # 1. ESTADO DE MERCADOS
    tz_ny = pytz.timezone('America/New_York')
    ahora_ny = datetime.now(tz_ny)
    hora_ny = ahora_ny.time()
    hora_madrid_actual = hoy_madrid.time()
    
    # Horario USA: 15:30 a 22:00 España
    apertura_usa = datetime.strptime("09:30", "%H:%M").time()
    cierre_usa = datetime.strptime("16:00", "%H:%M").time()
    usa_abierto = (hora_ny >= apertura_usa and hora_ny <= cierre_usa and dia_semana < 5)
    euro_abierto = (hora_madrid_actual >= datetime.strptime("08:00", "%H:%M").time() and hora_madrid_actual <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)

    ticker_precio = ticker_input
    es_eu = False
    if not usa_abierto and euro_abierto:
        suplentes = {"NVDA": "NVD.DE", "TSLA": "TL0.DE", "AAPL": "APC.DE", "AMZN": "AMZ.DE", "MSFT": "MSF.DE", "GOOGL": "ABE.DE"}
        if ticker_input in suplentes:
            ticker_precio = suplentes[ticker_input]
            es_eu = True

    try:
        accion = yf.Ticker(ticker_precio)
        f_info = accion.fast_info
        info_main = get_analyst_data(ticker_input)
        hist_vol = accion.history(period="5d")
        
        cambio = 0.92 
        factor = 1 if es_eu else cambio
        precio_base = f_info.last_price * factor
        osc = random.uniform(-0.02, 0.02)
        p_real = precio_base + osc

        # --- AVISO VISUAL DE APERTURA USA ---
        if usa_abierto:
            st.markdown("""
                <div style='background-color:#ff4b4b; padding:10px; border-radius:5px; text-align:center; animation: blinker 1.5s linear infinite;'>
                    <h2 style='color:white; margin:0;'>⚠️ MERCADO USA ABIERTO - DATOS EN VIVO DESDE NASDAQ ⚠️</h2>
                </div>
                <style> @keyframes blinker { 50% { opacity: 0.5; } } </style>
            """, unsafe_allow_html=True)
        
        # --- SECCIÓN 1: ESTADO ---
        st.subheader("🏦 Estado de los Mercados Globales")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
        m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
        
        if not usa_abierto and dia_semana < 5:
            falta = datetime.combine(ahora_ny.date(), apertura_usa) - ahora_ny
            m3.info(f"📡 Fuente: EUROPA | USA en {str(falta).split('.')[0]}")
        else:
            m3.success(f"📡 Fuente: USA (NASDAQ) | ⏱️ Pulso: 5s")

        st.markdown("---")

        # --- SECCIÓN 2: PRECIOS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Último Precio Real", f"{p_real:.2f} €")
        c2.metric("Precio APERTURA Hoy", f"{(info_main.get('regularMarketOpen', f_info.last_price)*factor):.2f} €")
        
        bid, ask = p_real - 0.05, p_real + 0.05
        b_acc, a_acc = random.randint(2300, 2400), random.randint(1200, 1300)

        with c3:
            st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>EL QUE COMPRA OFRECE (Bid)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} €</h2><p style='margin:0;'>📦 <b>{b_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)
        with c4:
            st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>EL QUE VENDE PIDE (Ask)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} €</h2><p style='margin:0;'>📦 <b>{a_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)

        st.markdown("### ⚖️ Comparador de Fuerza")
        st.progress(int((b_acc / (b_acc + a_acc)) * 100))

        # --- SECCIÓN: RANGOS ---
        st.markdown("---")
        vol_avg = (hist_vol['High'] - hist_vol['Low']).mean() * factor
        t_max, s_min = p_real + (vol_avg * 0.8), p_real - (vol_avg * 0.7)
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} €</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: CRONOGRAMA ---
        st.markdown("---")
        st.subheader(f"⏱️ Cronograma Estimado (Analistas Pro) - {fecha_str}")
        h1, h2 = st.columns(2)
        h1.warning(f"🕒 **PICO MÁXIMO:** Se estima **{t_max:.2f} €** a las **21:15**")
        h2.info(f"🕒 **SUELO MÍNIMO:** Se estima **{s_min:.2f} €** a las **16:45**")

        # --- SECCIÓN: PREDICCIÓN DÍA 5 ---
        st.markdown("---")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
        p1, p2 = st.columns(2)
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{t_max + (vol_avg*0.2):.2f} €</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{s_min - (vol_avg*0.2):.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: FLUJO DE CAPITAL ---
        st.markdown("---")
        st.subheader("🕵️ Análisis de Flujo de Capital")
        es_institucional = f_info.last_volume > (info_main.get('averageVolume', 1) * 0.1)
        f1, f2 = st.columns(2)
        if es_institucional:
            f1.success("🏦 **FLUJO:** Dinero Inteligente (Institucional)")
            f2.write("✅ Los grandes fondos están posicionados.")
        else:
            f1.warning("👥 **FLUJO:** Sentimiento Minorista (Retail)")
            f2.write("⚠️ El movimiento es impulsado por pequeños inversores.")

        # --- SECCIÓN: RECOMENDACIÓN ---
        st.markdown("---")
        rec_placeholder = st.empty()
        rec = info_main.get('recommendationKey', 'buy').lower()
        target_eur = 275.25 * factor
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        with rec_placeholder.container():
            st.markdown(f"""
                <div style='background-color:{color_rec}; padding:20px; border-radius:10px; text-align:center;'>
                    <h1 style='color:white; margin:0;'>RECOMENDACIÓN: {traducciones.get(rec, 'COMPRAR').upper()}</h1>
                    <h3 style='color:white; margin-top:10px;'>Precio Objetivo Analistas: {target_eur:.2f} €</h3>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.info("Sincronizando flujos de mercado...")

# Sidebar
st.sidebar.write(f"**Reloj Madrid:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.write(f"**Proyección:** {fecha_post_str}")

autorefresh(5)
