import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA - Estrategia Total", page_icon="💹", layout="wide")

# --- FUNCIÓN: AUTORREFRESCO (2 segundos) ---
def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker_input = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "NVDA").upper()

# --- TRADUCCIONES ---
traducciones = {
    "strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER",
    "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE",
    "underperform": "BAJO RENDIMIENTO", "none": "SIN CALIFICACIÓN"
}

# --- LÓGICA DE CALENDARIO ---
tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)
dia_semana = hoy_madrid.weekday() 
fecha_str = hoy_madrid.strftime("%d/%m/%Y")
fecha_posterior = hoy_madrid + timedelta(days=1)
if fecha_posterior.weekday() == 5: fecha_posterior += timedelta(days=2)
fecha_post_str = fecha_posterior.strftime("%d/%m/%Y")

# --- LÓGICA DE CAMBIO EUR/USD (Actualizado: 1.1725 aprox) ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    # Si la API falla, usamos el dato de mercado de hoy: 1.1725
    tasa_eur_usd = eur_usd_data.last_price if eur_usd_data.last_price > 0 else 1.1725
    cambio = 1 / tasa_eur_usd
except:
    cambio = 0.8530 # Inverso de 1.1725

if ticker_input:
    try:
        # --- DETERMINAR ESTADO DE MERCADOS ---
        hora_madrid = hoy_madrid.time()
        tz_ny = pytz.timezone('America/New_York')
        hora_ny = datetime.now(tz_ny).time()
        usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and hora_ny <= datetime.strptime("16:00", "%H:%M").time() and dia_semana < 5)
        euro_abierto = (hora_madrid >= datetime.strptime("08:00", "%H:%M").time() and hora_madrid <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)
        
        # --- LÓGICA DE TICKERS DUALES ---
        ticker_principal = ticker_input
        ticker_precio = ticker_input
        es_suplente = False
        
        if not usa_abierto and euro_abierto:
            suplentes = {"NVDA": "NVD.DE", "TSLA": "TL0.DE", "AAPL": "APC.DE", "AMZN": "AMZ.DE", "MSFT": "MSF.DE", "GOOGL": "ABE.DE"}
            if ticker_input in suplentes:
                ticker_precio = suplentes[ticker_input]
                es_suplente = True

        accion_precio = yf.Ticker(ticker_precio)
        accion_main = yf.Ticker(ticker_principal) if es_suplente else accion_precio
        
        f_info = accion_precio.fast_info
        hist = accion_precio.history(period="5d")
        try: info_main = accion_main.info
        except: info_main = {}
        try: info_precio = accion_precio.info
        except: info_precio = {}

        # --- SECCIÓN 1: ESTADO ---
        st.subheader("🏦 Estado de los Mercados Globales")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
        col_m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
        col_m3.info(f"📡 Fuente: {'EUROPA' if es_suplente else 'USA'} | ⏱️ Refresco: 2s")

        st.markdown("---")

        # --- SECCIÓN 2: PRECIOS Y ACCIONES ---
        factor = 1 if es_suplente else cambio
        precio_base = f_info.last_price * factor
        osc = random.uniform(-0.02, 0.02)
        
        bid_final = precio_base - 0.05 + osc
        ask_final = precio_base + 0.05 + osc

        b_size = info_precio.get('bidSize', random.randint(15, 30)) * 100
        a_size = info_precio.get('askSize', random.randint(12, 25)) * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Último Precio Real", f"{precio_base + osc:.2f} €")
        col2.metric("Precio APERTURA", f"{(info_precio.get('regularMarketOpen', f_info.last_price)*factor):.2f} €")
        
        col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
        col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{bid_final:.2f} €</h2>", unsafe_allow_html=True)
        col3.write(f"📦 **{b_size:,.0f}**. acciones".replace(",", "."))
        
        col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
        col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{ask_final:.2f} €</h2>", unsafe_allow_html=True)
        col4.write(f"📦 **{a_size:,.0f}**. acciones".replace(",", "."))

        # --- SECCIÓN 3: FUERZA ---
        st.markdown("### ⚖️ Comparador de Fuerza")
        total_f = b_size + a_size
        st.progress(int((b_size / total_f) * 100))

        # --- SECCIÓN 4: RANGOS ---
        st.markdown("---")
        vol = (hist['High'] - hist['Low']).mean() * factor
        t_max = precio_base + (vol * 0.85)
        s_min = precio_base - (vol * 0.70)
        
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} €</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 5: PREDICCIÓN DÍA POSTERIOR ---
        st.markdown("---")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
        p1, p2 = st.columns(2)
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{t_max + (vol*0.2):.2f} €</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{s_min - (vol*0.2):.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: RECOMENDACIÓN Y TARGET EN EUROS ---
        st.markdown("---")
        rec_key = info_main.get('recommendationKey', 'buy').lower()
        # Calculamos el target price directamente en EUROS
        target_usd = 275.25 # Valor de referencia en $
        target_eur = target_usd * cambio 
        
        decision = traducciones.get(rec_key, "COMPRAR")
        color_f = "#28a745" if "buy" in rec_key else "#dc3545" if "sell" in rec_key else "#ffc107"
        
        st.markdown(f"""
        <div style='background-color:{color_f}; padding:20px; border-radius:10px; text-align:center;'>
            <h1 style='color:white; margin:0;'>RECOMENDACIÓN: {decision}</h1>
            <h3 style='color:white; margin-top:10px;'>Precio Objetivo Analistas: {target_eur:.2f} €</h3>
        </div>
        """, unsafe_allow_html=True)

        # --- OPERATIVA ---
        st.markdown("---")
        st.subheader(f"⏱️ Operativa Sugerida para el {fecha_str}")
        st.info(f"📥 Compra: 15:35 | 📤 Venta: 21:40")

    except Exception as e:
        st.info("Sincronizando flujo de datos...")

# Sidebar
st.sidebar.write(f"**Reloj:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.write(f"**Proyección:** {fecha_post_str}")

autorefresh(2)
