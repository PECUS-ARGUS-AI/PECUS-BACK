import cv2
import numpy as np
from ultralytics import YOLO

def medir_raio(imagem_path="apple_red/sup.jpeg", conf=0.5):
    # 1. Carregar imagem original
    img_original = cv2.imread(imagem_path)
    img_resultado = img_original.copy()
    novo_tamanho = (544, 544)
    img_resultado = cv2.resize(img_resultado, novo_tamanho, interpolation=cv2.INTER_LINEAR)

    # 2. Carregar modelo YOLO
    modelo_yolo = YOLO('yolo11n-seg.pt')
    resultados = modelo_yolo(img_resultado, conf=conf, imgsz=544)
    result = resultados[0]

    # 3. Criar máscara da maçã
    mask = result.masks.data[0].cpu().numpy().astype(np.uint8) * 255
    yolo_h, yolo_w = mask.shape[:2]

    # 4. Encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)

    # 5. Calcular centroide do contorno
    M = cv2.moments(contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # 7. Encontrar largura horizontal da maçã
    points = contour[:, 0, :]
    x_coords = [p[0] for p in points]
    x_min, x_max = min(x_coords), max(x_coords)

    # 8. Raio
    x1, y1 = x_min, cy
    x2, y2 = x_max, cy
    raio = (x2 - x1) // 2

    # 9. Desenhar
    cv2.line(img_resultado, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.circle(img_resultado, (cx, cy), raio, (255, 0, 0), 2)
    cv2.circle(img_resultado, (cx, cy), 4, (0, 0, 255), -1)

    # 10. Salvar
    output_path = "maca_red_sup_horizontal_21_58.jpeg"
    cv2.imwrite(output_path, img_resultado)

    print(f"Ponto 1: ({x1}, {y1})")
    print(f"Ponto 2: ({x2}, {y2})")
    print(f"Raio (px): {raio}")

    return {
        "ponto1": (x1, y1),
        "ponto2": (x2, y2),
        "raio": raio,
        "saida": output_path
    }
