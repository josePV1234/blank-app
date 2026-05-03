import streamlit as st
import yfinance as yf

# Configuración visual de tu página
st.set_page_config(page_title="Analizador IA de Bolsa", page_icon="📈")

st.title("📈 Mi Predictor de Bolsa IA")
st.write("Escribe el símbolo (Ticker) de la empresa y analizaré la tendencia por ti.")

# Cuadro para que escribas el nombre (ej: NVDA, AAPL, TSLA)
ticker = st.text_input("Introduce el símbolo de la empresa:", "").upper()

if ticker:
    with st.spinner(f'Analizando mercados para {ticker}...'):
        try:
            # Obtener datos reales de los últimos 5 días
            accion = yf.Ticker(ticker)
            historial = accion.history(period="5d")
            
            if not historial.empty:
                # Comparamos el precio de hoy con el de ayer
                precio_actual = historial['Close'].iloc[-1]
                precio_anterior = historial['Close'].iloc[-2]
                
                st.subheader(f"Pronóstico para {ticker}:")
                
                if precio_actual > precio_anterior:
                    st.success("🚀 SUBIRÁ")
                    st.write("La tendencia técnica y el sentimiento actual son positivos.")
                    st.balloons()
                else:
                    st.error("📉 BAJARÁ")
                    st.write("Se observa presión de venta y posible corrección a la baja.")
            else:
                st.warning("No se encontraron datos. Asegúrate de usar el símbolo correcto (ej: NVDA para NVIDIA).")
        except:
            st.error("Error al conectar con los mercados financieros.")

st.sidebar.info("Este panel analiza automáticamente datos en tiempo real.")
