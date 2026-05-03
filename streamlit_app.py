import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Terminal Pro IA - Estrategia Total", page_icon="💹", layout="wide")

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

# --- LÓGICA DE CAMBIO EUR/USD ---
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Realizando análisis profundo para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            try: info = accion.info
            except: info = {}

            # --- SECCIÓN 1: ESTADO DE LOS MERCADOS (Incluyendo Europa y Trade Republic) ---
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

            # --- SECCIÓN 2: PRECIOS, APERTURA Y BID/ASK (CON COLORES) ---
            col1, col2, col3, col4 = st.columns(4)
            precio_real_eur = f_info.last_price * cambio
            apertura_estimada = (info.get('regularMarketOpen', f_info.last_price)) * cambio
            precio_bid = info.get('bid', f_info.last_price) * cambio
            precio_ask = info.get('ask', f_info.last_price) * cambio

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio APERTURA", f"{apertura_estimada:.2f} €")
            
            col3.markdown(f"<p style='color:#28a745; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE COMPRA OFRECE (Bid)</p>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='color:#28a745; margin-top:0;'>{precio_bid:.2f} €</h2>", unsafe_allow_html=True)
            
            col4.markdown(f"<p style='color:#007bff; font-size:16px; font-weight:bold; margin-bottom:0;'>EL QUE VENDE PIDE (Ask)</p>", unsafe_allow_html=True)
            col4.markdown(f"<h2 style='color:#007bff; margin-top:0;'>{precio_ask:.2f} €</h2>", unsafe_allow_html=True)

            # --- SECCIÓN 3: PUNTOS CRÍTICOS (MAYOR SUBIDA Y BAJADA) ---
            st.markdown("---")
            st.subheader(f"📊 Análisis de Movimientos Críticos Previstos ({fecha_str})")
            
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            valor_subida_esperada = volatilidad_avg * 0.80
            valor_bajada_esperada = volatilidad_avg * 0.65
            
            m1, m2 = st.columns(2)
            
            with m1:
                st.markdown("#### 🟢 Mayor SUBIDA estimada")
                st.write(f"**Importe de subida:** +{valor_subida_esperada:.2f} €")
                st.write(f"**Precio máximo previsto:** {(precio_real_eur + valor_subida_esperada):.2f} €")
                st.success(f"⏰ **Hora estimada:** 15:45 - 16:15")
                st.caption("Coincide con la entrada de volumen masivo de Nueva York.")

            with m2:
                st.markdown("#### 🔴 Mayor BAJADA estimada")
                st.write(f"**Importe de bajada:** -{valor_bajada_esperada:.2f} €")
                st.write(f"**Precio mínimo previsto:** {(precio_real_eur - valor_bajada_esperada):.2f} €")
                st.error(f"⏰ **Hora estimada:** 17:20 - 17:50")
                st.caption("Coincide con la toma de beneficios del mercado europeo.")

            # --- SECCIÓN 4: ESTRATEGIA TRADE REPUBLIC (CUÁNDO COMPRAR/VENDER) ---
            st.markdown("---")
            st.subheader("🚀 Estrategia de Operativa Recomendada")
            rec_key = info.get('recommendationKey', 'none').lower()
            tendencia_alcista = f_info.last_price > hist['Close'].iloc[-2]
            
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("### 📥 ¿A qué hora me interesa COMPRAR?")
                if rec_key in ['strong_buy', 'buy']:
                    st.success("**HORA ÓPTIMA: 15:35 (Apertura USA)**")
                else:
                    st.warning("**HORA ÓPTIMA: 18:30 (Calma Europea)**")
            with e2:
                st.markdown("### 📤 ¿A qué hora me interesa VENDER?")
                st.error("**HORA ÓPTIMA: 21:40 (Cierre Institucional)**")
                st.write("Aprovecha que Trade Republic sigue abierto para capturar el último impulso de USA.")

            # --- SECCIÓN 5: DECISIÓN DE ANALISTAS ---
            st.markdown("---")
            st.subheader("🎯 Consenso de Analistas (Wall Street)")
            rec_esp = traducciones.get(rec_key, "NEUTRAL")
            target_mean = info.get('targetMeanPrice', 0)
            
            c1, c2 = st.columns(2)
            color_rec = "green" if rec_key in ['strong_buy', 'buy'] else "red" if rec_key in ['underperform', 'sell'] else "orange"
            c1.markdown(f"<h2 style='color:{color_rec};'>{rec_esp}</h2>", unsafe_allow_html=True)
            c2.info(f"Precio objetivo analistas: {target_mean * cambio:.2f} € | Tendencia: {'ALCISTA' if tendencia_alcista else 'BAJISTA'}")

        except Exception as e:
            st.error(f"Error al analizar el Ticker {ticker}.")

st.sidebar.write(f"**Fecha actual:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio aplicado: 1 USD = {cambio:.4f} EUR")
