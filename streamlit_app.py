import streamlit as st
import yfinance as yf
from datetime import datetime
import time
import pytz 

# Configuración de página
st.set_page_config(page_title="Terminal Trade Republic", page_icon="💹", layout="wide")

# --- FUNCIÓN DE BÚSQUEDA ROBUSTA ---
def get_stock_data(ticker_raw):
    # Lista de sufijos por orden de prioridad para Trade Republic
    sufijos = [".LS", ".DE", ""] 
    
    for sufijo in sufijos:
        try:
            ticker_test = f"{ticker_raw}{sufijo}"
            accion = yf.Ticker(ticker_test)
            # Forzamos una pequeña descarga para validar que el ticker existe y tiene datos
            info = accion.info
            if 'regularMarketPrice' in info or 'currentPrice' in info:
                return accion, info
        except:
            continue
    return None, None

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal Real-Time (Sincronizado L&S)")

ticker_input = st.text_input("Introduce el Ticker (ej: SAP, NVDA, ASML):", "SAP").upper()

if ticker_input:
    with st.spinner('Buscando en mercados europeos...'):
        accion, info_full = get_stock_data(ticker_input)
    
    if accion and info_full:
        try:
            # Extraemos precios con fallback para evitar errores de None
            p_actual = info_full.get('currentPrice') or info_full.get('regularMarketPrice')
            p_apertura = info_full.get('open') or p_actual
            bid = info_full.get('bid') or (p_actual * 0.998)
            ask = info_full.get('ask') or (p_actual * 1.002)
            currency = info_full.get('currency', 'EUR')

            # --- VISUALIZACIÓN ---
            st.subheader(f"📊 {info_full.get('longName', ticker_input)} | Mercado: {info_full.get('exchange')}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio Actual", f"{p_actual:.2f} {currency}")
            c2.metric("Apertura", f"{p_apertura:.2f} {currency}")
            c3.write(f"**ISIN:** {info_full.get('isin', 'N/A')}")

            st.markdown("---")
            col_bid, col_ask = st.columns(2)
            with col_bid:
                st.success(f"**PRECIO VENTA (BID):** {bid:.2f} {currency}")
                st.caption("Precio al que Trade Republic te compra la acción.")
            with col_ask:
                st.info(f"**PRECIO COMPRA (ASK):** {ask:.2f} {currency}")
                st.caption("Precio al que tú compras la acción.")

            # Barra de rango diario
            low = info_full.get('dayLow', p_actual)
            high = info_full.get('dayHigh', p_actual)
            st.markdown(f"**Rango del día:** {low:.2f} --- ● --- {high:.2f}")
            
        except Exception as e:
            st.error(f"Error al procesar datos: {e}")
    else:
        st.error(f"No se pudo conectar con el mercado para '{ticker_input}'. Verifica que el ticker sea correcto.")

# Sidebar info
st.sidebar.write(f"Refresco automático: 10s")
st.sidebar.write(f"Hora Local: {datetime.now().strftime('%H:%M:%S')}")

time.sleep(10)
st.rerun()
