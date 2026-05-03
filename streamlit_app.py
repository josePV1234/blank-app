import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Pro EUR", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Inteligente (EUR)")
st.write("Análisis de precios, estimaciones y expertos con conversión a Euros.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, CAR, AMZN):", "").upper()

# Calcular fechas
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Calculando precios y estimaciones para {ticker}...'):
        try:
            # 1. Obtener datos y tipo de cambio USD/EUR
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")
            info = accion.info
            eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
            cambio = 1 / eur_usd # Factor para pasar de USD a EUR
            
            if not hist.empty:
                precio_cierre_usd = hist['Close'].iloc[-1]
                precio_cierre_eur = precio_cierre_usd * cambio
                
                # 2. Lógica de estimación basada en tendencia y analistas
                variacion_estimada = (info.get('targetMedianPrice', precio_cierre_usd) - precio_cierre_usd) / 250 # Estimación diaria
                if variacion_estimada == 0: variacion_estimada = (precio_cierre_usd - hist['Close'].iloc[-2]) / 2
                
                precio_est_usd = precio_cierre_usd + variacion_estimada
                precio_est_eur = precio_est_usd * cambio
                
                # 3. Mostrar Precios
                col1, col2 = st.columns(2)
                col1.metric("Precio Cierre Hoy", f"{precio_cierre_eur:.2f} €")
                col2.metric("Estimación Mañana", f"{precio_est_eur:.2f} €", f"{precio_est_eur - precio_cierre_eur:.2f} €")

                st.markdown("---")
                
                # 4. Diagnóstico
                rec_en = info.get('recommendationKey', 'none')
                if precio_est_eur > precio_cierre_eur:
                    st.success(f"🚀 SE PREVÉ QUE EL DÍA {fecha_str} LA ACCIÓN SUBIRÁ")
                else:
                    st.error(f"📉 SE PREVÉ QUE EL DÍA {fecha_str} LA ACCIÓN SEGUIRÁ CAYENDO")

                st.subheader(f"🔭 Previsión técnica más allá del {fecha_str}:")
                if rec_en in ['strong_buy', 'buy']:
                    st.info("⬆️ **TENDENCIA AL ALZA:** Los analistas esperan que la acción busque nuevos máximos próximamente.")
                elif rec_en in ['sell', 'strong_sell']:
                    st.warning("⬇️ **TENDENCIA HACIA ABAJO:** Se recomienda cautela por presión vendedora constante.")
                else:
                    st.write("➡️ **TENDENCIA LATERAL:** El mercado se mantiene estable sin cambios bruscos previstos.")

                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE", "none": "NEUTRAL"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(rec_en, 'NEUTRAL')}")
                
                if precio_est_eur > precio_cierre_eur: st.balloons()
            else:
                st.warning("No se encontraron datos. Revisa el símbolo (Ticker).")
        except:
            st.error("Error al conectar con los sistemas financieros o de cambio de moneda.")

st.sidebar.write(f"**Fecha consulta:** {hoy.strftime('%d/%m/%Y')}")
