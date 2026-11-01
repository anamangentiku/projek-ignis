"""
Preprocessing & Quality Evaluation Module for IGNIS
Menangani pembersihan teks, validasi geografis, imputasi missing values, normalisasi data, dan audit kualitas dataset.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

# Bounding box koordinat wilayah kedaulatan Republik Indonesia
INDONESIA_BBOX = {
    "lat_min": -11.5,
    "lat_max": 6.5,
    "lon_min": 94.5,
    "lon_max": 141.5
}

VALID_KEPARAHAN = ["Rendah", "Sedang", "Tinggi", "Kritis"]
VALID_TIPE_LAHAN = [
    "Gambut", 
    "Hutan Lindung", 
    "Perkebunan Sawit", 
    "Semak Belukar", 
    "Lahan Terbuka / Pertanian"
]

def clean_text(text: Any) -> str:
    """Membersihkan teks deskripsi dari spasi berlebih, tag HTML/Script, atau karakter aneh."""
    if text is None or pd.isna(text):
        return ""
    text_str = str(text)
    # Hapus tag script/style dan isinya
    text_clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text_str, flags=re.IGNORECASE | re.DOTALL)
    # Hapus tag HTML lainnya jika ada
    text_clean = re.sub(r"<[^>]+>", "", text_clean)
    # Hapus whitespace ganda & baris kosong berlebih
    text_clean = re.sub(r"\s+", " ", text_clean).strip()
    return text_clean

def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Memvalidasi apakah latitude dan longitude berada di wilayah Indonesia dan masuk akal.
    """
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return False, "Koordinat bukan angka valid"

    if np.isnan(lat) or np.isnan(lon):
        return False, "Koordinat tidak boleh NaN/kosong"

    if not (INDONESIA_BBOX["lat_min"] <= lat <= INDONESIA_BBOX["lat_max"]):
        return False, f"Latitude {lat:.4f} di luar batas wilayah Indonesia (-11.5° s/d 6.5°)"
    
    if not (INDONESIA_BBOX["lon_min"] <= lon <= INDONESIA_BBOX["lon_max"]):
        return False, f"Longitude {lon:.4f} di luar batas wilayah Indonesia (94.5° s/d 141.5°)"

    return True, "Koordinat valid"

def normalize_keparahan(val: Any) -> str:
    """Menormalisasi nilai tingkat keparahan ke standar valid."""
    if not val or pd.isna(val):
        return "Sedang"
    v = str(val).strip().capitalize()
    mapping = {
        "Low": "Rendah", "Rendah": "Rendah", "1": "Rendah",
        "Medium": "Sedang", "Sedang": "Sedang", "2": "Sedang",
        "High": "Tinggi", "Tinggi": "Tinggi", "3": "Tinggi",
        "Critical": "Kritis", "Kritis": "Kritis", "4": "Kritis", "Parah": "Kritis"
    }
    return mapping.get(v, "Sedang")

def normalize_tipe_lahan(val: Any) -> str:
    """Menormalisasi tipe lahan ke standar valid."""
    if not val or pd.isna(val):
        return "Lahan Terbuka / Pertanian"
    v = str(val).strip()
    v_lower = v.lower()
    if "gambut" in v_lower:
        return "Gambut"
    elif "hutan" in v_lower or "lindung" in v_lower or "konservasi" in v_lower:
        return "Hutan Lindung"
    elif "sawit" in v_lower or "kebun" in v_lower or "perkebunan" in v_lower:
        return "Perkebunan Sawit"
    elif "semak" in v_lower or "belukar" in v_lower or "alang" in v_lower:
        return "Semak Belukar"
    else:
        return "Lahan Terbuka / Pertanian"

