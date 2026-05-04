import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
import pytz 

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA - Estrategia Total", page_icon="💹", layout="wide")

# --- FUNCIÓN: AUTORREFRESCO ---
def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "NVDA").upper()

# --- TRADUCCIONES ---
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE", "none": "SIN CALIFICACIÓN"}

# --- LÓGICA HORARIA (MADRID) ---
tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)
fecha_str = hoy_madrid.strftime("%d/%m/%Y")

# --- FECHA MAÑANA ---
fecha_post = hoy_madrid + timedelta(days=1)
if fecha_post.weekday() == 5: fecha_post += timedelta(days=2)
fecha_post_str = fecha_post.strftime("%d/%m/%Y")

# --- CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Analizando {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            # Forzamos la actualización de info cada vez
            info = accion.info 

            # --- SECCIÓN 1: ESTADO MERCADOS ---
            st.subheader("🏦 Estado de los Mercados Globales")
            hora_madrid = hoy_madrid.time()
            tz_ny = pytz.timezone('America/New_York')
            hora_ny = datetime.now(tz_ny).time()
            
            euro_abierto = (hora_madrid >= datetime.strptime("09:00", "%H:%M").time() and hora_madrid <= datetime.strptime("17:30", "%H:%M").time() and hoy_madrid.weekday() < 5)
            usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and hora_ny <= datetime.strptime("16:00", "%H:%M").time() and hoy_madrid.weekday() < 5)

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
            c2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
            c3.info(f"**Trade Republic:** :{'green'}[ACTIVO]")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS REALES ---
            # Si Bid/Ask son 0 porque el mercado está cerrado, usamos el último precio
            precio_actual = f_info.last_price * cambio
            bid = info.get('bid', f_info.last_price) * cambio
            ask = info.get('ask', f_info.last_price) * cambio
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Último Precio Real", f"{precio_actual:.2f} €")
            col2.metric("Precio APERTURA", f"{(info.get('regularMarketOpen', f_info.last_price)*cambio):.2f} €")
            
            # Estilo mejorado para que no parezca "apagado"
            col3.markdown(f"<div style='background-color:#1e1e1e; padding:10px; border-radius:5px; border-bottom: 3px solid #28a745;'><p style='color:#28a745; font-weight:bold; margin:0;'>EL QUE COMPRA OFRECE</p><h2 style='margin:0;'>{bid:.2f} €</h2></div>", unsafe_allow_html=True)
            col4.markdown(f"<div style='background-color:#1e1e1e; padding:10px; border-radius:5px; border-bottom: 3px solid #007bff;'><p style='color:#007bff; font-weight:bold; margin:0;'>EL QUE VENDE PIDE</p><h2 style='margin:0;'>{ask:.2f} €</h2></div>", unsafe_allow_html=True)

            # --- SECCIÓN 4: RANGOS Y PREDICCIÓN ---
            st.markdown("---")
            volatilidad = (hist['High'] - hist['Low']).mean() * cambio
            
            # Hoy
            r1, r2 = st.columns(2)
            r1.success(f"### MÁXIMO hoy ({fecha_str}):\n# {precio_actual + (volatilidad*0.8):.2f} €")
            r2.error(f"### MÍNIMO hoy ({fecha_str}):\n# {precio_actual - (volatilidad*0.7):.2f} €")

            st.markdown("---")
            st.subheader(f"🔮 Predicción Mañana: {fecha_post_str}")
            p1, p2 = st.columns(2)
            # Predicción calculada para mañana
            p1.info(f"### MÁXIMO Previsto:\n# {precio_actual + (volatilidad*1.2):.2f} €")
            p2.warning(f"### MÍNIMO Previsto:\n# {precio_actual - (volatilidad*0.9):.2f} €")

            # --- DECISIÓN ---
            st.markdown("---")
            rec = info.get('recommendationKey', 'none').lower()
            color = "#28a745" if "buy" in rec else "#dc3545" if "sell" in rec else "#ffc107"
            st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; text-align:center;'><h1 style='color:white; margin:0;'>RECOMENDACIÓN: {traducciones.get(rec, 'MANTENER')}</h1></div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Mercado fuera de hora o Ticker no válido.")

# Sidebar info
st.sidebar.write(f"**Hora Madrid:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.write(f"Refresco automático: **30s**")

autorefresh(30)
