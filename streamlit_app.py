import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Terminal Pro IA - Estrategia", page_icon="💹", layout="wide")

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "NVDA").upper()

# --- DICCIONARIO DE TRADUCCIÓN ---
traducciones = {
    "strong_buy": "COMPRA FUERTE",
    "buy": "COMPRAR",
    "hold": "MANTENER",
    "neutral": "NEUTRAL",
    "sell": "VENDER",
    "strong_sell": "VENTA FUERTE",
    "underperform": "BAJO RENDIMIENTO",
    "none": "SIN CALIFICACIÓN"
}

# --- LÓGICA DE CALENDARIO ---
hoy = datetime.now()
dia_semana = hoy.weekday() 
if dia_semana >= 5: # Fin de semana
    fecha_analisis = hoy + timedelta(days=(7 - dia_semana))
else:
    fecha_analisis = hoy
fecha_str = fecha_analisis.strftime("%d/%m/%Y")

# --- LÓGICA DE CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Analizando datos de mercado para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            try: info = accion.info
            except: info = {}

            # --- SECCIÓN 1: ESTADO DEL MERCADO ---
            st.subheader("🏦 Estado del Mercado Global")
            hora_ny = (datetime.utcnow() - timedelta(hours=4)).time()
            mercado_usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and 
                                  hora_ny <= datetime.strptime("16:00", "%H:%M").time() and dia_semana < 5)
            
            if dia_semana >= 5:
                st.warning(f"⚠️ Mercado cerrado. Análisis estratégico para el {fecha_str}.")
            
            st.markdown(f"**Estado actual (EE.UU.):** :{'green' if mercado_usa_abierto else 'red'}[{'ABIERTO' if mercado_usa_abierto else 'CERRADO'}]")
            st.write("**Horario Regular (España):** 15:30 a 22:00")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS Y APERTURA (COLORES PERSONALIZADOS) ---
            col1, col2, col3, col4 = st.columns(4)
            precio_real_eur = f_info.last_price * cambio
            apertura_estimada = (info.get('regularMarketOpen', f_info.last_price)) * cambio
            
            # Precios de Bid y Ask
            precio_bid = info.get('bid', f_info.last_price) * cambio
            precio_ask = info.get('ask', f_info.last_price) * cambio

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio APERTURA", f"{apertura_estimada:.2f} €")
            
            # Formateo con colores solicitados
            col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{precio_bid:.2f} €</h2>", unsafe_allow_html=True)
            
            col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
            col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{precio_ask:.2f} €</h2>", unsafe_allow_html=True)

            # --- SECCIÓN 3: ESTRATEGIA DE ENTRADA Y SALIDA ---
            st.markdown("---")
            st.subheader(f"🚀 Estrategia Maestra de Inversión ({fecha_str})")
            
            rec_key = info.get('recommendationKey', 'none').lower()
            tendencia_alcista = f_info.last_price > hist['Close'].iloc[-2]
            
            e1, e2 = st.columns(2)
            
            with e1:
                st.markdown("### 📥 ¿A qué hora me interesa COMPRAR?")
                if rec_key in ['strong_buy', 'buy'] and tendencia_alcista:
                    st.success("**HORA ÓPTIMA: 15:35 - 15:50**")
                    st.write("Confirmación de analistas y chat: Entra pronto para capturar el impulso.")
                else:
                    st.warning("**HORA ÓPTIMA: 18:30 - 19:30**")
                    st.write("Mejor esperar a la calma de la tarde para comprar más barato.")

            with e2:
                st.markdown("### 📤 ¿A qué hora me interesa VENDER?")
                if tendencia_alcista:
                    st.error("**HORA ÓPTIMA: 21:40 - 21:55**")
                    st.write("Momento de máxima ganancia antes de que cierren las instituciones.")
                else:
                    st.error("**HORA ÓPTIMA: 16:30 - 17:00**")
                    st.write("Salida defensiva: Vende en el primer rebote tras la apertura.")

            # --- SECCIÓN 4: PROYECCIONES DE IMPORTES ---
            st.markdown("---")
            st.subheader("📊 Límites de Movimiento Estimados")
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            imp_subida = volatilidad_avg * 0.75
            imp_bajada = volatilidad_avg * 0.60
            
            m1, m2 = st.columns(2)
            m1.write(f"🟢 **Subida prevista:** +{imp_subida:.2f} € (Máximo: {(precio_real_eur + imp_subida):.2f} €)")
            m2.write(f"🔴 **Bajada prevista:** -{imp_bajada:.2f} € (Mínimo: {(precio_real_eur - imp_bajada):.2f} €)")

            # --- SECCIÓN 5: DECISIÓN DE EXPERTOS ---
            st.markdown("---")
            st.subheader("🎯 Consenso de Analistas")
            rec_esp = traducciones.get(rec_key, "NEUTRAL")
            target_mean = info.get('targetMeanPrice', 0)
            
            c1, c2 = st.columns(2)
            color_rec = "green" if rec_key in ['strong_buy', 'buy'] else "red" if rec_key in ['underperform', 'sell'] else "orange"
            c1.markdown(f"<h2 style='color:{color_rec};'>{rec_esp}</h2>", unsafe_allow_html=True)
            c2.info(f"Objetivo medio analistas: {target_mean * cambio:.2f} € | Tendencia: {'ALCISTA' if tendencia_alcista else 'BAJISTA'}")

        except Exception as e:
            st.error(f"Error al analizar el Ticker {ticker}.")

st.sidebar.write(f"**Fecha:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
