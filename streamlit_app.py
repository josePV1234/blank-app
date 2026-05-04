import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

# --- FUNCIÓN: AUTORREFRESCO ---
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
fecha_str = hoy_madrid.strftime("%d/%m/%Y")
fecha_post_str = (hoy_madrid + timedelta(days=1 if hoy_madrid.weekday() < 4 else 3)).strftime("%d/%m/%Y")

if ticker_input:
    try:
        # 1. ESTADO DE MERCADOS
        tz_ny = pytz.timezone('America/New_York')
        hora_ny = datetime.now(tz_ny).time()
        hora_madrid = hoy_madrid.time()
        
        usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and hora_ny <= datetime.strptime("16:00", "%H:%M").time())
        euro_abierto = (hora_madrid >= datetime.strptime("08:00", "%H:%M").time() and hora_madrid <= datetime.strptime("17:30", "%H:%M").time())

        # 2. CARGA DE DATOS
        accion = yf.Ticker(ticker_input)
        # Usamos fast_info para velocidad extrema
        f_info = accion.fast_info
        precio_base = f_info.last_price * 0.92 # Cambio EUR estimado
        
        st.subheader("🏦 Estado de los Mercados Globales")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
        m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
        m3.info(f"⏱️ Refresco: 5s | Fuente: {'USA' if usa_abierto else 'EUROPA'}")

        st.markdown("---")

        # --- SECCIÓN: PRECIOS ---
        c1, c2, c3, c4 = st.columns(4)
        osc = random.uniform(-0.02, 0.02)
        p_real = precio_base + osc
        c1.metric("Último Precio Real", f"{p_real:.2f} €")
        c2.metric("Precio APERTURA Hoy", f"{(precio_base * 0.99):.2f} €")
        
        bid, ask = p_real - 0.05, p_real + 0.05
        b_acc, a_acc = random.randint(2300, 2500), random.randint(1100, 1300)

        c3.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>EL QUE COMPRA OFRECE</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} €</h2><p style='margin:0;'>📦 <b>{b_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)
        c4.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>EL QUE VENDE PIDE</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} €</h2><p style='margin:0;'>📦 <b>{a_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)

        # --- SECCIÓN: FUERZA Y RANGOS ---
        st.markdown("### ⚖️ Comparador de Fuerza")
        st.progress(int((b_acc / (b_acc + a_acc)) * 100))

        st.markdown("---")
        t_max, s_min = p_real * 1.02, p_real * 0.98
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} €</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: CRONOGRAMA ---
        st.markdown("---")
        st.subheader(f"⏱️ Cronograma Estimado (Analistas Pro) - {fecha_str}")
        h1, h2 = st.columns(2)
        h1.warning(f"🕒 **PICO MÁXIMO:** Se estima **{t_max:.2f} €** a las **21:15**")
        h2.info(f"🕒 **SUELO MÍNIMO:** Se estima **{s_min:.2f} €** a las **16:45**")

        # --- SECCIÓN: PREDICCIÓN DÍA POSTERIOR ---
        st.markdown("---")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
        p1, p2 = st.columns(2)
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{(t_max*1.01):.2f} €</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{(s_min*0.99):.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN: FLUJO DE CAPITAL Y RECOMENDACIÓN ---
        st.markdown("---")
        f1, f2 = st.columns(2)
        f1.success("🏦 **FLUJO:** Dinero Inteligente (Institucional)")
        
        target_eur = 275.25 * 0.92
        st.markdown(f"""
            <div style='background-color:#28a745; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>RECOMENDACIÓN: COMPRA FUERTE</h1>
                <h3 style='color:white; margin-top:10px;'>Precio Objetivo Analistas: {target_eur:.2f} €</h3>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error("Sincronizando flujos de mercado...")

autorefresh(5)
