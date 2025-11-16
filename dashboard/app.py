import streamlit as st
import numpy as np
import cv2
import requests

API_URL = "http://127.0.0.1:8000/estimar"

st.set_page_config(
    page_title="PECUS — Pesagem Inteligente",
    page_icon="🐂",
    layout="wide"
)

st.title("🐂 PECUS – Sistema de Pesagem de Gado por Imagem")
st.write("Envie uma única foto do animal para estimar peso, volume e dimensões.")

uploaded_file = st.file_uploader("Envie a imagem do bovino", type=["jpg", "jpeg", "png"])

if uploaded_file:

    # --------------------------
    # Mostrar imagem enviada
    # --------------------------
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.image(img, caption="Imagem enviada", width="stretch")

    uploaded_file.seek(0)  # necessário antes de enviar à API

    # --------------------------
    # Enviar para API FastAPI
    # --------------------------
    with st.spinner("Processando..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        resultado = response.json()["resultado"]

        # ------------------------------
        # Métricas principais
        # ------------------------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Comprimento (m)", f"{resultado['comprimento']:.2f}")
        col2.metric("Largura média (m)", f"{resultado['largura_media']:.2f}")
        col3.metric("Altura média (m)", f"{resultado['altura_media']:.2f}")
        col4.metric("Volume (m³)", f"{resultado['volume_m3']:.4f}")

        st.metric("Estimativa de Peso", f"{resultado['massa_kg']} kg")

        st.divider()

        # ------------------------------------------
        # Mostrar imagens geradas (contorno + depth)
        # ------------------------------------------
        st.subheader("📸 Imagens geradas")

        colA, colB = st.columns(2)

        try:
            img_contorno = cv2.imread("saida/bovino_contorno.png")
            if img_contorno is not None:
                colA.image(img_contorno, caption="Bovino com contorno", width="stretch")
        except:
            pass

        try:
            img_depth = cv2.imread("saida/resultado_profundidade.png")
            if img_depth is not None:
                colB.image(img_depth, caption="Mapa de profundidade", width="stretch")
        except:
            pass

    else:
        st.error("❌ Erro ao processar imagem no servidor.")
