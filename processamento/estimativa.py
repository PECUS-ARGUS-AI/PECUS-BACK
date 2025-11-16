from ultralytics import YOLO
import cv2
import numpy as np
from processamento.depth import gerar_profundidade_e_nuvem_pontos, obter_ponto_3d

# Carrega o modelo YOLO (isso pode ficar fora)
modelo = YOLO('modelos/best.pt')


def processar_bovino(imagem_bytes):
    """
    Processa uma imagem enviada pela API
    e retorna dimensões e peso estimado do bovino.
    """

    # -----------------------------
    # 1) Carrega imagem enviada
    # -----------------------------
    npimg = np.frombuffer(imagem_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # -----------------------------
    # 2) YOLO detecta o boi
    # -----------------------------
    resultados = modelo.predict(
        source=img,
        imgsz=544,
        conf=0.70
    )

    # -----------------------------
    # 3) Depth + nuvem de pontos
    # -----------------------------
    pontos = gerar_profundidade_e_nuvem_pontos(
        imagem=img,
        largura=img.shape[1],
        altura=img.shape[0],
        pasta_saida="saida"
    )

    largura_imagem = img.shape[1]

    comprimento_total = 0
    larguras = []
    alturas = []

    # ---------------------------------------------------
    # 4) ITERAÇÃO sobre caixas, segmentações e medidas
    # ---------------------------------------------------
    for r in resultados:
        for caixa in r.boxes:
            x1, y1, x2, y2 = caixa.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

            pt_esq_3d = obter_ponto_3d(pontos, largura_imagem, x1, y1)
            pt_dir_3d = obter_ponto_3d(pontos, largura_imagem, x2, y1)
            pt_topo_meio_3d = obter_ponto_3d(pontos, largura_imagem, (x1 + x2) // 2, y1)  # noqa: F841
            pt_base_meio_3d = obter_ponto_3d(pontos, largura_imagem, (x1 + x2) // 2, y2)  # noqa: F841

            comprimento_total = np.linalg.norm(pt_dir_3d - pt_esq_3d)

        # --------------------------
        # SEGMENTAÇÃO
        # --------------------------
        if r.masks is not None:
            for seg in r.masks.xy:
                pontos_seg = np.array(seg, dtype=np.int32)

                idx_esq = np.argmin(pontos_seg[:, 0])
                idx_dir = np.argmax(pontos_seg[:, 0])

                x_esq = int(pontos_seg[idx_esq][0])
                x_dir = int(pontos_seg[idx_dir][0])

                mascara = np.zeros(img.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mascara, [pontos_seg], 255)

                xs = np.linspace(x_esq, x_dir, 10)
                for x in xs:
                    x = int(x)
                    coluna = mascara[:, x]
                    ys = np.where(coluna > 0)[0]

                    if len(ys) > 0:
                        y_topo = ys[0]
                        y_base = ys[-1]
                        y_meio = int((y_topo + y_base) / 2)

                        pt_topo_3d = obter_ponto_3d(pontos, largura_imagem, x, y_topo)
                        pt_base_3d = obter_ponto_3d(pontos, largura_imagem, x, y_base)
                        pt_meio_3d = obter_ponto_3d(pontos, largura_imagem, x, y_meio)

                        # distância vertical → largura corporal
                        largura = np.linalg.norm(pt_topo_3d - pt_base_3d)
                        larguras.append(largura)

                        # altura → profundidade do ponto central
                        altura = abs(pt_meio_3d[2])
                        alturas.append(altura)

    # -------------------------------------------
    # 5) CÁLCULOS FINAIS
    # -------------------------------------------
    media_altura = float(np.mean(alturas))
    media_largura = float(np.mean(larguras))
    comprimento_total = float(comprimento_total)

    volume = comprimento_total * media_largura * media_altura
    massa = volume * 1017  # densidade aproximada kg/m³
    
    # ----------------------------------------------------------
    # 6) DESENHO DO CONTORNO COMPLETO (igual ao script original)
    # ----------------------------------------------------------
    img_contorno = img.copy()

    for r in resultados:

        # ---- Caixa delimitadora ----
        for caixa in r.boxes:
            x1, y1, x2, y2 = caixa.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

            cv2.rectangle(img_contorno, (x1, y1), (x2, y2), (0, 255, 255), 2)

            cv2.circle(img_contorno, (x1, y1), 6, (0, 0, 255), -1)
            cv2.circle(img_contorno, (x2, y1), 6, (0, 0, 255), -1)
            cv2.circle(img_contorno, (x1, y2), 6, (0, 0, 255), -1)
            cv2.circle(img_contorno, (x2, y2), 6, (0, 0, 255), -1)

        # ---- Segmentação (máscara) ----
        if r.masks is not None:
            for seg in r.masks.xy:

                pontos_seg = np.array(seg, dtype=np.int32)
                idx_esq = np.argmin(pontos_seg[:, 0])
                idx_dir = np.argmax(pontos_seg[:, 0])

                p_esq = tuple(pontos_seg[idx_esq])
                p_dir = tuple(pontos_seg[idx_dir])

                x_esq, y_esq = int(p_esq[0]), int(p_esq[1])
                x_dir, y_dir = int(p_dir[0]), int(p_dir[1])

                cv2.circle(img_contorno, p_esq, 8, (0, 0, 255), -1)
                cv2.circle(img_contorno, p_dir, 8, (255, 0, 0), -1)
                cv2.line(img_contorno, p_esq, p_dir, (255, 255, 0), 3)

                mascara = np.zeros(img_contorno.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mascara, [pontos_seg], 255)

                xs = np.linspace(x_esq, x_dir, 10)

                for x in xs:
                    x = int(x)
                    coluna = mascara[:, x]
                    ys = np.where(coluna > 0)[0]

                    if len(ys) > 0:
                        y_topo, y_base = ys[0], ys[-1]
                        y_meio = int((y_topo + y_base) / 2)

                        cv2.line(img_contorno, (x, y_topo), (x, y_base), (0, 255, 255), 2)
                        cv2.circle(img_contorno, (x, y_topo), 4, (0, 0, 255), -1)
                        cv2.circle(img_contorno, (x, y_base), 4, (255, 0, 0), -1)
                        cv2.circle(img_contorno, (x, y_meio), 5, (0, 255, 0), -1)

    # ---- SALVAR A IMAGEM FINAL DO CONTORNO ----
    cv2.imwrite("saida/bovino_contorno.png", img_contorno)

    # -------------------------------------------
    # 7) Retorno limpo para API
    # -------------------------------------------
    return {
        "altura_media": round(media_altura, 2),
        "largura_media": round(media_largura, 2),
        "comprimento": round(comprimento_total, 2),
        "volume_m3": round(volume, 3),
        "massa_kg": round(massa / 1000000, 2)
    }
