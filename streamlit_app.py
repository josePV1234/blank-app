import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

st.title("💹 Terminal de Bolsa en Tiempo Real con Análisis de Expertos")

ticker = st.text_input("Introduce el Ticker (ej: NVDA, TSLA, SAN):", "").upper()

# --- DICCIONARIO DE TRADUCCIÓN ---
traducciones = {
    "strong_buy": "COMPRA FUERTE",
    "buy": "COMPRAR",
    "hold": "MANTENER",
    "neutral": "NEUTRAL",
    "sell": "VENDER",
    "strong_sell": "VENTA FUERTE",
    "underperform": "BAJO RENDIMIENTO",
    "none": "SIN DATOS"
}

# --- LÓGICA DE CAMBIO EUR/USD ---
hoy = datetime.now()
try:
    eur_usd_data = yf.Ticker("EURUSD=X").fast_info
    cambio = 1 / eur_usd_data.last_price
except:
    cambio = 0.92 

if ticker:
    with st.spinner(f'Conectando con el mercado para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            info = accion.info
            hist = accion.history(period="5d")
            
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

            # --- SECCIÓN 2: PRECIOS COMPRA/VENTA ---
            col1, col2, col3 = st.columns(3)
            
            precio_real_eur = f_info.last_price * cambio
            precio_compra_eur = info.get('bid', f_info.last_price) * cambio 
            precio_venta_eur = info.get('ask', f_info.last_price) * cambio  

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio de COMPRA (Bid)", f"{precio_compra_eur:.2f} €")
            col3.metric("Precio de VENTA (Ask)", f"{precio_venta_eur:.2f} €")

            # --- SECCIÓN 3: RECOMENDACIÓN ESTRATÉGICA (TRADUCIDA) ---
            st.markdown("---")
            st.subheader("🎯 Decisión Estratégica Institucional")
            
            target_mean = info.get('targetMeanPrice', 0)
            rec_key_raw = info.get('recommendationKey', 'none').lower()
            rec_esp = traducciones.get(rec_key_raw, rec_key_raw.upper())
            
            c1, c2 = st.columns()
            
            if rec_key_raw in ['strong_buy', 'buy']:
                c1.markdown(f"<h2 style='color:green;'>{rec_esp} ✅</h2>", unsafe_allow_html=True)
                c2.success(f"Analistas sugieren acumular. Precio objetivo: {target_mean * cambio:.2f} €")
            elif rec_key_raw in ['underperform', 'sell', 'strong_sell']:
                c1.markdown(f"<h2 style='color:red;'>{rec_esp} 🚨</h2>", unsafe_allow_html=True)
                c2.error("Riesgo de caída. Los analistas están reduciendo posiciones.")
            else:
                c1.markdown(f"<h2 style='color:orange;'>{rec_esp} ⚖️</h2>", unsafe_allow_html=True)
                c2.warning("Neutralidad en el mercado. No hay señales claras de entrada.")

            # --- SECCIÓN 4: PREDICCIÓN Y HORARIOS (TRADUCIDA) ---
            st.markdown("---")
            if not hist.empty:
                st.subheader(f"🔮 Pronóstico y Horarios Clave")
                
                col_pred, col_hora = st.columns(2)
                
                with col_pred:
                    st.markdown("**Comportamiento para Mañana:**")
                    if f_info.last_price > hist['Close'].iloc[-2]:
                        st.success("🚀 SE PREVÉ TENDENCIA ALCISTA")
                    else:
                        st.error("📉 SE PREVÉ PRESIÓN BAJISTA")
                    
                    st.info(f"💡 **Recomendación Asesores:** {rec_esp}")

                with col_hora:
                    st.markdown("**Mejores horas para operar (España):**")
                    st.write("⏱️ **15:30 - 16:15:** Apertura (Picos de volatilidad).")
                    st.write("⏱️ **19:00 - 20:30:** Consolidación.")
                    st.write("⏱️ **21:45 - 22:00:** Cierre institucional.")

        except Exception as e:
            st.error(f"Error al obtener datos. Revisa el Ticker.")

st.sidebar.write(f"**Actualizado:** {hoy.strftime('%H:%M:%S')}")
st.sidebar.caption(f"Cambio: 1 USD = {cambio:.4f} EUR")
