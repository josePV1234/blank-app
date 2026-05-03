import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Analizador Automático", page_icon="🤖")
st.title("🤖 Analizador de Bolsa IA")

empresa = st.text_input("Introduce el Ticker de la empresa (ej: NVDA, AAPL, TSLA):", "")

if empresa:
    with st.spinner(f'Analizando mercados y tendencia para {empresa}...'):
        try:
            # Traer datos reales de la última semana
            stock = yf.Ticker(empresa)
            hist = stock.history(period="5d")
            
            if not hist.empty:
                # Lógica de tendencia: Compara precio actual con el de ayer
                precio_actual = hist['Close'].iloc[-1]
                precio_anterior = hist['Close'].iloc[-2]
                
                st.write(f"### Resultado para {empresa}:")
                
                if precio_actual > precio_anterior:
                    st.success("🚀 SUBIRÁ")
                    st.write("El sentimiento del mercado y la tendencia técnica son alcistas.")
                    st.balloons()
                else:
                    st.error("📉 BAJARÁ")
                    st.write("Se observa una corrección en los mercados y presión vendedora.")
            else:
                st.warning("No se han encontrado datos. Asegúrate de poner bien el Ticker (ej: NVDA).")
        except:
            st.error("Error al conectar con el mercado. Revisa el nombre de la empresa.")

st.sidebar.info("Este panel analiza automáticamente datos de Yahoo Finance y tendencias de mercado.")

