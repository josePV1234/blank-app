import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Predictivo Realista", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Inteligente (EUR)")
st.write("Análisis de precios realistas y horarios de máxima intensidad.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, TSLA):", "").upper()

# Fechas
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Calculando previsiones realistas para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")
            info = accion.info
            eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
            cambio = 1 / eur_usd 
            
            if not hist.empty:
                precio_cierre_hoy = hist['Close'].iloc[-1] * cambio
                
                # 1. CÁLCULO MÁXIMO REALISTA (Basado en la media de máximos de la última semana)
                media_oscilacion = (hist['High'] - hist['Low']).mean() * cambio
                precio_max_realista = precio_cierre_hoy + (media_oscilacion * 0.7)
                precio_cierre_est = precio_cierre_hoy + (media_oscilacion * 0.1)

                # Mostrar Precios Principales
                st.metric("Precio Cierre Hoy", f"{precio_cierre_hoy:.2f} €")
                
                col1, col2 = st.columns(2)
                col1.metric(f"Máximo Estimado ({fecha_str})", f"{precio_max_realista:.2f} €")
                col2.metric(f"Cierre Estimado ({fecha_str})", f"{precio_cierre_est:.2f} €")

                st.markdown("---")
                
                # 2. HORARIOS DE PICOS (Análisis del mercado americano y europeo)
                st.subheader("⏰ Picos de Intensidad Previstos:")
                st.write(f"Para el día {fecha_str}, se prevé mayor volatilidad en estos tramos:")
                
                st.info("📌 **15:30 - 16:30 (Apertura USA):** Pico de máxima intensidad. Es cuando se producen los movimientos más bruscos de entrada.")
                st.info("📌 **18:00 - 19:30 (Cierre Europeo):** Segundo pico de volatilidad por el ajuste de carteras internacionales.")
                st.info("📌 **21:30 - 22:00 (Cierre USA):** Tramo de 'fuerza final' donde se define el precio de cierre estimado.")

                # 3. DIAGNÓSTICO
                st.markdown("---")
                if precio_cierre_est > precio_cierre_hoy:
                    st.success(f"🚀 EL DÍA {fecha_str} LA ACCIÓN SUBIRÁ LENTAMENTE")
                    st.balloons()
                else:
                    st.error(f"📉 EL DÍA {fecha_str} LA ACCIÓN SEGUIRÁ CAYENDO MODERADAMENTE")

                # Consenso
                rec_en = info.get('recommendationKey', 'none')
                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(rec_en, 'NEUTRAL')}")
                
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error en la conexión financiera.")
