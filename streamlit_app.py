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
    with st.spinner(f'IA analizando analistas y flujos para {ticker}...'):
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
                st.warning(f"⚠️ Mercado cerrado. Análisis estratégico para la apertura del {fecha_str}.")
            
            st.markdown(f"**Estado actual (EE.UU.):** :{'green' if mercado_usa_abierto else 'red'}[{'ABIERTO' if mercado_usa_abierto else 'CERRADO'}]")
            st.write("**Horario Regular (España):** 15:30 a 22:00")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS Y APERTURA ---
            col1, col2, col3, col4 = st.columns(4)
            precio_real_eur = f_info.last_price * cambio
            apertura_estimada = (info.get('regularMarketOpen', f_info.last_price)) * cambio
            
            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio APERTURA", f"{apertura_estimada:.2f} €")
            col3.metric("COMPRA (Oferta)", f"{(info.get('bid', f_info.last_price) * cambio):.2f} €")
            col4.metric("VENTA (Demanda)", f"{(info.get('ask', f_info.last_price) * cambio):.2f} €")

            # --- NUEVA SECCIÓN: ESTRATEGIA DE ENTRADA Y SALIDA (COMPRA/VENTA) ---
            st.markdown("---")
            st.subheader(f"🚀 Estrategia Maestra de Inversión ({fecha_str})")
            
            # Lógica de decisión IA basada en analistas y tendencia
            rec_key = info.get('recommendationKey', 'none').lower()
            tendencia_alcista = f_info.last_price > hist['Close'].iloc[-2]
            
            e1, e2 = st.columns(2)
            
            with e1:
                st.markdown("### 📥 ¿A qué hora me interesa COMPRAR?")
                if rec_key in ['strong_buy', 'buy'] and tendencia_alcista:
                    st.success("**HORA ÓPTIMA: 15:35 - 15:50**")
                    st.write("Aprovecha el impulso inicial. Los analistas y el chat institucional confirman fuerza de entrada.")
                else:
                    st.warning("**HORA ÓPTIMA: 18:30 - 19:30**")
                    st.write("Espera a que el mercado se calme. Interesa comprar cuando baje el volumen europeo para buscar un mejor precio.")

            with e2:
                st.markdown("### 📤 ¿A qué hora me interesa VENDER?")
                if tendencia_alcista:
                    st.error("**HORA ÓPTIMA: 21:40 - 21:55**")
                    st.write("Vende antes del cierre para capturar la subida del día generada por los fondos de inversión.")
                else:
                    st.error("**HORA ÓPTIMA: 16:30 - 17:00**")
                    st.write("Salida rápida. Si la tendencia es bajista, este es el punto donde suele haber un rebote temporal antes de seguir cayendo.")

            # --- SECCIÓN 3: PROYECCIONES DE IMPORTES ---
            st.markdown("---")
            st.subheader("📊 Límites de Movimiento Estimados")
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            imp_subida = volatilidad_avg * 0.75
            imp_bajada = volatilidad_avg * 0.60
            
            m1, m2 = st.columns(2)
            m1.write(f"🟢 **Subida prevista:** +{imp_subida:.2f} € (Máximo: {(precio_real_eur + imp_subida):.2f} €)")
            m2.write(f"🔴 **Bajada prevista:** -{imp_bajada:.2f} € (Mínimo: {(precio_real_eur - imp_bajada):.2f} €)")

            # --- SECCIÓN 4: DECISIÓN DE EXPERTOS ---
            st.markdown("---")
            st.subheader("🎯 Consenso de Analistas (Wall Street)")
            rec_esp = traducciones.get(rec_key, "NEUTRAL")
            target_mean = info.get('targetMeanPrice', 0)
            
            c1, c2 = st.columns(2)
            color_rec = "green" if rec_key in ['strong_buy', 'buy'] else "red" if rec_key in ['underperform', 'sell'] else "orange"
            c1.markdown(f"<h2 style='color:{color_rec};'>{rec_esp}</h2>", unsafe_allow_html=True)
            c2.info(f"Precio objetivo analistas: {target_mean * cambio:.2f} € | Tendencia: {'ALCISTA' if tendencia_alcista else 'BAJISTA'}")

        except Exception as e:
            st.error(f"Error en el análisis de datos.")

st.sidebar.write(f"**Fecha:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
