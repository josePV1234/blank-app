import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

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
    with st.spinner(f'Analizando {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            f_info = accion.fast_info
            hist = accion.history(period="5d")
            
            # Intentar obtener info detallada, si falla usamos valores por defecto
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
            # Usar fast_info si el bid/ask de info falla
            precio_compra_eur = info.get('bid', f_info.last_price) * cambio 
            precio_venta_eur = info.get('ask', f_info.last_price) * cambio  

            col1.metric("Último Precio Real", f"{precio_real_eur:.2f} €")
            col2.metric("Precio de COMPRA (Oferta)", f"{precio_compra_eur:.2f} €")
            col3.metric("Precio de VENTA (Demanda)", f"{precio_venta_eur:.2f} €")

            # --- SECCIÓN 3: DECISIÓN ESTRATÉGICA ---
            st.markdown("---")
            st.subheader("🎯 Decisión Estratégica Institucional")
            
            target_mean = info.get('targetMeanPrice', 0)
            rec_key_raw = info.get('recommendationKey', 'none').lower()
            rec_esp = traducciones.get(rec_key_raw, "NEUTRAL")
            
            c1, c2 = st.columns(2)
            
            # Lógica de recomendación con protección contra datos vacíos
            if rec_key_raw in ['strong_buy', 'buy'] or (target_mean and f_info.last_price < target_mean):
                c1.markdown(f"<h2 style='color:green;'>{rec_esp} ✅</h2>", unsafe_allow_html=True)
                texto_obj = f"Precio objetivo medio: {target_mean * cambio:.2f} €" if target_mean else "Tendencia de acumulación detectada."
                c2.success(f"Analistas sugieren posiciones alcistas. {texto_obj}")
            elif rec_key_raw in ['underperform', 'sell', 'strong_sell']:
                c1.markdown(f"<h2 style='color:red;'>{rec_esp} 🚨</h2>", unsafe_allow_html=True)
                c2.error("Alerta de analistas: Se detecta presión vendedora o sobrevaloración.")
            else:
                c1.markdown(f"<h2 style='color:orange;'>{rec_esp} ⚖️</h2>", unsafe_allow_html=True)
                c2.warning("Mercado en equilibrio o falta de consenso claro. Precaución.")

            # --- SECCIÓN 4: PRONÓSTICO Y HORARIOS ---
            st.markdown("---")
            if not hist.empty:
                st.subheader(f"🔮 Pronóstico y Horarios Clave")
                col_pred, col_hora = st.columns(2)
                
                with col_pred:
                    st.markdown("**Comportamiento para Mañana:**")
                    tendencia_subida = f_info.last_price > hist['Close'].iloc[-2]
                    if tendencia_subida:
                        st.success("🚀 SE PREVÉ TENDENCIA ALCISTA")
                    else:
                        st.error("📉 SE PREVÉ PRESIÓN BAJISTA")
                    st.info(f"💡 **Consenso de Asesores:** {rec_esp}")

                with col_hora:
                    st.markdown("**Mejores horas para operar (España):**")
                    st.write("⏱️ **15:30 - 16:15:** Apertura (Picos de volatilidad máxima).")
                    st.write("⏱️ **19:00 - 20:30:** Consolidación de la tendencia diaria.")
                    st.write("⏱️ **21:45 - 22:00:** Cierre (Movimiento de grandes fondos).")

        except Exception as e:
            st.error(f"Error técnico: No se han podido cargar los datos de {ticker}. Inténtalo de nuevo en unos segundos.")

st.sidebar.write(f"**Actualizado:** {hoy.strftime('%H:%M:%S')}")
st.sidebar.caption(f"Cambio aplicado: 1 USD = {cambio:.4f} EUR")
