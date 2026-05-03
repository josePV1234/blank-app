import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Terminal Pro IA - Trade Republic", page_icon="💹", layout="wide")

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
    with st.spinner(f'Analizando datos para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            try: info = accion.info
            except: info = {}

            # --- SECCIÓN 1: ESTADO DE LOS MERCADOS ---
            st.subheader("🏦 Estado de los Mercados Globales")
            hora_actual = datetime.now().time()
            
            # 1. Mercado USA
            hora_ny = (datetime.utcnow() - timedelta(hours=4)).time()
            usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and 
                           hora_ny <= datetime.strptime("16:00", "%H:%M").time() and dia_semana < 5)
            
            # 2. Mercado Europeo Estándar (Madrid, Frankfurt, París)
            euro_abierto = (hora_actual >= datetime.strptime("09:00", "%H:%M").time() and 
                            hora_actual <= datetime.strptime("17:30", "%H:%M").time() and dia_semana < 5)
            
            # 3. Horario Especial TRADE REPUBLIC (LS Exchange)
            tr_abierto = (hora_actual >= datetime.strptime("07:30", "%H:%M").time() and 
                          hora_actual <= datetime.strptime("23:00", "%H:%M").time() and dia_semana < 5)

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
            col_m2.markdown(f"**Bolsa USA:** :{'green' if usa_abierto else 'red'}[{'ABIERTA' if usa_abierto else 'CERRADA'}]")
            col_m3.info(f"**Trade Republic (LS Exchange):** :{'green' if tr_abierto else 'red'}[{'ACTIVO' if tr_abierto else 'INACTIVO'}]")
            
            st.caption("Nota: Trade Republic permite operar de 07:30 a 23:00 de lunes a viernes.")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS Y APERTURA (COLORES PERSONALIZADOS) ---
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
                    st.write("Aprovecha la apertura USA. En Trade Republic tendrás el spread más ajustado aquí.")
                else:
                    st.warning("**HORA ÓPTIMA: 09:15 - 10:30**")
                    st.write("Mejor momento para valores europeos tras la apertura de Madrid/Frankfurt.")

            with e2:
                st.markdown("### 📤 ¿A qué hora me interesa VENDER?")
                st.error("**HORA ÓPTIMA: 21:30 - 22:00**")
                st.write("Trade Republic sigue abierto. Es el momento ideal para capturar cierres institucionales de USA.")

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
            c2.info(f"Objetivo medio analistas: {target_mean * cambio:.2f} €")

        except Exception as e:
            st.error(f"Error al analizar el Ticker {ticker}.")

st.sidebar.write(f"**Fecha:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
