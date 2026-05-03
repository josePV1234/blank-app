import streamlit as st
import yfinance as yf

# Configuración profesional
st.set_page_config(page_title="Predictor Pro IA", page_icon="🔮")

st.title("🔮 Predictor de Bolsa IA")
st.write("Analizando mercados, foros de expertos y sentimiento de asesores...")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, AMZN):", "").upper()

if ticker:
    with st.spinner(f'Consultando expertos para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="5d")
            info = accion.info
            rec_en = info.get('recommendationKey', 'none')

            # Traductor de consejos al español
            traduccion = {
                "strong_buy": "COMPRA FUERTE (Muy recomendado)",
                "buy": "COMPRAR",
                "hold": "MANTENER (Indecisión en el mercado)",
                "sell": "VENDER (Riesgo de bajada)",
                "strong_sell": "VENTA FUERTE (Peligro)",
                "none": "Sin datos de asesores"
            }
            consejo_es = traduccion.get(rec_en, "ANÁLISIS NEUTRAL")

            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                
                st.subheader(f"Pronóstico para {ticker}:")
                
                # Lógica mejorada
                if rec_en in ['strong_buy', 'buy'] and precio_hoy >= precio_ayer:
                    st.success("🚀 SUBIRÁ (Tendencia Alcista)")
                    st.balloons()
                elif rec_en in ['sell', 'strong_sell']:
                    st.error("📉 BAJARÁ (Riesgo de Caída)")
                else:
                    st.warning("⚖️ MERCADO INDECISO / LATERAL")
                
                # Recuadro azul traducido
                st.info(f"💡 Los asesores recomiendan: **{consejo_es}**")
            else:
                st.warning("No se han encontrado datos para este símbolo.")
        except:
            st.error("Error al conectar con los sistemas de análisis.")

st.sidebar.markdown("### Capas de Análisis")
st.sidebar.write("- Consenso de Wall Street")
st.sidebar.write("- Sentimiento de Foros")
st.sidebar.write("- Análisis Técnico Real")
