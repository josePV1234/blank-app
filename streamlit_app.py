import streamlit as st

st.set_page_config(page_title="Analizador Pro", page_icon="🎯")
st.title("🎯 Analizador de Bolsa Directo")

empresa = st.text_input("Introduce la Empresa:", "").upper()

if empresa:
    st.write(f"### Análisis para {empresa}")
    resultado = st.radio("Pronóstico de mi IA:", ["Esperando...", "SUBIRÁ", "BAJARÁ"])
    
    if resultado == "SUBIRÁ":
        st.success(f"📈 EL LUNES {empresa} SUBIRÁ")
        st.balloons()
    elif resultado == "BAJARÁ":
        st.error(f"📉 EL LUNES {empresa} BAJARÁ")
