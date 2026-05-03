import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "").upper()

# Calcular fechas y cambio EUR/USD
hoy = datetime.now()
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 # Valor de seguridad

if ticker:
    with st.spinner(f'Conectando con el mercado para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            info = accion.info
            
            # --- SECCIÓN 1: ESTADO DEL MERCADO ---
            st.subheader("🏦 Estado del Mercado Global")
            # Determinar estado (Lógica simplificada por zona horaria)
            hora_ny = (datetime.utcnow() - timedelta(hours=4)).time() # Hora NY aprox
            mercado_usa_abierto = (hora_ny >= datetime.strptime("09:30", "%H:%M").time() and 
                                  hora_ny <= datetime.strptime("16:00", "%H:%M").time() and 
                                  hoy.weekday() < 5)
            
            status_color = "green" if mercado_usa_abierto else "red"
            status_text = "ABIERTO" if mercado_usa_abierto else "CERRADO"
            
            st.markdown(f"**Estado actual (EE.UU.):** :{status_color}[{status_text}]")
            st.write("**Horario Regular (España):** 15:30 a 22:00 | **Horario Madrid:** 09:00 a 17:30")

            st.markdown("---")

            # --- SECCIÓN 2: PRECIOS COMPRA/VENTA Y REAL ---
            col1, col2, col3 = st.columns(3)
            
            precio_real_eur = f_info.last_price * cambio
            precio_compra_eur = info.get('bid', f_info.last_price) * cambio # Bid
            precio_venta_eur = info.get('ask', f_info.last_price) * cambio  # Ask

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio de COMPRA (Bid)", f"{precio_compra_eur:.2f} €")
            col3.metric("Precio de VENTA (Ask)", f"{precio_venta_eur:.2f} €")

            # --- SECCIÓN 3: PREDICCIÓN Y ANÁLISIS ---
            st.markdown("---")
            hist = accion.history(period="5d")
            if not hist.empty:
                precio_cierre_hoy = hist['Close'].iloc[-1] * cambio
                rec_en = info.get('recommendationKey', 'none')
                
                st.subheader(f"🔮 Pronóstico para la próxima sesión:")
                if rec_en in ['strong_buy', 'buy'] and f_info.last_price > hist['Close'].iloc[-2]:
                    st.success("🚀 SE PREVÉ QUE LA ACCIÓN SUBIRÁ")
                else:
                    st.error("📉 SE PREVÉ QUE LA ACCIÓN TENDRÁ PRESIÓN BAJISTA")
                
                st.info(f"💡 **Recomendación Asesores:** {rec_en.upper()}")

        except Exception as e:
            st.error(f"Error al obtener datos en tiempo real.")

st.sidebar.write(f"**Actualizado:** {hoy.strftime('%H:%M:%S')}")
