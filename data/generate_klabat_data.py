"""
Seeder Data Kebakaran Hutan & Lahan di Gunung Klabat, Minahasa Utara.
Menghasilkan laporan realistis di berbagai titik lereng dan jalur pendakian Gunung Klabat.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import init_db, get_connection

KLABAT_SPOTS = []

def calculate_klabat_priority(keparahan: str, jarak_km: float, vegetasi: str) -> (float, str, str):
    """
    Menghitung skor prioritas risiko kebakaran di lereng Gunung Klabat.
    Fokus utama: Keselamatan pemukiman lereng dan keselamatan pendaki di jalur gunung.
    """
    # 1. Bobot Keparahan (0 - 40)
    sev_map = {"Kritis": 40.0, "Tinggi": 28.0, "Sedang": 18.0, "Rendah": 8.0}
    s_sev = sev_map.get(keparahan, 20.0)

    # 2. Bobot Kedekatan Pemukiman / Jalur Pendakian (0 - 35)
    if jarak_km <= 0.4:
        s_jarak = 35.0
        ket_jarak = "Sangat dekat pemukiman warga lereng (< 400 meter), ancaman langsung bangunan dan warga."
    elif jarak_km <= 1.0:
        s_jarak = 26.0
        ket_jarak = "Dekat pemukiman / akses wisata Kaki Dian (400m - 1 km)."
    elif jarak_km <= 2.5:
        s_jarak = 18.0
        ket_jarak = "Area jalur pendakian aktif, potensi membahayakan rute evakuasi pendaki."
    else:
        s_jarak = 8.0
        ket_jarak = "Jauh dari pemukiman (> 2.5 km), di ketinggian hutan / savana puncak."

    # 3. Bobot Tipe Vegetasi (0 - 25)
    if "Semak" in vegetasi or "Alang-alang" in vegetasi:
        s_veg = 25.0
        ket_veg = "Bahan bakar vegetasi kering sangat mudah merambat cepat tersapu angin lereng."
    elif "Cengkeh" in vegetasi or "Pala" in vegetasi or "Kebun" in vegetasi:
        s_veg = 20.0
        ket_veg = "Perkebunan rakyat produktif, risiko kerugian ekonomi warga lokal tinggi."
    elif "Savana" in vegetasi:
        s_veg = 16.0
        ket_veg = "Padang rumput puncak mudah membakar namun terisolasi dari perumahan."
    else:
        s_veg = 12.0
        ket_veg = "Hutan kanopi basah."

    total_skor = round(min(100.0, s_sev + s_jarak + s_veg), 1)

    if total_skor >= 75.0:
        label = "Kritis"
    elif total_skor >= 55.0:
        label = "Tinggi"
    elif total_skor >= 35.0:
        label = "Sedang"
    else:
        label = "Rendah"

    alasan = f"Skor {total_skor}/100 ({label}). {ket_jarak} {ket_veg}"
    return total_skor, label, alasan

def seed_klabat_database():
    """Mengisi database dengan laporan Gunung Klabat."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM laporan_klabat")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return

    base_time = datetime.now() - timedelta(hours=14)

    for i, s in enumerate(KLABAT_SPOTS, start=1):
        gmaps_link = f"https://www.google.com/maps?q={s['lat']},{s['lon']}"
        skor, label, alasan = calculate_klabat_priority(s["keparahan"], s["jarak_pemukiman_km"], s["vegetasi"])
        tgl = (base_time + timedelta(hours=i * 1.5)).strftime("%Y-%m-%d %H:%M:%S")

        status_penanganan = "Menunggu Penanganan"
        if i in [1, 2]:
            status_penanganan = "Tim Menuju Lokasi"
        elif i == 3:
            status_penanganan = "Sedang Dipadamkan"

        cursor.execute("""
        INSERT INTO laporan_klabat (
            kode_laporan, tanggal_lapor, nama_user, kontak_user,
            link_lokasi, gambar_kebakaran, deskripsi_tempat, lokasi_area,
            latitude, longitude, keparahan, tipe_vegetasi, jarak_pemukiman_km,
            skor_prioritas, label_prioritas, alasan_prioritas, status_penanganan,
            catatan_tim, is_simulated, created_at
        ) VALUES (
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?
        )
        """, (
            f"KLB-2026-{i:03d}",
            tgl,
            s["pelapor"],
            s["kontak"],
            gmaps_link,
            s["gambar"],
            s["deskripsi"],
            s["area"],
            s["lat"],
            s["lon"],
            s["keparahan"],
            s["vegetasi"],
            s["jarak_pemukiman_km"],
            skor,
            label,
            alasan,
            status_penanganan,
            "Regu Posko Damkar Airmadidi & BPBD Minut telah menerima notifikasi.",
            1,
            tgl
        ))

    conn.commit()
    conn.close()
    print("Database Gunung Klabat berhasil diisi dengan data awal.")

if __name__ == "__main__":
    seed_klabat_database()
