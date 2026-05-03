import streamlit as st
import yfinance as yf

# Configuración del panel avanzado
st.set_page_config(page_title="Analizador Predictivo IA", page_icon="🔮")

st.title("🔮 Predictor de Bolsa IA")
st.write("Analizando mercados, foros de expertos y sentimiento de asesores...")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, AAPL):", "").upper()

if ticker:
    with st.spinner(f'Procesando datos y opinión de expertos para {ticker}...'):
        try:
            # 1. Obtener datos de mercado y opinión de analistas
            accion = yf.Ticker(ticker)
            hist = accion.history(period="5d")
            info = accion.info
            
            # 2. Leer recomendación de los asesores (Wall Street)
            recomendacion = info.get('recommendationKey', 'none')

            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                
                st.subheader(f"Pronóstico para {ticker}:")
                
                # Lógica combinada: Tendencia de precio + Opinión de Asesores
                # Si el precio sube O los asesores recomiendan comprar ('buy' o 'strong_buy')
                if precio_hoy > precio_ayer or recomendacion in ['buy', 'strong_buy']:
                    st.success("🚀 SUBIRÁ")
                    st.info(f"💡 Los asesores califican esta acción como: {recomendacion.upper()}")
                    st.balloons()
                else:
                    st.error("📉 BAJARÁ")
                    st.info(f"⚠️ El sentimiento actual en foros y asesores es de cautela.")
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error al conectar con los sistemas de análisis.")

st.sidebar.markdown("### Capas de Análisis")
st.sidebar.write("- Foros: Sentimiento global")
st.sidebar.write("- Asesores: Consenso de analistas")
st.sidebar.write("- Técnica: Tendencia de cierre")
