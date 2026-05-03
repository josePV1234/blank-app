import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Predictivo Total", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Total (EUR)")
st.write("Análisis profundo de precios, máximos y cierres estimados.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, TSLA, AMZN):", "").upper()

# Calcular fechas
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Ejecutando modelos de predicción para {ticker}...'):
        try:
            # 1. Obtener datos y tipo de cambio USD/EUR
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")
            info = accion.info
            eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
            cambio = 1 / eur_usd 
            
            if not hist.empty:
                # Precios de Hoy
                precio_cierre_hoy_usd = hist['Close'].iloc[-1]
                precio_cierre_hoy_eur = precio_cierre_hoy_usd * cambio
                
                # 2. Estimaciones para Mañana (Basado en volatilidad y precio objetivo)
                volatilidad = hist['Close'].pct_change().std() # Desviación para el máximo
                objetivo_mediano_usd = info.get('targetMedianPrice', precio_cierre_hoy_usd)
                dif_objetivo = (objetivo_mediano_usd - precio_cierre_hoy_usd) / 200 # Ajuste diario
                
                # Cálculo de Máximo y Cierre
                precio_max_est_usd = precio_cierre_hoy_usd * (1 + volatilidad + abs(dif_objetivo))
                precio_cierre_est_usd = precio_cierre_hoy_usd + dif_objetivo
                
                # Conversión a Euros
                precio_max_est_eur = precio_max_est_usd * cambio
                precio_cierre_est_eur = precio_cierre_est_usd * cambio
                
                # 3. Mostrar Resultados principales
                st.metric("Precio Cierre Hoy", f"{precio_cierre_hoy_eur:.2f} €")
                
                col1, col2 = st.columns(2)
                col1.metric(f"Máximo Estimado ({fecha_str})", f"{precio_max_est_eur:.2f} €")
                col2.metric(f"Cierre Estimado ({fecha_str})", f"{precio_cierre_est_eur:.2f} €")

                st.markdown("---")
                
                # 4. Diagnóstico Detallado
                rec_en = info.get('recommendationKey', 'none')
                velocidad = "RÁPIDAMENTE" if volatilidad > 0.03 else "MODERADAMENTE" if volatilidad > 0.01 else "LENTAMENTE"
                
                if precio_cierre_est_eur > precio_cierre_hoy_eur:
                    st.success(f"🚀 EL DÍA {fecha_str} LA ACCIÓN SUBIRÁ {velocidad}")
                    st.balloons()
                else:
                    st.error(f"📉 EL DÍA {fecha_str} LA ACCIÓN SEGUIRÁ CAYENDO {velocidad}")

                # Previsión a futuro
                st.subheader(f"🔭 Proyección para los próximos días:")
                if rec_en in ['strong_buy', 'buy']:
                    st.info("⬆️ **AL ALZA:** Los analistas esperan nuevos máximos en el corto plazo.")
                elif rec_en in ['sell', 'strong_sell']:
                    st.warning("⬇️ **HACIA ABAJO:** Se detecta presión vendedora sostenida.")
                else:
                    st.write("➡️ **LATERAL:** Se prevé estabilidad sin cambios bruscos.")

                # Consenso Wall Street
                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(rec_en, 'NEUTRAL')}")
                
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error en la conexión financiera.")
