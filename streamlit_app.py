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

# --- LÓGICA DE CAMBIO EUR/USD ---
hoy = datetime.now()
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Analizando proyecciones para {ticker}...'):
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
                                  hoy.weekday() < 5)
            
            status_color = "green" if mercado_usa_abierto else "red"
            status_text = "ABIERTO" if mercado_usa_abierto else "CERRADO"
            
            st.markdown(f"**Estado actual (EE.UU.):** :{status_color}[{status_text}]")
            st.write("**Horario Regular (España):** 15:30 a 22:00 | **Horario Madrid:** 09:00 a 17:30")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS EN TIEMPO REAL ---
            col1, col2, col3 = st.columns(3)
            
            precio_real_eur = f_info.last_price * cambio
            precio_compra_eur = info.get('bid', f_info.last_price) * cambio 
            precio_venta_eur = info.get('ask', f_info.last_price) * cambio  

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio de COMPRA (Oferta)", f"{precio_compra_eur:.2f} €")
            col3.metric("Precio de VENTA (Demanda)", f"{precio_venta_eur:.2f} €")

            # --- SECCIÓN: PROYECCIÓN DE MÁXIMOS Y HORARIOS ---
            st.markdown("---")
            st.subheader("🚀 Proyección de Impulso Diario")
            
            rango_diario = (hist['High'] - hist['Low']).mean() * cambio
            maximo_estimado = precio_real_eur + (rango_diario * 0.5)
            
            hora_actual_es = datetime.now().hour
            if hora_actual_es < 16:
                hora_pico = "15:45 - 16:15 (Apertura de EE.UU.)"
            elif 16 <= hora_actual_es < 20:
                hora_pico = "17:30 - 18:00 (Cierre de Europa)"
            else:
                hora_pico = "21:30 - 21:50 (Cierre de EE.UU.)"

            p1, p2 = st.columns(2)
            p1.metric("Máximo Estimado Hoy", f"{maximo_estimado:.2f} €", f"+{((maximo_estimado/precio_real_eur)-1)*100:.2f}%")
            p2.metric("Hora de mayor movimiento", hora_pico)

            # --- SECCIÓN 3: DECISIÓN ESTRATÉGICA ---
            st.markdown("---")
            st.subheader("🎯 Decisión de los Expertos")
            
            target_mean = info.get('targetMeanPrice', 0)
            rec_key_raw = info.get('recommendationKey', 'none').lower()
            rec_esp = traducciones.get(rec_key_raw, "NEUTRAL")
            
            c1, c2 = st.columns(2)
            
            if rec_key_raw in ['strong_buy', 'buy'] or (target_mean and f_info.last_price < target_mean):
                c1.markdown(f"<h2 style='color:green;'>{rec_esp} ✅</h2>", unsafe_allow_html=True)
                c2.success(f"Los grandes bancos están comprando. Objetivo: {target_mean * cambio:.2f} €")
            elif rec_key_raw in ['underperform', 'sell', 'strong_sell']:
                c1.markdown(f"<h2 style='color:red;'>{rec_esp} 🚨</h2>", unsafe_allow_html=True)
                c2.error("Los expertos sugieren vender o tener mucho cuidado.")
            else:
                c1.markdown(f"<h2 style='color:orange;'>{rec_esp} ⚖️</h2>", unsafe_allow_html=True)
                c2.warning("No hay una opinión clara. Mejor esperar.")

            # --- SECCIÓN 4: PRONÓSTICO Y EXPLICACIÓN DE HORARIOS ---
            st.markdown("---")
            if not hist.empty:
                st.subheader(f"🔮 ¿Qué esperar hoy?")
                col_pred, col_hora_det = st.columns(2)
                
                with col_pred:
                    st.markdown("**Tendencia de la acción:**")
                    if f_info.last_price > hist['Close'].iloc[-2]:
                        st.success("🚀 VA HACIA ARRIBA (Sigue subiendo)")
                    else:
                        st.error("📉 VA HACIA ABAJO (Está bajando)")

                with col_hora_det:
                    st.markdown("**Momentos clave para mirar el móvil:**")
                    st.write("⏱️ **15:30 a 16:15:** Cuando abre el mercado en Nueva York y el precio se mueve con mucha fuerza.")
                    st.write("⏱️ **21:45 a 22:00:** Justo antes de cerrar, cuando los grandes inversores deciden sus posiciones finales.")

        except Exception as e:
            st.error(f"Error al cargar los datos. Inténtalo de nuevo.")

st.sidebar.write(f"**Actualizado:** {hoy.strftime('%H:%M:%S')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
