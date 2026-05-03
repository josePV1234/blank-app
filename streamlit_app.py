import streamlit as st
import yfinance as yf

# Configuración profesional
st.set_page_config(page_title="Predictor Pro Mañana", page_icon="🔮")

st.title("🔮 Predictor de Bolsa para Mañana")
st.write("Analizando comportamiento de mercados y expertos para la apertura del próximo día hábil...")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, AMZN):", "").upper()

if ticker:
    with st.spinner(f'Calculando probabilidad para mañana en {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="5d")
            info = accion.info
            rec_en = info.get('recommendationKey', 'none')

            traduccion = {
                "strong_buy": "COMPRA FUERTE (Muy recomendado)",
                "buy": "COMPRAR",
                "hold": "MANTENER (Indecisión)",
                "sell": "VENDER",
                "strong_sell": "VENTA FUERTE",
                "none": "Sin datos de asesores"
            }
            consejo_es = traduccion.get(rec_en, "ANÁLISIS NEUTRAL")

            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                
                st.subheader(f"Pronóstico para la próxima sesión de {ticker}:")
                
                # Lógica combinada con explicaciones detalladas
                if rec_en in ['strong_buy', 'buy'] and precio_hoy > precio_ayer:
                    st.success("🚀 SUBIRÁ")
                    st.write("Análisis: Existe una alineación positiva entre el precio y los expertos. Hay fuerza alcista para la apertura de mañana.")
                    st.balloons()
                elif rec_en in ['strong_buy', 'buy'] and precio_hoy <= precio_ayer:
                    st.warning("⚖️ MERCADO INDECISO / LATERAL")
                    st.write("Análisis: Aunque los expertos confían en el valor, ahora mismo el precio no tiene fuerza para dispararse de inmediato.")
                elif rec_en in ['sell', 'strong_sell']:
                    st.error("📉 BAJARÁ")
                    st.write("Análisis: Se detecta presión vendedora. Es probable que el comportamiento de mañana sea bajista.")
                else:
                    st.warning("⚖️ RANGO LATERAL")
                    st.write("Análisis: Sin una tendencia clara. El precio se mantiene estable sin mucha fuerza para dispararse.")
                
                st.info(f"💡 Los asesores califican la acción como: **{consejo_es}**")
            else:
                st.warning("No se han encontrado datos para este símbolo.")
        except:
            st.error("Error al conectar con los sistemas financieros.")

st.sidebar.info("Este panel predice el comportamiento para la apertura de la siguiente sesión bursátil.")
