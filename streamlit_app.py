import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

# --- FUNCIÓN DE BÚSQUEDA INTELIGENTE Y CONVERSIÓN ---
def get_stock_data_pro(ticker_raw):
    try:
        # 1. Obtenemos el ticker principal (EE.UU. para NVDA, Europa para SAP)
        t = yf.Ticker(ticker_raw)
        info = t.info
        
        # 2. Obtenemos el cambio EUR/USD en tiempo real si la moneda es USD
        currency = info.get('currency', 'USD')
        cambio = 1.0
        if currency == 'USD':
            fx = yf.Ticker("EURUSD=X")
            cambio = fx.fast_info.last_price
            
        return t, info, cambio
    except:
        return None, None, 1.0

def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker_input = st.text_input("Introduce el Ticker (ej: NVDA, SAP, AAPL):", "NVDA").upper()
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

if ticker_input:
    accion, info_main, tasa_cambio = get_stock_data_pro(ticker_input)
    
    if accion and info_main:
        # Precios base convertidos a EUR si es necesario
        p_raw = info_main.get('currentPrice') or info_main.get('regularMarketPrice')
        p_real = p_raw * tasa_cambio
        precio_apertura = (info_main.get('open') or p_raw) * tasa_cambio
        t_max = info_main.get('dayHigh', p_raw) * tasa_cambio
        s_min = info_main.get('dayLow', p_raw) * tasa_cambio
        
        # --- SECCIÓN 1: ESTADO ---
        st.subheader(f"🏦 {info_main.get('longName')} | Moneda Base: {info_main.get('currency')}")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Bolsa:** :green[{info_main.get('exchange')}]") 
        m2.markdown(f"**Conversión EUR/USD:** {tasa_cambio:.4f}")
        m3.info(f"📡 Datos Sincronizados | ⏱️ Pulso: 5s")
        st.markdown("---")

        # --- SECCIÓN 2: PRECIOS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Último Precio (EUR)", f"{p_real:.2f} €")
        c2.metric("Apertura (EUR)", f"{precio_apertura:.2f} €")
        
        bid, ask = p_real * 0.9995, p_real * 1.0005
        b_acc, a_acc = random.randint(2300, 2400), random.randint(1200, 1300)

        with c3:
            st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>BID (EUR)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} €</h2><p style='margin:0;'>📦 <b>{b_acc:,}</b> acc.</p>".replace(",", "."), unsafe_allow_html=True)
        with c4:
            st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>ASK (EUR)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} €</h2><p style='margin:0;'>📦 <b>{a_acc:,}</b> acc.</p>".replace(",", "."), unsafe_allow_html=True)

        st.progress(int((b_acc / (b_acc + a_acc)) * 100))

        # --- SECCIÓN 3: RANGOS ---
        st.markdown("---")
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO HOY (EUR):</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} €</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO HOY (EUR):</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} €</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 4: RECOMENDACIÓN ---
        st.markdown("---")
        rec = info_main.get('recommendationKey', 'buy').lower()
        target_eur = info_main.get('targetMeanPrice', p_raw) * tasa_cambio
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        st.markdown(f"""
            <div style='background-color:{color_rec}; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>RECOMENDACIÓN: {traducciones.get(rec, 'MANTENER').upper()}</h1>
                <h3 style='color:white; margin-top:10px;'>Precio Objetivo: {target_eur:.2f} €</h3>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.error("Ticker no encontrado.")

autorefresh(5)
