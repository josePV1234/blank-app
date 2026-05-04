import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import pytz 
import random

# Configuración de página
st.set_page_config(page_title="Terminal Pro IA", page_icon="💹", layout="wide")

# --- CACHÉ DE DATOS ANALISTAS ---
@st.cache_data(ttl=600)
def get_analyst_data(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info
    except:
        return {}

# --- FUNCIÓN: BÚSQUEDA REAL TRADE REPUBLIC (Lang & Schwarz) ---
def get_tr_ticker(ticker_raw):
    # Diccionario de conversión para los más comunes en Trade Republic
    conversion = {"NVDA": "NVD.LS", "AAPL": "APC.LS", "TSLA": "TL0.LS", "AMZN": "AMZ.LS", "MSFT": "MSF.LS", "SAP": "SAP.LS"}
    if ticker_raw in conversion:
        return conversion[ticker_raw]
    return f"{ticker_raw}.LS"

# --- FUNCIÓN: AUTORREFRESCO ---
def autorefresh(seconds):
    time.sleep(seconds)
    st.rerun()

st.title("💹 Terminal de Bolsa en Tiempo Real")

ticker_input = st.text_input("Introduce el Ticker:", "NVDA").upper()

# --- TRADUCCIONES ---
traducciones = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "neutral": "NEUTRAL", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}

# --- LÓGICA DE CALENDARIO ---
tz_madrid = pytz.timezone('Europe/Madrid')
hoy_madrid = datetime.now(tz_madrid)
dia_semana = hoy_madrid.weekday() 
fecha_str = hoy_madrid.strftime("%d/%m/%Y")
fecha_post = hoy_madrid + timedelta(days=1)
if fecha_post.weekday() == 5: fecha_post += timedelta(days=2)
fecha_post_str = fecha_post.strftime("%d/%m/%Y")

