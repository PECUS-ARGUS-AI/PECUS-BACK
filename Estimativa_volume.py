import numpy as np
from math import pi
import numpy.linalg as la

def estimar_volume(coordenadas_file, p1, p2, densidade=0.85, massa_real=175):
    data = np.loadtxt(coordenadas_file)
    width = 544
    height = data.shape[0] // width
    xyz = data.reshape((height, width, 3))

    pt1 = xyz[p1[1], p1[0], :]  # corrigido: [y, x]
    pt2 = xyz[p2[1], p2[0], :]

    diam = la.norm(pt1 - pt2)
    r = diam / 2.0
    V = (4.0 / 3.0) * pi * (r**3)
    massa_estim = V * densidade

    V_real = massa_real / densidade
    scale = (V_real / V) ** (1/3)

    r_corrigido = r * scale
    V_corrigido = (4/3) * pi * (r_corrigido**3)
    massa_corrigida = V_corrigido * densidade

    return {
        "raio": r,
        "volume": V,
        "massa": massa_estim,
        "fator_calib": scale,
        "raio_corrigido": r_corrigido,
        "volume_corrigido": V_corrigido,
        "massa_corrigida": massa_corrigida
    }
