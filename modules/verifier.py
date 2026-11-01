"""
Verification and Consistency Validation Module for IGNIS.
Menangani:
1. Deteksi duplikasi spasio-temporal (Haversine formula & delta waktu)
2. Text similarity analysis (Jaccard token similarity)
3. Audit konsistensi laporan (Logika keparahan vs jarak vs deskripsi)
4. Pemisahan tegas verifikasi sistem (otomatis) vs verifikasi petugas posko/lapangan.
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd
from .preprocessing import validate_coordinates

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Menghitung jarak lingkaran besar antara dua titik koordinat (dalam kilometer)
    menggunakan formula Haversine.
    """
    R = 6371.0  # Radius bumi dalam kilometer
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(R * c, 3)

def text_jaccard_similarity(text1: str, text2: str) -> float:
    """Menghitung similaritas Jaccard antara dua string deskripsi."""
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return round(len(intersection) / len(union), 3)

def check_spatial_temporal_duplicates(
    new_lat: float, 
    new_lon: float, 
    new_time_str: str, 
    existing_reports: List[Dict[str, Any]], 
    radius_km: float = 3.5, 
    time_window_hours: float = 36.0
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Mendeteksi apakah laporan baru merupakan duplikasi dari kejadian yang sama
    dalam radius < radius_km dan rentang waktu < time_window_hours.
    """
    duplicates = []
    
    try:
        dt_new = datetime.strptime(new_time_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        dt_new = datetime.now()

    for rep in existing_reports:
        try:
            ex_lat = float(rep["latitude"])
            ex_lon = float(rep["longitude"])
        except (ValueError, KeyError, TypeError):
            continue

        dist = haversine_distance(new_lat, new_lon, ex_lat, ex_lon)
        if dist <= radius_km:
            # Periksa selisih waktu
            time_diff_hours = 0.0
            if "tanggal_lapor" in rep and rep["tanggal_lapor"]:
                try:
                    dt_ex = datetime.strptime(rep["tanggal_lapor"], "%Y-%m-%d %H:%M:%S")
                    time_diff_hours = abs((dt_new - dt_ex).total_seconds()) / 3600.0
                except Exception:
                    time_diff_hours = 0.0

            if time_diff_hours <= time_window_hours:
                duplicates.append({
                    "id": rep.get("id"),
                    "kode_laporan": rep.get("kode_laporan", "N/A"),
                    "jarak_km": dist,
                    "selisih_jam": round(time_diff_hours, 1),
                    "pelapor": rep.get("nama_pelapor", "Anonim"),
                    "keparahan": rep.get("keparahan", "N/A"),
                    "status_petugas": rep.get("status_verifikasi_petugas", "N/A")
                })

    is_duplicate = len(duplicates) > 0
    return is_duplicate, duplicates

def audit_report_consistency(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Melakukan verifikasi logika dan integritas informasi:
    - Validasi koordinat (bounding box Indonesia)
    - Peringatan jika tingkat keparahan bertolak belakang dengan deskripsi / jarak
    - Kelengkapan bukti pendukung
    """
    issues = []
    warnings = []
    score_penalty = 0

    # 1. Bounding box koordinat
    lat = report_data.get("latitude")
    lon = report_data.get("longitude")
    valid_coord, coord_msg = validate_coordinates(lat, lon)
    if not valid_coord:
        issues.append(f"Anomali Koordinat: {coord_msg}")
        score_penalty += 40

    # 2. Kelengkapan data dasar
    desc = str(report_data.get("deskripsi", "")).strip()
    if len(desc) < 15:
        issues.append("Deskripsi terlalu singkat (< 15 karakter). Informasi minim.")
        score_penalty += 15

    # 3. Kontradiksi Keparahan vs Jarak/Deskripsi
    keparahan = report_data.get("keparahan", "Sedang")
    jarak = float(report_data.get("jarak_pemukiman_km", 2.0))
    desc_lower = desc.lower()

    if keparahan == "Kritis" and ("sampah" in desc_lower or "pekarangan" in desc_lower) and jarak > 10:
        warnings.append("Indikasi Hiperbola: Label Kritis tapi teks menyebutkan sampah/pekarangan di jarak jauh (>10 km).")
        score_penalty += 10

    if keparahan == "Rendah" and ("gambut" in desc_lower or "sesak" in desc_lower or "meluas" in desc_lower) and jarak < 0.5:
        warnings.append("Indikasi Under-reporting: Label Rendah padahal api di gambut sangat dekat pemukiman (<500m).")
        score_penalty += 10

    # 4. Bukti foto
    bukti = report_data.get("bukti_url", "")
    has_evidence = bool(bukti and len(str(bukti).strip()) > 5)

    is_valid_report = len(issues) == 0

    return {
        "is_valid": is_valid_report,
        "coord_valid": valid_coord,
        "has_evidence": has_evidence,
        "issues": issues,
        "warnings": warnings,
        "score_penalty": score_penalty,
        "summary": "Valid & Konsisten" if (is_valid_report and len(warnings) == 0) else (
            f"{len(issues)} Kesalahan Kritis, {len(warnings)} Peringatan Logika"
        )
    }

def run_system_verification(report_data: Dict[str, Any], existing_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Orkestrator verifikasi otomatis oleh sistem:
    Menggabungkan audit konsistensi dan deteksi duplikasi klaster.
    """
    consistency = audit_report_consistency(report_data)
    
    lat = float(report_data.get("latitude", 0.0))
    lon = float(report_data.get("longitude", 0.0))
    tgl = report_data.get("tanggal_lapor", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    is_dup, dup_list = check_spatial_temporal_duplicates(lat, lon, tgl, existing_reports)

    if not consistency["coord_valid"]:
        system_status = "Anomali Koordinat"
    elif is_dup:
        system_status = f"Terindikasi Duplikat (Klaster {len(dup_list) + 1} Laporan)"
    elif len(consistency["issues"]) > 0:
        system_status = "Menunggu Data Lengkap"
    else:
        system_status = "Terverifikasi Otomatis"

    return {
        "system_status": system_status,
        "is_duplicate": is_dup,
        "cluster_count": len(dup_list) + 1,
        "duplicates": dup_list,
        "consistency": consistency
    }
