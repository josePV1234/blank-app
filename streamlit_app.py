import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Analizador Predictivo Pro", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Inteligente")
st.write("Análisis de mercados, expertos y velocidad de tendencia en tiempo real.")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, CAR, AMZN):", "").upper()

# Calcular la fecha de mañana (o próxima sesión)
hoy = datetime.now()
mañana = hoy + timedelta(days=1)
fecha_str = mañana.strftime("%d/%m/%Y")

if ticker:
    with st.spinner(f'Realizando análisis profundo para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")
            info = accion.info
            rec_en = info.get('recommendationKey', 'none')

            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                variacion = abs((precio_hoy - precio_ayer) / precio_ayer) * 100
                
                # Velocidad del movimiento
                velocidad = "MUY RÁPIDAMENTE" if variacion > 3 else "MODERADAMENTE" if variacion > 1 else "LENTAMENTE"
                
                st.subheader(f"Análisis para la sesión del {fecha_str}:")

                # 1. PREVISIÓN PARA MAÑANA CON FECHA
                if precio_hoy > precio_ayer:
                    st.success(f"🚀 SE PREVÉ QUE EL DÍA {fecha_str} LA ACCIÓN SUBIRÁ {velocidad}")
                else:
                    st.error(f"📉 SE PREVÉ QUE EL DÍA {fecha_str} LA ACCIÓN SEGUIRÁ CAYENDO {velocidad}")

                # 2. ANÁLISIS DE LOS PRÓXIMOS DÍAS
                st.markdown("---")
                st.subheader(f"🔭 Previsión técnica más allá del {fecha_str}:")
                
                if rec_en in ['strong_buy', 'buy']:
                    st.info("⬆️ **TENDENCIA AL ALZA:** El consenso de expertos es muy positivo. Se espera que tras los movimientos de mañana, la acción busque nuevos máximos en los próximos días.")
                elif rec_en in ['sell', 'strong_sell']:
                    st.warning("⬇️ **TENDENCIA HACIA ABAJO:** Hay presión vendedora constante. Los analistas sugieren que la acción seguirá buscando suelos más bajos próximamente.")
                else:
                    st.write("➡️ **TENDENCIA LATERAL:** El mercado está indeciso. Se prevé que la acción se mantenga estable sin grandes cambios en la próxima semana.")

                # Consenso traducido
                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE", "none": "NEUTRAL"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(rec_en, 'NEUTRAL')}")
                
                if precio_hoy > precio_ayer: st.balloons()
            else:
                st.warning("No se encontraron datos. Revisa el símbolo (Ticker).")
        except:
            st.error("Error al conectar con los sistemas financieros.")

st.sidebar.write(f"**Fecha de consulta:** {hoy.strftime('%d/%m/%Y')}")
st.sidebar.info("Este panel analiza la velocidad de la tendencia y proyecta el comportamiento futuro.")
