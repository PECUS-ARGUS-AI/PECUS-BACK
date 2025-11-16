from ultralytics import YOLO
import cv2
import numpy as np
from coordenadas_depth_map import gerar_profundidade_e_nuvem_pontos, obter_ponto_3d

# Carrega o modelo YOLO
modelo = YOLO('best.pt')

# Carrega a imagem
img = cv2.imread('teste_gado.jpg')

"""h, w, _ = img.shape
crop = img[0:h, 0:int(w * 0.8)]
print(crop.shape)"""

# Executa a detecção no YOLO
resultados = modelo.predict(source=img, imgsz=544, conf=0.70, save=True)

# Gera nuvem de pontos e depth map
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

for r in resultados:
    img_contorno = r.orig_img.copy()

    for caixa in r.boxes:
        x1, y1, x2, y2 = caixa.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        print(f"Caixa delimitadora: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        cv2.rectangle(img_contorno, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.circle(img_contorno, (x1, y1), 6, (0, 0, 255), -1)
        cv2.circle(img_contorno, (x2, y1), 6, (0, 0, 255), -1)
        cv2.circle(img_contorno, (x1, y2), 6, (0, 0, 255), -1)
        cv2.circle(img_contorno, (x2, y2), 6, (0, 0, 255), -1)

        pt_esq_3d = obter_ponto_3d(pontos, largura_imagem, x1, y1)
        pt_dir_3d = obter_ponto_3d(pontos, largura_imagem, x2, y1)
        pt_topo_meio_3d = obter_ponto_3d(pontos, largura_imagem, (x1 + x2)//2, y1)
        pt_base_meio_3d = obter_ponto_3d(pontos, largura_imagem, (x1 + x2)//2, y2)

        comprimento_total = np.linalg.norm(pt_dir_3d - pt_esq_3d)
        area = comprimento_total * np.linalg.norm(pt_base_meio_3d - pt_topo_meio_3d)

    # Se houver segmentação
    if r.masks is not None:
        for seg in r.masks.xy:
            pontos_seg = np.array(seg, dtype=np.int32)

            idx_esq = np.argmin(pontos_seg[:, 0])
            idx_dir = np.argmax(pontos_seg[:, 0])

            p_esq = tuple(pontos_seg[idx_esq])
            p_dir = tuple(pontos_seg[idx_dir])

            x_esq, y_esq = int(p_esq[0]), int(p_esq[1])
            x_dir, y_dir = int(p_dir[0]), int(p_dir[1])

            print(f"Ponto extremo esquerdo (x_min): ({x_esq}, {y_esq})")
            print(f"Ponto extremo direito (x_max): ({x_dir}, {y_dir})")
            print("-" * 60)

            cv2.circle(img_contorno, p_esq, 8, (0, 0, 255), -1)
            cv2.circle(img_contorno, p_dir, 8, (255, 0, 0), -1)
            cv2.line(img_contorno, p_esq, p_dir, (255, 255, 0), 3)

            # Cria máscara da segmentação
            mascara = np.zeros(img_contorno.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mascara, [pontos_seg], 255)

            num_amostras = 10
            xs = np.linspace(x_esq, x_dir, num_amostras)

            for x in xs:
                x = int(x)
                coluna = mascara[:, x]
                ys = np.where(coluna > 0)[0]

                if len(ys) > 0:
                    y_topo, y_base = ys[0], ys[-1]

                    cv2.line(img_contorno, (x, y_topo), (x, y_base), (0, 255, 255), 2)
                    cv2.circle(img_contorno, (x, y_topo), 4, (0, 0, 255), -1)
                    cv2.circle(img_contorno, (x, y_base), 4, (255, 0, 0), -1)

                    y_meio = int((y_topo + y_base) / 2)
                    cv2.circle(img_contorno, (x, y_meio), 5, (0, 255, 0), -1)

                    print(f"Ponto topo px: {x, int(y_topo)}")
                    print(f"Ponto base px: {x, int(y_base)}")
                    print(f"Ponto meio px: {x, int(y_meio)}")

                    pt_topo_3d = obter_ponto_3d(pontos, largura_imagem, x, y_topo)
                    pt_base_3d = obter_ponto_3d(pontos, largura_imagem, x, y_base)
                    pt_meio_3d = obter_ponto_3d(pontos, largura_imagem, x, y_meio)

                    print(f"Ponto topo 3D: {pt_topo_3d}")
                    print(f"Ponto base 3D: {pt_base_3d}")
                    print(f"Ponto meio 3D: {pt_meio_3d}")

                    largura = np.linalg.norm(pt_topo_3d - pt_base_3d)
                    print(f"Largura {largura}")
                    larguras.append(largura)

                    altura = abs(pt_meio_3d[2])
                    print(f"Altura {altura}")
                    alturas.append(altura)

                    print("-" * 60)

    media_altura = np.mean(alturas)
    print(f"Média Altura {media_altura}")

    media_largura = np.mean(larguras)
    print(f"Largura final {media_largura}")
    print(f"Comprimento: {comprimento_total}")

    volume = comprimento_total * media_largura * media_altura

    print(f"Volume: {volume/1000000:.2f}")
    print(f"Massa: {volume*1017:.2f}")

    cv2.imwrite("saida/bovino_contorno.png", img_contorno)

    cv2.imshow("Bovino", img_contorno)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
