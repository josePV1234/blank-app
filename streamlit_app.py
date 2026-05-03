import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Predictivo Pro", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Total (EUR)")
st.write("Predicción de horarios, dirección y análisis de comportamiento de picos.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, TSLA):", "").upper()

# Fechas
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Analizando movimientos complejos para {ticker}...'):
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
                
                # Precios Principales
                precio_max_realista = precio_cierre_hoy + (volatilidad_media * 0.6)
                precio_cierre_est = precio_cierre_hoy + (volatilidad_media * 0.1) if tendencia_alcista else precio_cierre_hoy - (volatilidad_media * 0.1)
                
                st.metric("Precio Cierre Hoy", f"{precio_cierre_hoy:.2f} €")
                col1, col2 = st.columns(2)
                col1.metric(f"Máximo Estimado ({fecha_str})", f"{precio_max_realista:.2f} €")
                col2.metric(f"Cierre Estimado ({fecha_str})", f"{precio_cierre_est:.2f} €")

                # --- NUEVA SECCIÓN DE EXPLICACIÓN DE COMPORTAMIENTO ---
                st.markdown("---")
                st.subheader("💡 Análisis del Comportamiento:")
                
                hora_max = "15:45 - 16:15" if not tendencia_alcista else "21:00 - 21:45"
                
                if not tendencia_alcista:
                    st.warning(f"""
                    ⚠️ **ALERTA DE FALSO IMPULSO:** Se estima que el pico máximo de **{precio_max_realista:.2f} €** se alcance temprano (entre las **{hora_max}**). 
                    Sin embargo, ten cuidado: se prevé que sea solo un intento de subida inicial y que, seguidamente, el precio vuelva a caer debido a la fuerte presión vendedora que domina la sesión.
                    """)
                else:
                    st.info(f"✅ **IMPULSO SOSTENIDO:** Se espera que el máximo se alcance al final de la sesión (**{hora_max}**), lo que indica una subida real y estable durante el día.")

                # Pronóstico de Picos de Intensidad
                st.subheader(f"⏰ Picos de Intensidad Detallados ({fecha_str}):")
                movimiento_pico = volatilidad_media * 0.4
                direccion = "SUBIDA" if tendencia_alcista else "BAJADA"

                st.info(f"📌 **15:30 - 16:30 (Apertura USA):** Se prevé una **{direccion}** de **{movimiento_pico:.2f} €**. Momento de alta volatilidad.")
                st.info(f"📌 **18:00 - 19:30 (Cierre Europeo):** Movimiento de **{direccion}** de **{(movimiento_pico/2):.2f} €**.")
                st.info(f"📌 **21:30 - 22:00 (Cierre USA):** Movimiento de **{direccion}** final de **{(movimiento_pico/3):.2f} €**.")

                # Diagnóstico Final y Consenso
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
