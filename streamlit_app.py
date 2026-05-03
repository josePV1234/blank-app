import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

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

# --- LÓGICA DE CALENDARIO Y FECHAS ---
hoy = datetime.now()
dia_semana = hoy.weekday() 

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
    with st.spinner(f'Realizando análisis profundo de {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            
            try:
                info = accion.info
            except:
                info = {}

            # --- SECCIÓN 1: ESTADO DEL MERCADO ---
            st.subheader("🏦 Estado del Mercado Global")
            hora_ny = (datetime.utcnow() - timedelta(hours=4)).time()
            mercado_usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and 
                                  hora_ny <= datetime.strptime("16:00", "%H:%M").time() and 
                                  dia_semana < 5)
            
            status_color = "green" if mercado_usa_abierto else "red"
            status_text = "ABIERTO" if mercado_usa_abierto else "CERRADO"
            
            if dia_semana >= 5:
                st.warning(f"⚠️ Mercado cerrado. Proyectando para el {fecha_str}.")
            
            st.markdown(f"**Estado actual (EE.UU.):** :{status_color}[{status_text}]")
            st.write("**Horario Regular (España):** 15:30 a 22:00 | **Horario Madrid:** 09:00 a 17:30")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS EN TIEMPO REAL ---
            col1, col2, col3 = st.columns(3)
            precio_real_eur = f_info.last_price * cambio
            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio de COMPRA (Oferta)", f"{(info.get('bid', f_info.last_price) * cambio):.2f} €")
            col3.metric("Precio de VENTA (Demanda)", f"{(info.get('ask', f_info.last_price) * cambio):.2f} €")

            # --- NUEVA SECCIÓN: ANÁLISIS DE PUNTOS CRÍTICOS (SUBIDAS Y BAJADAS) ---
            st.markdown("---")
            st.subheader(f"📊 Análisis de Movimientos Previstos ({fecha_str})")
            
            # Cálculo de volatilidad esperada
            volatilidad_avg = (hist['High'] - hist['Low']).mean() * cambio
            importe_subida = volatilidad_avg * 0.75
            importe_bajada = volatilidad_avg * 0.60
            
            m1, m2 = st.columns(2)
            
            with m1:
                st.markdown("#### 🟢 Previsión de SUBIDA")
                st.write(f"**Importe estimado de subida:** +{importe_subida:.2f} €")
                st.write(f"**Techo máximo esperado:** {(precio_real_eur + importe_subida):.2f} €")
                st.info("⏰ **Hora prevista de pico máximo:** 15:45 - 16:30 (Impulso inicial de apertura)")

            with m2:
                st.markdown("#### 🔴 Previsión de BAJADA")
                st.write(f"**Importe estimado de bajada:** -{importe_bajada:.2f} €")
                st.write(f"**Suelo mínimo esperado:** {(precio_real_eur - importe_bajada):.2f} €")
                st.info("⏰ **Hora prevista de caída/ajuste:** 17:15 - 18:00 (Cierre de mercados europeos)")

            # --- SECCIÓN 3: DECISIÓN DE EXPERTOS ---
            st.markdown("---")
            st.subheader("🎯 Decisión de los Expertos")
            rec_key_raw = info.get('recommendationKey', 'none').lower()
            rec_esp = traducciones.get(rec_key_raw, "NEUTRAL")
            target_mean = info.get('targetMeanPrice', 0)
            
            c1, c2 = st.columns(2)
            if rec_key_raw in ['strong_buy', 'buy']:
                c1.markdown(f"<h2 style='color:green;'>{rec_esp} ✅</h2>", unsafe_allow_html=True)
                c2.success(f"Los bancos están acumulando. Objetivo analista: {target_mean * cambio:.2f} €")
            elif rec_key_raw in ['underperform', 'sell']:
                c1.markdown(f"<h2 style='color:red;'>{rec_esp} 🚨</h2>", unsafe_allow_html=True)
                c2.error("Los analistas sugieren precaución o venta.")
            else:
                c1.markdown(f"<h2 style='color:orange;'>{rec_esp} ⚖️</h2>", unsafe_allow_html=True)
                c2.warning("Consenso neutral. Esperar a confirmación de tendencia.")

            # --- SECCIÓN 4: PRONÓSTICO Y EXPLICACIÓN ---
            st.markdown("---")
            if not hist.empty:
                st.subheader(f"🔮 Resumen para el inversor")
                col_pred, col_hora_det = st.columns(2)
                with col_pred:
                    if f_info.last_price > hist['Close'].iloc[-2]:
                        st.success("🚀 TENDENCIA: ALCISTA (El mercado tiene fuerza compradora)")
                    else:
                        st.error("📉 TENDENCIA: BAJISTA (El mercado tiene presión de venta)")

                with col_hora_det:
                    st.write("⏱️ **Mañana (15:30):** Mucha fuerza, ideal para ver la dirección del día.")
                    st.write("⏱️ **Tarde (21:45):** Los 'peces gordos' cierran sus operaciones.")

        except Exception as e:
            st.error(f"Error al analizar el Ticker. Asegúrate de que sea correcto.")

st.sidebar.write(f"**Análisis del:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
