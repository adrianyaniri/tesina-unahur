import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "weld-geometry"))

from annotate import annotate_image

IMG = Path("data/raw/imagenes/originales/Cordon1_Seccion 1 horizontal C1.jpg")

def main():
    print(f"Abriendo: {IMG}")
    
    # Podés ajustar el zoom acá si hace falta
    coords = annotate_image(IMG, zoom=1.2)
    
    print("\n¡Anotación exitosa!")
    for key, val in coords.items():
        print(f"  {key}: {val}")

if __name__ == "__main__":
    main()