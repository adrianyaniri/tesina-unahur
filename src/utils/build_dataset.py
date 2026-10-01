import os
import re
from pathlib import Path
import pandas as pd


def generate_cortes():
    base_dir = Path(__file__).resolve().parent.parent
    img_dir = base_dir / "data" / "imagenes" / "originales"
    exp_path = base_dir / "docs" / "experiments.csv"

    df_exp = pd.read_csv(exp_path)
    pattern = re.compile(
        r"Cordon(\d+)_Seccion\s*(\d+)\s*horizontal\s*C\1\.jpg", re.IGNORECASE
    )

    records = []
    for fname in os.listdir(img_dir):
        if fname.lower().endswith(".jpg"):
            m = pattern.match(fname)
            if m:
                cordon = int(m.group(1))
                seccion = int(m.group(2))
                if cordon != 15:
                    records.append({
                        "ruta": fname,
                        "experimento_id": cordon,
                        "seccion": seccion,
                    })

    df_imgs = pd.DataFrame(records)
    merged = pd.merge(
        df_imgs,
        df_exp,
        left_on="experimento_id",
        right_on="experiencia_id",
        how="inner",
    )
    merged = merged.sort_values(by=["experimento_id", "seccion"]).reset_index(
        drop=True
    )

    merged["corte_id"] = range(1, len(merged) + 1)

    empty_cols = [
        "scale_start_x",
        "scale_start_y",
        "scale_end_x",
        "scale_end_y",
        "base_left_x",
        "base_left_y",
        "base_right_x",
        "base_right_y",
    ]
    for col in empty_cols:
        merged[col] = ""

    cols = [
        "corte_id",
        "experimento_id",
        "seccion",
        "ruta",
        "scale_start_x",
        "scale_start_y",
        "scale_end_x",
        "scale_end_y",
        "base_left_x",
        "base_left_y",
        "base_right_x",
        "base_right_y",
        "Perilla voltaje [unidades de marca]",
        "Perilla vel. alambre [unidades de marca]",
        "Flujo de gas [litros /min]",
        "Voltaje [volts]",
        "Corriente [ampers]",
    ]

    df_final = merged[cols]

    out_data = base_dir / "data" / "cortes.csv"
    out_raw = base_dir / "data" / "raw" / "cortes.csv"
    out_docs = base_dir / "docs" / "cortes.csv"

    df_final.to_csv(out_data, index=False, encoding="utf-8")
    df_final.to_csv(out_raw, index=False, encoding="utf-8")
    df_final.to_csv(out_docs, index=False, encoding="utf-8")

    print(f"cortes.csv generado exitosamente con {len(df_final)} filas.")


if __name__ == "__main__":
    generate_cortes()
