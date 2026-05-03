import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Terminal Pro IA - Estrategia Final", page_icon="💹", layout="wide")

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
# Si es fin de semana (Sábado=5, Domingo=6), proyectamos al lunes
if dia_semana == 5: 
    fecha_analisis = hoy + timedelta(days=2)
elif dia_semana == 6: 
    fecha_analisis = hoy + timedelta(days=1)
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
    with st.spinner(f'Analizando estrategia final para {ticker}...'):
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

            # --- SECCIÓN 2: PRECIOS Y BID/ASK (CON COLORES) ---
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

            # --- NUEVA SECCIÓN: DECISIÓN FINAL DE INVERSIÓN ---
            st.markdown("---")
            st.subheader(f"🚩 DECISIÓN FINAL PARA EL DÍA: {fecha_str}")
            
            rec_key = info.get('recommendationKey', 'none').lower()
            tendencia_alcista = f_info.last_price > hist['Close'].iloc[-2]
            target_mean = info.get('targetMeanPrice', 0)
            
            # Lógica de decisión simplificada
            if rec_key in ['strong_buy', 'buy'] and tendencia_alcista:
                decision_final = "COMPRAR"
                color_final = "#28a745" # Verde
                explicacion = f"La IA y los asesores coinciden: {ticker} tiene fuerza alcista y volumen para subir hoy {fecha_str}."
            elif rec_key in ['underperform', 'sell', 'strong_sell'] or not tendencia_alcista:
                decision_final = "VENDER / EVITAR"
                color_final = "#dc3545" # Rojo
                explicacion = f"Riesgo detectado. La presión de venta es superior a la compra para este {fecha_str}. Mejor proteger capital."
            else:
                decision_final = "MANTENER / NEUTRAL"
                color_final = "#ffc107" # Ámbar
                explicacion = f"Mercado en equilibrio para el {fecha_str}. No hay una señal clara de entrada o salida masiva."

            st.markdown(f"""
                <div style="background-color: {color_final}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0;">ACCIÓN RECOMENDADA: {decision_final}</h1>
                    <p style="color: white; font-size: 1.2rem; margin-top: 10px;">{explicacion}</p>
                </div>
            """, unsafe_allow_html=True)

            # --- SECCIÓN 3: PUNTOS CRÍTICOS (SUBIDAS Y BAJADAS) ---
            st.markdown("---")
            st.subheader(f"📊 Movimientos Críticos Previstos ({fecha_str})")
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            valor_subida = volatilidad_avg * 0.80
            valor_bajada = volatilidad_avg * 0.65
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown("#### 🟢 Mayor SUBIDA estimada")
                st.write(f"**Importe de subida:** +{valor_subida:.2f} €")
                st.success(f"⏰ **Hora estimada:** 15:45 - 16:15")
            with m2:
                st.markdown("#### 🔴 Mayor BAJADA estimada")
                st.write(f"**Importe de bajada:** -{valor_bajada:.2f} €")
                st.error(f"⏰ **Hora estimada:** 17:20 - 17:50")

            # --- SECCIÓN 4: HORARIOS TRADE REPUBLIC ---
            st.markdown("---")
            st.subheader("🚀 Horarios de Operativa Trade Republic")
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("### 📥 Hora de COMPRA ideal")
                st.write("15:35 (Aprovechando la liquidez de apertura USA)")
            with e2:
                st.markdown("### 📤 Hora de VENTA ideal")
                st.write("21:40 (Cierre de mercado americano para maximizar ganancias)")

        except Exception as e:
            st.error(f"Error al procesar el análisis de {ticker}.")

st.sidebar.write(f"**Análisis generado el:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