def preprocess_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Melakukan pipeline preprocessing lengkap:
    1. Backup data mentah
    2. Pembersihan teks nama, lokasi, deskripsi
    3. Normalisasi keparahan dan tipe lahan
    4. Validasi dan penanganan missing values
    5. Audit anomali koordinat
    6. Menghitung ringkasan perbaikan
    """
    cleaned_df = df.copy()
    initial_rows = len(cleaned_df)
    
    # Track metrics preprocessing
    stats = {
        "initial_rows": initial_rows,
        "missing_values_imputed": 0,
        "text_cleaned_count": 0,
        "invalid_coords_flagged": 0,
        "normalized_categories_count": 0
    }

    # Kolom wajib standar
    col_mapping = {
        "lat": "latitude",
        "lon": "longitude",
        "long": "longitude",
        "desc": "deskripsi",
        "keterangan": "deskripsi",
        "severity": "keparahan",
        "land_type": "tipe_lahan"
    }
    cleaned_df.rename(columns={k: v for k, v in col_mapping.items() if k in cleaned_df.columns}, inplace=True)

    # 1. Bersihkan Deskripsi & Lokasi
    if "deskripsi" in cleaned_df.columns:
        cleaned_df["deskripsi"] = cleaned_df["deskripsi"].apply(clean_text)
        stats["text_cleaned_count"] += len(cleaned_df)
    else:
        cleaned_df["deskripsi"] = "Laporan kebakaran lahan tanpa deskripsi detail."

    if "lokasi" in cleaned_df.columns:
        cleaned_df["lokasi"] = cleaned_df["lokasi"].apply(clean_text)
    else:
        cleaned_df["lokasi"] = "Lokasi belum terspesifikasi"

    # 2. Imputasi & Normalisasi
    if "keparahan" in cleaned_df.columns:
        cleaned_df["keparahan"] = cleaned_df["keparahan"].apply(normalize_keparahan)
    else:
        cleaned_df["keparahan"] = "Sedang"

    if "tipe_lahan" in cleaned_df.columns:
        cleaned_df["tipe_lahan"] = cleaned_df["tipe_lahan"].apply(normalize_tipe_lahan)
    else:
        cleaned_df["tipe_lahan"] = "Semak Belukar"

    # Jarak pemukiman
    if "jarak_pemukiman_km" in cleaned_df.columns:
        missing_dist = cleaned_df["jarak_pemukiman_km"].isna().sum()
        stats["missing_values_imputed"] += int(missing_dist)
        cleaned_df["jarak_pemukiman_km"] = pd.to_numeric(cleaned_df["jarak_pemukiman_km"], errors="coerce").fillna(2.5)
        cleaned_df["jarak_pemukiman_km"] = cleaned_df["jarak_pemukiman_km"].apply(lambda x: max(0.05, float(x)))
    else:
        cleaned_df["jarak_pemukiman_km"] = 2.5

    # Luas estimasi
    if "luas_estimasi_ha" in cleaned_df.columns:
        cleaned_df["luas_estimasi_ha"] = pd.to_numeric(cleaned_df["luas_estimasi_ha"], errors="coerce").fillna(1.0)
    else:
        cleaned_df["luas_estimasi_ha"] = 1.0

    # 3. Validasi Geografis
    coords_valid_mask = []
    coord_errors = []
    for _, row in cleaned_df.iterrows():
        lat = row.get("latitude", np.nan)
        lon = row.get("longitude", np.nan)
        is_valid, reason = validate_coordinates(lat, lon)
        coords_valid_mask.append(is_valid)
        coord_errors.append(reason)
    
    cleaned_df["is_coord_valid"] = coords_valid_mask
    cleaned_df["coord_validation_notes"] = coord_errors
    stats["invalid_coords_flagged"] = int((~np.array(coords_valid_mask)).sum())

    # Flag status verifikasi sistem jika ada masalah koordinat
    if "status_verifikasi_sistem" not in cleaned_df.columns:
        cleaned_df["status_verifikasi_sistem"] = cleaned_df.apply(
            lambda r: "Anomali Koordinat" if not r["is_coord_valid"] else "Terverifikasi Otomatis",
            axis=1
        )

    return cleaned_df, stats

def evaluate_dataset_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Mengevaluasi kualitas dataset:
    - Kelengkapan data (Completeness)
    - Validitas koordinat
    - Proporsi kategori keparahan
    - Deteksi duplikasi laporan
    - Distribusi tipe lahan
    """
    total = len(df)
    if total == 0:
        return {"error": "Dataset kosong"}

    # Completeness per key column
    key_cols = ["tanggal_lapor", "lokasi", "latitude", "longitude", "deskripsi", "keparahan", "tipe_lahan"]
    present_cols = [c for c in key_cols if c in df.columns]
    null_counts = {c: int(df[c].isna().sum()) for c in present_cols}
    completeness_score = round((1.0 - (sum(null_counts.values()) / (len(present_cols) * total))) * 100, 2)

    # Validitas koordinat
    if "latitude" in df.columns and "longitude" in df.columns:
        valid_coords = sum([
            1 for _, r in df.iterrows() 
            if validate_coordinates(r["latitude"], r["longitude"])[0]
        ])
        coord_validity_ratio = round((valid_coords / total) * 100, 2)
    else:
        coord_validity_ratio = 0.0

    # Duplikasi teks deskripsi atau koordinat identik
    dup_desc = int(df.duplicated(subset=["deskripsi"]).sum()) if "deskripsi" in df.columns else 0
    dup_coords = int(df.duplicated(subset=["latitude", "longitude"]).sum()) if "latitude" in df.columns else 0

    # Distribusi keparahan
    severity_dist = df["keparahan"].value_counts().to_dict() if "keparahan" in df.columns else {}
    land_dist = df["tipe_lahan"].value_counts().to_dict() if "tipe_lahan" in df.columns else {}

    return {
        "total_records": total,
        "completeness_score": completeness_score,
        "coord_validity_ratio": coord_validity_ratio,
        "null_counts": null_counts,
        "duplicate_descriptions": dup_desc,
        "duplicate_coordinates": dup_coords,
        "severity_distribution": severity_dist,
        "land_distribution": land_dist
    }
