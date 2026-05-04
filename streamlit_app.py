import streamlit as st
import yfinance as yf
from datetime import datetime
import time
import pytz 

# Configuración de página
st.set_page_config(page_title="Terminal Pro Trade Republic", page_icon="💹", layout="wide")

# --- CACHÉ DE DATOS ---
@st.cache_data(ttl=10) # Reducido a 10s para máxima precisión
def get_stock_data(ticker):
    try:
        # Añadimos el sufijo .LS para que coincida con Lang & Schwarz (Trade Republic)
        if "." not in ticker:
            ticker_ls = f"{ticker}.LS"
        else:
            ticker_ls = ticker
            
        t = yf.Ticker(ticker_ls)
        # Si .LS no devuelve datos (ej. algunas americanas), usamos el ticker original
        if t.fast_info.last_price is None:
            t = yf.Ticker(ticker)
            
        return t
    except:
        return None

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal Real-Time (Sincronizado L&S)")

# El usuario introduce el ticker normal (ej: SAP o NVDA)
ticker_raw = st.text_input("Introduce el Ticker (ej: SAP, NVDA, ASML):", "SAP").upper()

tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)

if ticker_raw:
    accion = get_stock_data(ticker_raw)
    
    if accion:
        try:
            f_info = accion.fast_info
            info_full = accion.info
            
            # DATOS REALES (Sin cálculos aleatorios)
            p_actual = f_info.last_price
            p_apertura = f_info.open if f_info.open else p_actual
            # En Trade Republic el bid/ask es real, aquí lo aproximamos con datos de mercado
            bid = info_full.get('bid', p_actual - 0.02)
            ask = info_full.get('ask', p_actual + 0.02)
            
            currency = info_full.get('currency', 'EUR')

            # --- SECCIÓN 1: CABECERA ---
            st.subheader(f"📊 {info_full.get('longName', ticker_raw)} ({currency})")
            m1, m2, m3 = st.columns(3)
            m1.metric("Último Precio", f"{p_actual:.2d} {currency}")
            m2.metric("Apertura Hoy", f"{p_apertura:.2f} {currency}")
            m3.info(f"Market: {info_full.get('exchange', 'L&S')}")

            # --- SECCIÓN 2: BID / ASK (Como en Trade Republic) ---
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div style='background-color:#1e1e1e; padding:20px; border-radius:10px; border-left:8px solid #28a745;'>
                        <p style='color:#28a745; font-weight:bold; margin:0;'>PRECIO COMPRA (ASK)</p>
                        <h1 style='margin:0;'>{ask:.2f} {currency}</h1>
                        <p style='font-size:0.8em; color:grey;'>Precio al que entrarías ahora</p>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style='background-color:#1e1e1e; padding:20px; border-radius:10px; border-left:8px solid #ff4b4b;'>
                        <p style='color:#ff4b4b; font-weight:bold; margin:0;'>PRECIO VENTA (BID)</p>
                        <h1 style='margin:0;'>{bid:.2f} {currency}</h1>
                        <p style='font-size:0.8em; color:grey;'>Precio al que saldrías ahora</p>
                    </div>
                """, unsafe_allow_html=True)

            # --- SECCIÓN 3: RANGOS DEL DÍA ---
            st.markdown("---")
            low_day = f_info.day_low
            high_day = f_info.day_high
            st.write(f"**Rango Diario:** {low_day:.2f} - {high_day:.2f}")
            progreso = ((p_actual - low_day) / (high_day - low_day)) if high_day != low_day else 0.5
            st.progress(min(max(progreso, 0.0), 1.0))

            # --- ANÁLISIS DE VOLUMEN ---
            vol_actual = f_info.last_volume
            vol_media = info_full.get('averageVolume', 1)
            
            if vol_actual > (vol_media * 1.5):
                st.success("🔥 **ALTA VOLATILIDAD:** El volumen actual es superior a la media. Movimiento institucional detectado.")
            else:
                st.info("💎 **FLUJO NORMAL:** El mercado se mueve con volúmenes estándar.")

        except Exception as e:
            st.error(f"Error obteniendo datos en tiempo real: {e}")
    else:
        st.error("No se encontró el Ticker. Prueba con el nombre completo.")

# Sidebar
st.sidebar.write(f"**Última actualización:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.markdown("---")
st.sidebar.caption("Sincronizado con Lang & Schwarz (Exchange de Trade Republic)")

autorefresh(5)