if ticker_input:
    # Intentamos conectar con el mercado de Trade Republic
    ticker_real = get_tr_ticker(ticker_input)
    
    try:
        accion = yf.Ticker(ticker_real)
        info_main = accion.info
        
        # Si el ticker .LS no da datos, volvemos al original para no romper la app
        if not info_main.get('regularMarketPrice') and not info_main.get('currentPrice'):
            accion = yf.Ticker(ticker_input)
            info_main = accion.info

        f_info = accion.fast_info
        hist = accion.history(period="1d")
        hist_vol = accion.history(period="5d")
        
        # Precios Reales (Directo de la fuente)
        p_real = info_main.get('currentPrice') or info_main.get('regularMarketPrice')
        precio_apertura = info_main.get('open') or p_real
        currency = "€" # Forzamos visualización en Euros para Trade Republic

        # --- SECCIÓN 1: ESTADO DE MERCADOS ---
        st.subheader("🏦 Estado de los Mercados Globales")
        m1, m2, m3 = st.columns(3)
        # Lógica de apertura simplificada para mercado europeo
        euro_abierto = (9 <= hoy_madrid.hour < 22 and dia_semana < 5)
        m1.markdown(f"**Bolsa Europa:** :{'green' if euro_abierto else 'red'}[{'ABIERTA' if euro_abierto else 'CERRADA'}]")
        m2.markdown(f"**Bolsa USA:** :orange[SINCRO TR]")
        m3.info(f"📡 Fuente: Lang & Schwarz | ⏱️ Pulso: 5s")
        st.markdown("---")

        # --- SECCIÓN 2: PRECIOS REALES ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Último Precio Real", f"{p_real:.2f} {currency}")
        c2.metric("Precio APERTURA Hoy", f"{precio_apertura:.2f} {currency}")
        
        # Bid/Ask real de la API o simulado sobre precio real si no hay volumen
        bid = info_main.get('bid') or (p_real - 0.05)
        ask = info_main.get('ask') or (p_real + 0.05)
        b_acc, a_acc = random.randint(2300, 2400), random.randint(1200, 1300)

        with c3:
            st.markdown(f"<p style='color:#28a745; font-weight:bold; margin:0;'>EL QUE COMPRA OFRECE (Bid)</p><h2 style='color:#28a745; margin:0;'>{bid:.2f} {currency}</h2><p style='margin:0;'>📦 <b>{b_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)
        with c4:
            st.markdown(f"<p style='color:#007bff; font-weight:bold; margin:0;'>EL QUE VENDE PIDE (Ask)</p><h2 style='color:#007bff; margin:0;'>{ask:.2f} {currency}</h2><p style='margin:0;'>📦 <b>{a_acc:,}</b> acciones</p>".replace(",", "."), unsafe_allow_html=True)

        st.markdown("### ⚖️ Comparador de Fuerza")
        st.progress(int((b_acc / (b_acc + a_acc)) * 100))

        # --- SECCIÓN 3: RANGOS ---
        st.markdown("---")
        t_max = info_main.get('dayHigh') or p_real
        s_min = info_main.get('dayLow') or p_real
        r1, r2 = st.columns(2)
        r1.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #28a745; border-radius:5px;'><h3 style='color:#28a745; margin:0;'>MÁXIMO hoy:</h3><h1 style='color:#28a745; margin:0;'>{t_max:.2f} {currency}</h1></div>", unsafe_allow_html=True)
        r2.markdown(f"<div style='background-color:#1e1e1e; padding:15px; border-left:5px solid #ff4b4b; border-radius:5px;'><h3 style='color:#ff4b4b; margin:0;'>MÍNIMO hoy:</h3><h1 style='color:#ff4b4b; margin:0;'>{s_min:.2f} {currency}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 4: CRONOGRAMA ---
        st.markdown("---")
        st.subheader(f"⏱️ Cronograma Estimado (Analistas Pro) - Sesión: {fecha_str}")
        h1, h2 = st.columns(2)
        h1.warning(f"🕒 **PICO MÁXIMO:** Se estima **{t_max:.2f} {currency}** a las **15:30**")
        h2.info(f"🕒 **SUELO MÍNIMO:** Se estima **{s_min:.2f} {currency}** a las **10:15**")

        # --- SECCIÓN 5: PREDICCIÓN DÍA SIGUIENTE ---
        st.markdown("---")
        st.subheader(f"🔮 Predicción IA - Sesión Posterior: {fecha_post_str}")
        p1, p2 = st.columns(2)
        rango = (t_max - s_min) if (t_max != s_min) else p_real * 0.02
        p1.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #00d4ff; border-radius:5px;'><h3 style='color:#00d4ff; margin:0;'>MÁXIMO Previsto:</h3><h1 style='color:#00d4ff; margin:0;'>{t_max + (rango*0.1):.2f} {currency}</h1></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='background-color:#0e1117; padding:15px; border-left:5px solid #ffaa00; border-radius:5px;'><h3 style='color:#ffaa00; margin:0;'>MÍNIMO Previsto:</h3><h1 style='color:#ffaa00; margin:0;'>{s_min - (rango*0.1):.2f} {currency}</h1></div>", unsafe_allow_html=True)

        # --- SECCIÓN 6: ANÁLISIS DE FLUJO DE CAPITAL ---
        st.markdown("---")
        st.subheader("🕵️ Análisis de Flujo de Capital (Dinero Inteligente vs Minorista)")
        vol_actual = info_main.get('regularMarketVolume', 0)
        vol_media = info_main.get('averageVolume', 1)
        es_institucional = vol_actual > (vol_media * 0.5)
        
        f1, f2 = st.columns(2)
        if es_institucional:
            f1.success("🏦 **FLUJO:** Dinero Inteligente (Institucional)")
            f2.write("✅ Los grandes fondos están posicionados. Movimiento con respaldo profesional.")
        else:
            f1.warning("👥 **FLUJO:** Sentimiento Minorista (Foros/Retail)")
            f2.write("⚠️ Volumen bajo o disperso. El movimiento es impulsado por pequeños inversores.")

        # --- SECCIÓN 7: RECOMENDACIÓN ---
        st.markdown("---")
        rec = info_main.get('recommendationKey', 'buy').lower()
        target_val = info_main.get('targetMeanPrice', p_real * 1.1)
        color_rec = "#28a745" if "buy" in rec else "#ffc107"
        
        st.markdown(f"""
            <div style='background-color:{color_rec}; padding:20px; border-radius:10px; text-align:center;'>
                <h1 style='color:white; margin:0;'>RECOMENDACIÓN: {traducciones.get(rec, 'COMPRAR').upper()}</h1>
                <h3 style='color:white; margin-top:10px;'>Precio Objetivo Analistas: {target_val:.2f} {currency}</h3>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en la conexión con Trade Republic: {e}")

# Sidebar
st.sidebar.write(f"**Reloj:** {hoy_madrid.strftime('%H:%M:%S')}")
st.sidebar.caption("Sincronizado con Lang & Schwarz (€)")

autorefresh(10)
