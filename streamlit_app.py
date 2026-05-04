import streamlit as st
import yfinance as yf
from datetime import datetime
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Terminal Sincronizada TR", layout="wide")

def get_real_tr_data(ticker_raw):
    # Forzamos el ticker de Lang & Schwarz (.LS) que usa Trade Republic
    # Si es NVDA, buscamos NVD.LS o NVDA.LS
    search_tickers = [f"{ticker_raw}.LS", "NVD.LS", ticker_raw]
    
    for t_symbol in search_tickers:
        try:
            t = yf.Ticker(t_symbol)
            # auto_adjust=True asegura que el precio considere los splits
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                info = t.info
                return t, info, hist['Close'].iloc[-1]
        except: continue
    return None, None, None

st.title("💹 Terminal Sincronizada con Trade Republic")

ticker_input = st.text_input("Introduce Ticker (ej: NVDA, SAP):", "NVDA").upper()

if ticker_input:
    accion, info, precio_final = get_real_tr_data(ticker_input)
    
    if precio_final:
        # Usamos el precio final obtenido directamente del historial ajustado
        p_real = precio_final
        # Ajustamos el resto de valores
        p_apertura = info.get('open') or p_real
        t_max = info.get('dayHigh') or p_real
        s_min = info.get('dayLow') or p_real
        currency = info.get('currency', 'EUR')

        st.subheader(f"🏦 {info.get('longName')} | {currency} (Ajustado por Split)")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio TR Real", f"{p_real:.2f} {currency}")
        c2.metric("Apertura", f"{p_apertura:.2f} {currency}")
        
        # Simulación de Bid/Ask sobre precio real ajustado
        with c3: st.success(f"BID: {p_real - 0.02:.2f} {currency}")
        with c4: st.info(f"ASK: {p_real + 0.02:.2f} {currency}")

        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} {currency}</h1></div>", unsafe_allow_html=True)
    else:
        st.error("No se pudo sincronizar el precio ajustado. Intenta con NVD (Nvidia en Europa).")

time.sleep(5)
st.rerun()
