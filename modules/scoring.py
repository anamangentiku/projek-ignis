"""
Explainable AI (XAI) Risk Scoring Module for IGNIS.
Menghitung skor prioritas risiko kebakaran hutan dan lahan (0-100)
berdasarkan formula berbobot multi-kriteria yang transparan dan dapat dijelaskan (Explainable AI).
"""

from typing import Dict, Any, Tuple

def calculate_risk_score(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menghitung skor prioritas risiko 0-100 dengan transparansi penuh (XAI).
    
    Formula Pembobotan:
    Skor Total = S_keparahan (30%) + S_jarak (25%) + S_lahan (20%) + S_klaster (15%) + S_bukti (10%) - Penalti
    """
    breakdown = {}
    
    # 1. Komponen Keparahan Kejadian (Maks 30 Poin)
    keparahan = str(report.get("keparahan", "Sedang")).capitalize()
    keparahan_table = {
        "Kritis": (30.0, "Kobaran api massif / kabut pekat membahayakan nyawa langsung"),
        "Tinggi": (22.0, "Api aktif merambat cepat dan vegetasi sangat kering"),
        "Sedang": (14.0, "Titik api terlokalisir atau bara api berpotensi meluas"),
        "Rendah": (6.0, "Sisa pembakaran terkendali atau titik panas terisolasi")
    }
    s_keparahan, alasan_keparahan = keparahan_table.get(keparahan, (14.0, "Kategori standar"))
    breakdown["keparahan"] = {
        "nama": "Tingkat Keparahan Kejadian",
        "bobot_maks": 30.0,
        "skor_didapat": s_keparahan,
        "nilai_input": keparahan,
        "alasan": f"Status '{keparahan}' berkontribusi {s_keparahan} dari 30 poin. {alasan_keparahan}."
    }

    # 2. Komponen Kedekatan Pemukiman / Fasilitas Publik (Maks 25 Poin)
    try:
        jarak_km = float(report.get("jarak_pemukiman_km", 2.5))
    except (ValueError, TypeError):
        jarak_km = 2.5

    if jarak_km <= 0.3:
        s_jarak = 25.0
        alasan_jarak = "Sangat dekat pemukiman (< 300m), risiko tinggi ISPA dan korban jiwa"
    elif jarak_km <= 1.0:
        s_jarak = 20.0
        alasan_jarak = "Dekat pemukiman (300m - 1km), asap tebal mulai masuk perumahan"
    elif jarak_km <= 2.5:
        s_jarak = 14.0
        alasan_jarak = "Zona penyangga sedang (1km - 2.5km) dari fasilitas penduduk"
    elif jarak_km <= 5.0:
        s_jarak = 8.0
        alasan_jarak = "Cukup jauh dari pemukiman (2.5km - 5km)"
    else:
        s_jarak = 3.0
        alasan_jarak = "Sangat jauh (> 5km), dampak langsung ke pemukiman minim"

    breakdown["jarak_pemukiman"] = {
        "nama": "Kedekatan Pemukiman Warga",
        "bobot_maks": 25.0,
        "skor_didapat": s_jarak,
        "nilai_input": f"{jarak_km:.2f} km",
        "alasan": f"Jarak {jarak_km:.2f} km menghasilkan skor {s_jarak} dari 25 poin. {alasan_jarak}."
    }

    # 3. Komponen Kerentanan Ekologis Tipe Lahan (Maks 20 Poin)
    tipe_lahan = str(report.get("tipe_lahan", "Semak Belukar"))
    lahan_table = {
        "Gambut": (20.0, "Gambut memiliki risiko bara bawah tanah (smoldering) sangat sulit dipadamkan dan emisi karbon tinggi"),
        "Hutan Lindung": (17.0, "Mengancam ekosistem keanekaragaman hayati dan kawasan resapan air utama"),
        "Perkebunan Sawit": (13.0, "Potensi kerugian ekonomi perkebunan dan penyebaran api cepat melalui kanal"),
        "Semak Belukar": (10.0, "Bahan bakar vegetasi kering mudah terbakar namun relatif dapat diatasi di permukaan"),
        "Lahan Terbuka / Pertanian": (6.0, "Topografi terbuka memudahkan manuver armada pemadam darat")
    }
    s_lahan, alasan_lahan = lahan_table.get(tipe_lahan, (10.0, "Tipe lahan umum"))
    breakdown["tipe_lahan"] = {
        "nama": "Kerentanan Ekologis Lahan",
        "bobot_maks": 20.0,
        "skor_didapat": s_lahan,
        "nilai_input": tipe_lahan,
        "alasan": f"Tipe '{tipe_lahan}' bernilai {s_lahan} dari 20 poin. {alasan_lahan}."
    }

    # 4. Komponen Klaster Laporan Spasio-Temporal (Maks 15 Poin)
    try:
        klaster = int(report.get("jumlah_laporan_serupa", 1))
    except (ValueError, TypeError):
        klaster = 1

    if klaster >= 4:
        s_klaster = 15.0
        alasan_klaster = f"Terdeteksi klaster massif ({klaster} laporan warga berbeda), validitas kejadian sangat tinggi"
    elif klaster >= 2:
        s_klaster = 10.0
        alasan_klaster = f"Terdeteksi beberapa laporan warga serupa ({klaster} laporan) di area yang sama"
    else:
        s_klaster = 4.0
        alasan_klaster = "Laporan tunggal dari 1 pelapor, sedang menunggu laporan pembanding"

    breakdown["klaster_laporan"] = {
        "nama": "Klaster Laporan Sekitar",
        "bobot_maks": 15.0,
        "skor_didapat": s_klaster,
        "nilai_input": f"{klaster} laporan",
        "alasan": f"Indeks klaster ({klaster} laporan) memberi {s_klaster} dari 15 poin. {alasan_klaster}."
    }

    # 5. Komponen Kelengkapan Bukti & Kredibilitas (Maks 10 Poin)
    bukti_url = str(report.get("bukti_url", "")).strip()
    kontak = str(report.get("kontak_pelapor", "")).strip()
    has_bukti = len(bukti_url) > 5
    has_kontak = len(kontak) >= 8

    if has_bukti and has_kontak:
        s_bukti = 10.0
        alasan_bukti = "Laporan lengkap dengan lampiran bukti dokumentasi dan kontak pelapor aktif"
    elif has_bukti or has_kontak:
        s_bukti = 6.0
        alasan_bukti = "Laporan memiliki sebagian bukti atau nomor kontak pelapor tertera"
    else:
        s_bukti = 2.0
        alasan_bukti = "Laporan minim data verifikasi pendukung (tanpa bukti foto dan kontak)"

    breakdown["kelengkapan_bukti"] = {
        "nama": "Kelengkapan Bukti & Kredibilitas",
        "bobot_maks": 10.0,
        "skor_didapat": s_bukti,
        "nilai_input": "Lengkap" if (has_bukti and has_kontak) else ("Parsial" if (has_bukti or has_kontak) else "Minim"),
        "alasan": f"Kredibilitas laporan dinilai {s_bukti} dari 10 poin. {alasan_bukti}."
    }

    # Penalti jika ada anomali koordinat
    penalty = 0.0
    status_sistem = str(report.get("status_verifikasi_sistem", ""))
    if "Anomali Koordinat" in status_sistem:
        penalty = 25.0
        breakdown["penalti_anomali"] = {
            "nama": "Penalti Anomali Koordinat",
            "bobot_maks": 0.0,
            "skor_didapat": -25.0,
            "nilai_input": "Koordinat di luar RI",
            "alasan": "Koordinat tidak valid dikenai penalti pengurangan 25 poin untuk mencegah false emergency."
        }

    # Total Skor
    total_skor = s_keparahan + s_jarak + s_lahan + s_klaster + s_bukti - penalty
    total_skor = round(max(0.0, min(100.0, total_skor)), 1)

    # Klasifikasi Label
    if total_skor >= 75.0:
        label = "Kritis"
        badge_color = "#E63946"  # Merah menyala
        rekomendasi_aksi = "Mobilisasi Darurat: Helikopter Water Bombing & Regu Khusus Gabungan (TNI/Polri/Manggala Agni)"
    elif total_skor >= 55.0:
        label = "Tinggi"
        badge_color = "#F4A261"  # Oranye terang
        rekomendasi_aksi = "Prioritas Utama: Regu Pemadam Darat BPBD & Sekat Bakar Preventif"
    elif total_skor >= 35.0:
        label = "Sedang"
        badge_color = "#E9C46A"  # Kuning emas
        rekomendasi_aksi = "Patroli Terpadu: Pengecekan Sumber Air / Embung dan Monitoring Drone"
    else:
        label = "Rendah"
        badge_color = "#2A9D8F"  # Hijau stabil
        rekomendasi_aksi = "Pemantauan Rutin: Sosialisasi Pencegahan Kebakaran ke Kelompok Tani Peduli Api"

    # Penjelasan XAI Naratif Komprehensif
    narasi_xai = (
        f"Skor Prioritas Risiko dihitung sebesar {total_skor}/100 ({label}). "
        f"Faktor dominan: Keparahan '{keparahan}' (+{s_keparahan} poin), "
        f"Jarak ke Pemukiman {jarak_km:.1f} km (+{s_jarak} poin), serta "
        f"Karakteristik Tipe Lahan '{tipe_lahan}' (+{s_lahan} poin). "
        f"Dukungan {klaster} laporan warga (+{s_klaster} poin) dan kredibilitas bukti (+{s_bukti} poin)."
    )

    # Perbandingan Sebelum vs Sesudah Analisis AI
    # Sebelum: Keparahan mentah dari pelapor (subjektif)
    # Sesudah: Prioritas terintegrasi berbasis bukti objektif multi-kriteria
    perbandingan = {
        "sebelum": {
            "sumber": "Laporan Mentah Masyarakat (Subjektif)",
            "keparahan_lapor": keparahan,
            "asumsi_prioritas": "Berdasarkan persepsi pengunggah tanpa kalibrasi risiko"
        },
        "sesudah": {
            "sumber": "Analisis AI Multi-Kriteria IGNIS (Objektif)",
            "skor_terukur": total_skor,
            "label_terukur": label,
            "kalibrasi": "Terverifikasi dengan jarak spasial, tipe ekosistem gambut, dan klaster laporan"
        }
    }

    return {
        "total_skor": total_skor,
        "label": label,
        "badge_color": badge_color,
        "rekomendasi_aksi": rekomendasi_aksi,
        "breakdown": breakdown,
        "narasi_xai": narasi_xai,
        "perbandingan": perbandingan
    }
