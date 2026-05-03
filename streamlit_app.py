import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Predictor Pro Mañana", page_icon="🔮")

st.title("🔮 Predictor de Bolsa para Mañana")
st.write("Analizando comportamiento de mercados y expertos para la apertura del próximo día hábil...")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, AMZN):", "").upper()

if ticker:
    with st.spinner(f'Analizando jugada para mañana en {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="5d")
            info = accion.info
            rec_en = info.get('recommendationKey', 'none')

            # Traductor de consejos
            traduccion = {
                "strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER",
                "sell": "VENDER", "strong_sell": "VENTA FUERTE", "none": "NEUTRAL"
            }
            consejo_es = traduccion.get(rec_en, "NEUTRAL")

            if not historial.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                volumen = info.get('volume', 0)
                volumen_medio = info.get('averageVolume', 1)
                
                st.subheader(f"Análisis para la apertura de {ticker}:")
                
                # --- NUEVA LÓGICA DE FRASES INTUITIVAS ---
                
                # Caso 1: Subida con mucha fuerza
                if rec_en in ['strong_buy', 'buy'] and precio_hoy > precio_ayer and volumen > volumen_medio:
                    st.success("🚀 SE PREVÉ QUE MAÑANA SUBA CON MUCHA FUERZA")
                    st.write("**Análisis:** Hay una alineación perfecta entre expertos y volumen de compras. El valor tiene mucha inercia alcista.")
                    st.balloons()
                
                # Caso 2: Subida lenta / Indecisión alcista
                elif rec_en in ['strong_buy', 'buy'] and precio_hoy > precio_ayer:
                    st.success("📈 SE PREVÉ QUE MAÑANA VAYA AL ALZA AUNQUE MUY LENTA")
                    st.write("**Análisis:** Los expertos confían, pero el precio no tiene fuerza para dispararse de inmediato. Irá paso a paso.")

                # Caso 3: Oportunidad de compra en caída (Rebote)
                elif rec_en in ['strong_buy', 'buy'] and precio_hoy < precio_ayer:
                    st.warning("🛒 SE PREVÉ COMPRAR: EL PRECIO SIGUE CAYENDO PERO EN BREVE SUBIRÁ")
                    st.write("**Análisis:** Es una oportunidad de 'rebaja'. Los expertos mantienen la confianza pese a la caída de hoy.")

                # Caso 4: Mercado estancado
                elif rec_en == 'hold':
                    st.info("⚖️ SE PREVÉ QUE MAÑANA SE QUEDE IGUAL (MERCADO LATERAL)")
                    st.write("**Análisis:** Ahora mismo el precio no tiene fuerza para dispararse ni para caer. Mejor esperar.")

                # Caso 5: Bajada clara
                else:
                    st.error("📉 SE PREVÉ QUE MAÑANA SIGA CAYENDO")
                    st.write("**Análisis:** La presión vendedora es fuerte y los asesores no recomiendan entrar todavía.")

                st.info(f"💡 Consenso de Wall Street: **{consejo_es}**")
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error al conectar con los sistemas financieros.")

st.sidebar.info("Este panel analiza la probabilidad de movimiento para la apertura de la siguiente sesión.")
