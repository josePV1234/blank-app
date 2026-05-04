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

ticker_input = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "NVDA").upper()

# --- DICCIONARIO DE TRADUCCIÓN ---
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

# --- LÓGICA DE CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker_input:
    with st.spinner(f'Actualizando precios reales...'):
        try:
            # --- DETERMINAR ESTADO DE MERCADOS ---
            hora_madrid = hoy_madrid.time()
            tz_ny = pytz.timezone('America/New_York')
            hora_ny = datetime.now(tz_ny).time()
            usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and hora_ny <= datetime.strptime("16:00", "%H:%M").time() and dia_semana < 5)
            euro_abierto = (hora_madrid >= datetime.strptime("08:00", "%H:%M").time() and hora_madrid <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)
            
            # --- CONMUTACIÓN DE TICKER ---
            ticker_final = ticker_input
            es_suplente = False
            if not usa_abierto and euro_abierto:
                suplentes = {"NVDA": "NVD.DE", "TSLA": "TL0.DE", "AAPL": "APC.DE", "AMZN": "AMZ.DE", "MSFT": "MSF.DE", "GOOGL": "ABE.DE"}
                if ticker_input in suplentes:
                    ticker_final = suplentes[ticker_input]
                    es_suplente = True

            accion = yf.Ticker(ticker_final)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            try: info = accion.info
            except: info = {}

            st.subheader("🏦 Estado de los Mercados Globales")
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
            col_m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
            col_m3.info(f"📡 Fuente: {'EUROPA' if es_suplente else 'USA'}")

            st.markdown("---")

            # --- SECCIÓN 2: LÓGICA DE PRECIOS DINÁMICOS ---
            factor = 1 if es_suplente else cambio
            precio_base = f_info.last_price
            
            # Calculamos un spread realista (0.05% aprox) para cuando el mercado no lo da
            spread_est = precio_base * 0.0005 
            
            # Intentamos obtener Bid/Ask real, si son iguales o cero, aplicamos el spread dinámico
            bid_val = info.get('bid', 0)
            ask_val = info.get('ask', 0)

            if bid_val == 0 or bid_val == ask_val:
                bid_val = precio_base - (spread_est / 2)
                ask_val = precio_base + (spread_est / 2)

            bid_final = bid_val * factor
            ask_final = ask_val * factor
            
            # Simulamos volumen de órdenes si el mercado está en subasta
            bid_size = info.get('bidSize', 0) * 100 if info.get('bidSize', 0) > 0 else 1500
            ask_size = info.get('askSize', 0) * 100 if info.get('askSize', 0) > 0 else 1200

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Último Precio Real", f"{precio_base * factor:.2f} €")
            col2.metric("Precio APERTURA", f"{(info.get('regularMarketOpen', precio_base)*factor):.2f} €")
            
            col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{bid_final:.2f} €</h2>", unsafe_allow_html=True)
            col3.write(f"📦 **{bid_size:,.0f}**. acciones".replace(",", "."))
            
            col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
            col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{ask_final:.2f} €</h2>", unsafe_allow_html=True)
            col4.write(f"📦 **{ask_size:,.0f}**. acciones".replace(",", "."))

            # --- SECCIÓN 3: FUERZA ---
            st.markdown("### ⚖️ Comparador de Fuerza")
            total = bid_size + ask_size
            porc = (bid_size / total) * 100
            st.progress(int(porc))
            st.write(f"🟢 **Compra:** {porc:.1f}% | 🔵 **Venta:** {100-porc:.1f}%")

            # --- SECCIÓN 4: RANGOS Y PREDICCIÓN (MANTENIDO) ---
            st.markdown("---")
            vol = (hist['High'] - hist['Low']).mean() * factor
            t_max = (precio_base * factor) + (vol * 0.85)
            s_min = (precio_base * factor) - (vol * 0.70)
            
            r1, r2 = st.columns(2)
            r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} €</h1></div>", unsafe_allow_html=True)
            r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} €</h1></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
            p1, p2 = st.columns(2)
            p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{t_max + (vol*0.2):.2f} €</h1></div>", unsafe_allow_html=True)
            p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{s_min - (vol*0.2):.2f} €</h1></div>", unsafe_allow_html=True)

            # --- DECISIÓN ---
            st.markdown("---")
            rec = info.get('recommendationKey', 'buy').lower()
            color = "#28a745" if "buy" in rec else "#dc3545" if "sell" in rec else "#ffc107"
            st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; text-align:center;'><h1 style='color:white; margin:0;'>{traducciones.get(rec, 'COMPRAR').upper()}</h1></div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Sincronizando...")

# Sidebar
st.sidebar.write(f"**Reloj Madrid:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.write(f"**Proyección:** {fecha_post_str}")

autorefresh(30)
