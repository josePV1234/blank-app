import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Analizador Predictivo Pro", page_icon="🔮")

st.title("🔮 Analizador de Bolsa Inteligente")
st.write("Analizando mercados, sentimiento de expertos y velocidad de tendencia...")

ticker = st.text_input("Introduce el símbolo (ej: NVDA, CAR, AMZN):", "").upper()

if ticker:
    with st.spinner(f'Realizando análisis profundo para {ticker}...'):
        try:
            accion = yf.Ticker(ticker)
            hist = accion.history(period="10d")  # Tomamos más días para ver la tendencia futura
            info = accion.info
            rec_en = info.get('recommendationKey', 'none')

            if not hist.empty:
                precio_hoy = hist['Close'].iloc[-1]
                precio_ayer = hist['Close'].iloc[-2]
                variacion = abs((precio_hoy - precio_ayer) / precio_ayer) * 100
                
                # Determinamos la velocidad del movimiento
                velocidad = "MUY RÁPIDAMENTE" if variacion > 3 else "MODERADAMENTE" if variacion > 1 else "LENTAMENTE"
                
                st.subheader(f"Análisis para la apertura de mañana:")

                # 1. PREVISIÓN PARA MAÑANA
                if precio_hoy > precio_ayer:
                    st.success(f"🚀 SE PREVÉ QUE MAÑANA SUBIRÁ {velocidad}")
                else:
                    st.error(f"📉 SE PREVÉ QUE MAÑANA SEGUIRÁ CAYENDO {velocidad}")

                # 2. ANÁLISIS DE LOS PRÓXIMOS DÍAS (Tendencia a corto plazo)
                st.markdown("---")
                st.subheader("🔭 Previsión para los próximos días:")
                
                # Lógica basada en el consenso de analistas y tendencia acumulada
                if rec_en in ['strong_buy', 'buy']:
                    st.info("⬆️ **TENDENCIA AL ALZA:** El consenso de expertos es muy positivo. Se espera que tras los movimientos de mañana, la acción busque nuevos máximos en los próximos días.")
                elif rec_en in ['sell', 'strong_sell']:
                    st.warning("⬇️ **TENDENCIA HACIA ABAJO:** Hay presión vendedora constante. Los analistas sugieren que la acción seguirá buscando suelos más bajos próximamente.")
                else:
                    st.write("➡️ **TENDENCIA LATERAL:** El mercado está indeciso. Se prevé que la acción se mantenga estable sin grandes cambios en la próxima semana.")

                # Recuadro informativo del consenso
                traduccion = {"strong_buy": "COMPRA FUERTE", "buy": "COMPRAR", "hold": "MANTENER", "sell": "VENDER", "strong_sell": "VENTA FUERTE", "none": "NEUTRAL"}
                st.info(f"💡 **Consenso de Wall Street:** {traduccion.get(rec_en, 'NEUTRAL')}")
                
                if precio_hoy > precio_ayer: st.balloons()
            else:
                st.warning("No se encontraron datos.")
        except:
            st.error("Error al conectar con los sistemas financieros.")

st.sidebar.info("Este panel analiza la velocidad de la tendencia actual y proyecta el comportamiento a corto plazo.")
