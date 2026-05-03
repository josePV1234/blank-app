import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA - Estrategia Total", page_icon="💹", layout="wide")

# --- NUEVA FUNCIÓN: AUTORREFRESCO ---
if 'count' not in st.session_state:
    st.session_state.count = 0

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "NVDA").upper()

# --- DICCIONARIO DE TRADUCCIÓN ---
traducciones = {
    "strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER",
    "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE",
    "underperform": "BAJO RENDIMIENTO", "none": "SIN CALIFICACIÓN"
}

# --- LÓGICA DE CALENDARIO ---
hoy = datetime.now()
dia_semana = hoy.weekday() 
if dia_semana >= 5: 
    fecha_analisis = hoy + timedelta(days=(7 - dia_semana))
else:
    fecha_analisis = hoy
fecha_str = fecha_analisis.strftime("%d/%m/%Y")

# --- LÓGICA DÍA POSTERIOR ---
fecha_posterior = fecha_analisis + timedelta(days=1)
if fecha_posterior.weekday() == 5:
    fecha_posterior += timedelta(days=2)
fecha_post_str = fecha_posterior.strftime("%d/%m/%Y")

# --- LÓGICA DE CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Actualizando datos de {ticker} en vivo...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            try: info = accion.info
            except: info = {}

            # --- SECCIÓN 1: ESTADO DE LOS MERCADOS ---
            st.subheader("🏦 Estado de los Mercados Globales")
            hora_actual = datetime.now().time()
            hora_ny = (datetime.utcnow() - timedelta(hours=4)).time()
            
            usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and hora_ny <= datetime.strptime("16:00", "%H:%M").time() and dia_semana < 5)
            euro_abierto = (hora_actual >= datetime.strptime("09:00", "%H:%M").time() and hora_actual <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)
            tr_abierto = (hora_actual >= datetime.strptime("07:30", "%H:%M").time() and hora_actual <= datetime.strptime("23:00", "%H:%M").time() and dia_semana < 5)

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
            col_m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
            col_m3.info(f"**Trade Republic:** :{'green' if tr_abierto else 'red'}[{'ACTIVO' if tr_abierto else 'INACTIVO'}]")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS Y ÓRDENES PROGRAMADAS ---
            col1, col2, col3, col4 = st.columns(4)
            precio_real_eur = f_info.last_price * cambio
            
            bid_size = info.get('bidSize', 0) * 100 
            ask_size = info.get('askSize', 0) * 100

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio APERTURA", f"{(info.get('regularMarketOpen', f_info.last_price)*cambio):.2f} €")
            
            col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{info.get('bid', 0)*cambio:.2f} €</h2>", unsafe_allow_html=True)
            col3.write(f"📦 **{bid_size:,.0f}**. acciones".replace(",", "."))
            
            col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
            col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{info.get('ask', 0)*cambio:.2f} €</h2>", unsafe_allow_html=True)
            col4.write(f"📦 **{ask_size:,.0f}**. acciones".replace(",", "."))

            # --- SECCIÓN 3: COMPARADOR DE FUERZA ---
            st.markdown("### ⚖️ Comparador de Fuerza")
            total_ordenes = bid_size + ask_size
            if total_ordenes > 0:
                porcentaje_compra = (bid_size / total_ordenes) * 100
                st.progress(int(porcentaje_compra))
                c_izq, c_der = st.columns(2)
                c_izq.write(f"🟢 **Ganas de comprar:** {porcentaje_compra:.1f}%")
                c_der.write(f"🔵 **Ganas de vender:** {100-porcentaje_compra:.1f}%")

            # --- SECCIÓN 4: RANGO DE PRECIOS MÁXIMO/MÍNIMO ---
            st.markdown("---")
            st.subheader(f"📊 Rango de Precios Estimado - Sesión: {fecha_str}")
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            techo_max = precio_real_eur + (volatilidad_avg * 0.85)
            suelo_min = precio_real_eur - (volatilidad_avg * 0.70)
            
            r1, r2 = st.columns(2)
            r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{techo_max:.2f} €</h1></div>", unsafe_allow_html=True)
            r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{suelo_min:.2f} €</h1></div>", unsafe_allow_html=True)

            # --- SECCIÓN 5: PREDICCIÓN DÍA POSTERIOR ---
            st.markdown("---")
            st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
            pred_max = techo_max + (volatilidad_avg * 0.2)
            pred_min = suelo_min - (volatilidad_avg * 0.2)
            
            pcol1, pcol2 = st.columns(2)
            pcol1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Estimado ({fecha_post_str}):</h3><h1 style='color:#00d4ff; margin:0;'>{pred_max:.2f} €</h1></div>", unsafe_allow_html=True)
            pcol2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Estimado ({fecha_post_str}):</h3><h1 style='color:#ffaa00; margin:0;'>{pred_min:.2f} €</h1></div>", unsafe_allow_html=True)

            # --- SECCIÓN: DECISIÓN FINAL ---
            st.markdown("---")
            st.subheader(f"🚩 DECISIÓN FINAL PARA EL DÍA: {fecha_str}")
            rec_key = info.get('recommendationKey', 'none').lower()
            color_f = "#28a745" if rec_key in ['strong_buy', 'buy'] else "#dc3545" if rec_key in ['sell', 'strong_sell'] else "#ffc107"
            decision = traducciones.get(rec_key, "MANTENER / NEUTRAL")
            st.markdown(f"<div style='background-color:{color_f}; padding:20px; border-radius:10px; text-align:center;'><h1 style='color:white; margin:0;'>RECOMENDACIÓN: {decision}</h1></div>", unsafe_allow_html=True)

            # --- SECCIÓN: PUNTOS CRÍTICOS (FECHA AÑADIDA AQUÍ) ---
            st.markdown("---")
            st.subheader(f"⏱️ Operativa Sugerida para el {fecha_str}")
            p1, p2 = st.columns(2)
            p1.info(f"**Mayor SUBIDA esperada ({fecha_str}):** +{(techo_max-precio_real_eur):.2f} €")
            p1.error(f"**Mayor BAJADA esperada ({fecha_str}):** -{(precio_real_eur-suelo_min):.2f} €")
            p2.write(f"📥 **Compra ideal ({fecha_str}):** 15:35 | 📤 **Venta ideal ({fecha_str}):** 21:40")

        except Exception as e:
            st.error(f"Error al obtener datos. Reintentando...")

# Sidebar
st.sidebar.write(f"**Día Actual:** {fecha_str}")
st.sidebar.write(f"**Próximo Análisis:** {fecha_post_str}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")

autorefresh(30)
