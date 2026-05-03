import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Predictivo Pro", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Total (EUR)")
st.write("Predicción de horarios, dirección y hora estimada del máximo.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, TSLA):", "").upper()

# Fechas
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Calculando hora del máximo para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")
            info = accion.info
            eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
            cambio = 1 / eur_usd 
            
            if not hist.empty:
                precio_cierre_hoy = hist['Close'].iloc[-1] * cambio
                volatilidad_media = (hist['High'] - hist['Low']).mean() * cambio
                tendencia_alcista = precio_cierre_hoy > (hist['Close'].iloc[-5] * cambio)
                
                # Estimación de la Hora del Máximo basada en tendencia
                # Las acciones alcistas suelen tocar máximos cerca del cierre (21:30)
                # Las acciones con rebote temprano suelen tocarlo al abrir (15:45)
                hora_max_estimada = "15:45 - 16:15" if not tendencia_alcista else "21:00 - 21:45"

                # Precios Principales
                st.metric("Precio Cierre Hoy", f"{precio_cierre_hoy:.2f} €")
                
                col1, col2 = st.columns(2)
                precio_max_realista = precio_cierre_hoy + (volatilidad_media * 0.6)
                precio_cierre_est = precio_cierre_hoy + (volatilidad_media * 0.1) if tendencia_alcista else precio_cierre_hoy - (volatilidad_media * 0.1)
                
                col1.metric(f"Máximo Estimado ({fecha_str})", f"{precio_max_realista:.2f} €")
                col2.metric(f"Cierre Estimado ({fecha_str})", f"{precio_cierre_est:.2f} €")

                # --- NUEVA SECCIÓN: HORA DEL MÁXIMO ---
                st.warning(f"🎯 **Hora Estimada del Máximo:** Se prevé que el pico de {precio_max_realista:.2f} € se alcance entre las **{hora_max_estimada}**.")

                st.markdown("---")
                
                # Pronóstico de Picos de Intensidad
                st.subheader(f"⏰ Pronóstico de Picos de Intensidad ({fecha_str}):")
                movimiento_pico = volatilidad_media * 0.4
                direccion = "SUBIDA" if tendencia_alcista else "BAJADA"

                st.info(f"📌 **15:30 - 16:30 (Apertura USA):** Se prevé una **{direccion}** brusca de **{movimiento_pico:.2f} €**.")
                st.info(f"📌 **18:00 - 19:30 (Cierre Europeo):** Se estima un movimiento de **{direccion}** de **{(movimiento_pico/2):.2f} €**.")
                st.info(f"📌 **21:30 - 22:00 (Cierre USA):** Se prevé una **{direccion}** final de **{(movimiento_pico/3):.2f} €**.")

                # Diagnóstico Final
                st.markdown("---")
                if tendencia_alcista:
                    st.success(f"🚀 EL DÍA {fecha_str} LA ACCIÓN TIENE TENDENCIA AL ALZA")
                    st.balloons()
                else:
                    st.error(f"📉 EL DÍA {fecha_str} LA ACCIÓN TIENE PRESIÓN BAJISTA")

                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(info.get('recommendationKey'), 'NEUTRAL')}")
                
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error en la conexión financiera.")
