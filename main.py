from coordenad_depth import run_depth
from medir_raio_maca import medir_raio
from Estimativa_volume import estimar_volume

IMG = "/home/jvos3/Desenvolvimento/Projetos JOAO/PECUS/MACA/apple_red/sup.jpeg"
OUTDIR = "vis_depth"

print("\n=== PROCESSANDO DEPTH ANYTHING ===")
run_depth(
    img_path=IMG,
    outdir=OUTDIR,
    save_pointcloud=True,
    focal_length=800
)

print("\n=== MEDINDO RAIO DA MAÇÃ (YOLO) ===")
resultado = medir_raio(
    imagem_path=IMG,
    conf=0.5
)

p1 = resultado["ponto1"]
p2 = resultado["ponto2"]

print(f"Usando p1={p1}, p2={p2}")

print("\n=== ESTIMANDO VOLUME ===")
vol = estimar_volume(
    coordenadas_file=f"{OUTDIR}/sup_coordinates.txt",
    p1=p1,
    p2=p2
)

print("\n----- RESULTADOS -----")
print(f"Raio estimado (cm): {vol['raio']:.3f}")
print(f"Volume estimado (cm³): {vol['volume']:.2f}")
print(f"Massa estimada (g): {vol['massa']:.2f}")
print(f"Fator calibração: {vol['fator_calib']:.3f}")
print(f"Raio corrigido (cm): {vol['raio_corrigido']:.3f}")
print(f"Volume corrigido (cm³): {vol['volume_corrigido']:.2f}")
print(f"Massa corrigida (g): {vol['massa_corrigida']:.2f}")


print("Resultado da medição:", resultado)
