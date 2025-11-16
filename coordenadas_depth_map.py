import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from torchvision.transforms import Compose
from depth_anything.dpt import DepthAnything
from depth_anything.util.transform import Resize, NormalizeImage, PrepareForNet


def gerar_profundidade_e_nuvem_pontos(
        imagem: str,
        largura: int,
        altura: int,
        pasta_saida: str = "./saida_profundidade",
        codificador: str = "vits",
        distancia_focal: float = None):
    """
    Processa imagem -> Mapa de Profundidade -> Nuvem de Pontos (x, y, z)

    Retorna:
        pontos_3d (np.ndarray): N x 3 -> coordenadas 3D
        profundidade_real (np.ndarray): mapa de profundidade relativo
        caminho_profundidade (str): caminho do depth map salvo
    """

    os.makedirs(pasta_saida, exist_ok=True)

    DISPOSITIVO = 'cuda' if torch.cuda.is_available() else 'cpu'

    modelo = DepthAnything.from_pretrained(f'LiheYoung/depth_anything_{codificador}14').to(DISPOSITIVO).eval()

    img_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB) / 255.0
    h, w = img_rgb.shape[:2]

    transformacao = Compose([
        Resize(width=largura, height=altura, keep_aspect_ratio=True,
               ensure_multiple_of=14, resize_method='lower_bound',
               image_interpolation_method=cv2.INTER_CUBIC),
        NormalizeImage(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
        PrepareForNet(),
    ])

    img_tensor = transformacao({'image': img_rgb})['image']
    img_tensor = torch.from_numpy(img_tensor).unsqueeze(0).to(DISPOSITIVO)

    with torch.no_grad():
        profundidade = modelo(img_tensor)  # (1, H, W)

    # Redimensionar para o tamanho original
    profundidade = F.interpolate(profundidade[None], (h, w),
                                 mode='bilinear', align_corners=False)[0, 0]
    profundidade_real = profundidade.cpu().numpy()

    # ==== Salvar mapa de profundidade ====
    profundidade_norm = (profundidade_real - profundidade_real.min()) / \
                        (profundidade_real.max() - profundidade_real.min()) * 255.0

    profundidade_vis = profundidade_norm.astype(np.uint8)
    caminho_profundidade = os.path.join(pasta_saida, "resultado_profundidade.png")
    cv2.imwrite(caminho_profundidade,
                cv2.applyColorMap(profundidade_vis, cv2.COLORMAP_INFERNO))

    # ==== Converter para pontos 3D ====
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


def obter_ponto_3d(pontos, largura, x, y):
    """
    Retorna o ponto 3D correspondente a uma coordenada (x, y).
    """
    altura = pontos.shape[0] // largura
    xyz = pontos.reshape((altura, largura, 3))

    return xyz[y, x, :]
