import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose
from depth_anything.dpt import DepthAnything
from depth_anything.util.transform import Resize, NormalizeImage, PrepareForNet

# ======================================================
# 1) CARREGAR MODELO APENAS UMA VEZ
# ======================================================
DISPOSITIVO = 'cuda' if torch.cuda.is_available() else 'cpu'
CODIFICADOR = "vits"

print("🔄 Carregando modelo DepthAnything...")

modelo_depth = DepthAnything.from_pretrained(
    f"LiheYoung/depth_anything_{CODIFICADOR}14"
).to(DISPOSITIVO).eval()

print("✅ DepthAnything carregado com sucesso.")


# ======================================================
# 2) FUNÇÃO PRINCIPAL
# ======================================================
def gerar_profundidade_e_nuvem_pontos(
    imagem,
    largura,
    altura,
    pasta_saida="./saida_profundidade",
    distancia_focal=None
):
    """
    Recebe imagem BGR e gera:
        - Nuvem de pontos 3D
        - Depth map salvo no disco
    """

    os.makedirs(pasta_saida, exist_ok=True)

    # Converter para RGB
    img_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB) / 255.0
    h, w = img_rgb.shape[:2]

    # ------------------------------------------------------
    # TRANSFORMAÇÃO
    # ------------------------------------------------------
    transformacao = Compose([
        Resize(
            width=largura,
            height=altura,
            keep_aspect_ratio=True,
            ensure_multiple_of=14,
            resize_method='lower_bound',
            image_interpolation_method=cv2.INTER_CUBIC
        ),
        NormalizeImage(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        PrepareForNet(),
    ])

    img_tensor = transformacao({"image": img_rgb})["image"]
    img_tensor = torch.from_numpy(img_tensor).unsqueeze(0).to(DISPOSITIVO)

    # ------------------------------------------------------
    # INFERÊNCIA DE PROFUNDIDADE
    # ------------------------------------------------------
    with torch.no_grad():
        profundidade = modelo_depth(img_tensor)

    profundidade = F.interpolate(
        profundidade[None], (h, w),
        mode="bilinear",
        align_corners=False
    )[0, 0]

    profundidade_real = profundidade.cpu().numpy()

    # ------------------------------------------------------
    # SALVAR DEPTH MAP
    # ------------------------------------------------------
    profundidade_norm = (profundidade_real - profundidade_real.min()) / \
                        (profundidade_real.max() - profundidade_real.min()) * 255.0

    depth_vis = profundidade_norm.astype(np.uint8)
    caminho_depth = os.path.join(pasta_saida, "resultado_profundidade.png")
    cv2.imwrite(caminho_depth, cv2.applyColorMap(depth_vis, cv2.COLORMAP_INFERNO))

    # ------------------------------------------------------
    # NUVEM DE PONTOS
    # ------------------------------------------------------
    if distancia_focal is None:
        distancia_focal = max(h, w) * 0.8

    cx, cy = w / 2, h / 2
    u, v = np.meshgrid(np.arange(w), np.arange(h))

    x_norm = (u - cx) / distancia_focal
    y_norm = (v - cy) / distancia_focal

    x_3d = x_norm * profundidade_real
    y_3d = y_norm * profundidade_real
    z_3d = profundidade_real

    pontos_3d = np.stack([x_3d, y_3d, z_3d], axis=-1).reshape(-1, 3)

    return pontos_3d


# ======================================================
# 3) FUNÇÃO UTILITÁRIA — OBTÉM PONTO (x, y) EM 3D
# ======================================================
def obter_ponto_3d(pontos, largura, x, y):
    altura = pontos.shape[0] // largura
    xyz = pontos.reshape((altura, largura, 3))
    return xyz[y, x, :]
