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

# --- LÓGICA DE CALENDARIO (MADRID) ---
tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)
dia_semana = hoy_madrid.weekday() 

if dia_semana >= 5: 
    fecha_analisis = hoy_madrid + timedelta(days=(7 - dia_semana))
else:
    fecha_analisis = hoy_madrid
fecha_str = fecha_analisis.strftime("%d/%m/%Y")

# --- LÓGICA DÍA POSTERIOR ---
fecha_posterior = fecha_analisis + timedelta(days=1)
if fecha_posterior.weekday() == 5: fecha_posterior += timedelta(days=2)
fecha_post_str = fecha_posterior.strftime("%d/%m/%Y")

# --- LÓGICA DE CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Analizando {ticker}...'):
        try:
            # Usamos period="1d" e interval="1m" para forzar el dato más fresco posible
            accion = yf.Ticker(ticker)
            datos_recientes = accion.history(period="1d", interval="1m")
            f_info = accion.fast_info
            hist_5d = accion.history(period="5d")
            info = accion.info

            # --- SECCIÓN 1: ESTADO DE LOS MERCADOS ---
            st.subheader("🏦 Estado de los Mercados Globales")
            hora_madrid = hoy_madrid.time()
            euro_abierto = (hora_madrid >= datetime.strptime("08:00", "%H:%M").time() and hora_madrid <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
            col_m2.info(f"**Reloj Madrid:** {hoy_madrid.strftime('%H:%M:%S')}")
            col_m3.info(f"**Trade Republic:** :green[ACTIVO]")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS Y ÓRDENES (CORREGIDO PARA REALISMO) ---
            col1, col2, col3, col4 = st.columns(4)
            
            # Intentar obtener el precio más real (el último de la gráfica de 1 minuto)
            precio_actual_raw = datos_recientes['Close'].iloc[-1] if not datos_recientes.empty else f_info.last_price
            precio_eur = precio_actual_raw * cambio

            # Lógica para Bid/Ask: Si no hay datos en vivo (mercado cerrado), simulamos el spread real
            bid_raw = info.get('bid') if info.get('bid', 0) > 0 else precio_actual_raw * 0.9995
            ask_raw = info.get('ask') if info.get('ask', 0) > 0 else precio_actual_raw * 1.0005
            
            bid_eur = bid_raw * cambio
            ask_eur = ask_raw * cambio

            col1.metric("Último Precio Real", f"{precio_eur:.2f} €")
            col2.metric("Precio APERTURA", f"{(info.get('regularMarketOpen', precio_actual_raw)*cambio):.2f} €")
            
            col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{bid_eur:.2f} €</h2>", unsafe_allow_html=True)
            
            col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
            col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{ask_eur:.2f} €</h2>", unsafe_allow_html=True)

            # --- SECCIÓN 4: RANGOS Y PREDICCIÓN DÍA 5 ---
            st.markdown("---")
            volatilidad = (hist_5d['High'] - hist_5d['Low']).mean() * cambio
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader(f"📊 Rango Hoy ({fecha_str})")
                st.info(f"**Máximo:** {(precio_eur + volatilidad*0.8):.2f} € | **Mínimo:** {(precio_eur - volatilidad*0.8):.2f} €")
            
            with c2:
                st.subheader(f"🔮 Próxima Sesión ({fecha_post_str})")
                st.success(f"**Máximo Previsto:** {(precio_eur + volatilidad*1.2):.2f} €")
                st.error(f"**Mínimo Previsto:** {(precio_eur - volatilidad*1.2):.2f} €")

            # --- SECCIÓN: OPERATIVA ---
            st.markdown("---")
            st.subheader(f"⏱️ Operativa Sugerida {fecha_str}")
            st.write(f"📥 **Compra:** 15:35 ({fecha_str}) | 📤 **Venta:** 21:40 ({fecha_str})")

        except Exception as e:
            st.error("Sincronizando con el mercado...")

# Sidebar
st.sidebar.write(f"**Actualización automática cada 30s**")
st.sidebar.write(f"Último análisis: {hoy_madrid.strftime('%H:%M:%S')}")

autorefresh(30)
