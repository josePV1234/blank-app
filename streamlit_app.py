import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Analizador IA", page_icon="📈")
st.title("📈 Mi Predictor de Bolsa IA")
st.write("Escribe el símbolo (ej: NVDA, AAPL) para ver la tendencia.")

ticker = st.text_input("Introduce el símbolo:", "").upper()

if ticker:
    with st.spinner(f'Analizando {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="5d")
            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                st.subheader(f"Resultado para {ticker}:")
                if precio_hoy > precio_ayer:
                    st.success("🚀 SUBIRÁ")
                    st.balloons()
                else:
                    st.error("📉 BAJARÁ")
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error de conexión.")
