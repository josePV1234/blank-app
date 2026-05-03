import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Analizador IA de Bolsa", page_icon="📈")
st.title("📈 Mi Predictor de Bolsa IA")
st.write("Escribe el símbolo (Ticker) de la empresa y analizaré la tendencia por ti.")

ticker = st.text_input("Introduce el símbolo de la empresa (ej: NVDA):", "").upper()

if ticker:
    with st.spinner(f'Analizando mercados para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            historial = accion.history(period="5d")
            if not historial.empty:
                precio_actual = historial['Close'].iloc[-1]
                precio_anterior = historial['Close'].iloc[-2]
                st.subheader(f"Pronóstico para {ticker}:")
                if precio_actual > precio_anterior:
                    st.success("🚀 SUBIRÁ")
                    st.balloons()
                else:
                    st.error("📉 BAJARÁ")
            else:
                st.warning("No se encontraron datos. Usa códigos como NVDA o AAPL.")
        except:
            st.error("Error al conectar con los mercados.")
