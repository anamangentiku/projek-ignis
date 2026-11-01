"""
Generator Dataset Simulasi Karhutla untuk IGNIS.
Membuat >= 110 data simulasi laporan karhutla realistis di hotspot Indonesia:
Riau, Sumsel, Jambi, Kalbar, Kalteng, Kalsel, dan Jatim.
Menyimpan ke CSV dan otomatis menginisialisasi SQLite database dengan flag is_simulated=1.
"""

import os
import sys
import random
import pandas as pd
from datetime import datetime, timedelta

# Pastikan root proyek ada di sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REGIONS = [
    {
        "provinsi": "Riau",
        "kabupaten": "Bengkalis",
        "lat_center": 1.4800,
        "lon_center": 102.1300,
        "default_land": "Gambut",
        "lokasi_list": ["Desa Sepahat, Kec. Bandar Laksamana", "Desa Temiang, Kec. Bukit Batu", "Desa Muntai, Kec. Bantan", "Kawasan Cagar Biosfer Giam Siak Kecil"]
    },
    {
        "provinsi": "Riau",
        "kabupaten": "Pelalawan",
        "lat_center": 0.3500,
        "lon_center": 102.0500,
        "default_land": "Perkebunan Sawit",
        "lokasi_list": ["Desa Teluk Meranti, Semenanjung Kampar", "Kec. Langgam KM 18", "Desa Kuala Panduk", "Kecamatan Pangkalan Kuras"]
    },
    {
        "provinsi": "Kalimantan Tengah",
        "kabupaten": "Pulang Pisau",
        "lat_center": -2.7500,
        "lon_center": 114.2500,
        "default_land": "Gambut",
        "lokasi_list": ["Desa Taruna Jaya, Kec. Jabiren Raya", "Kawasan Ex-PLG Blok A", "Desa Garung KM 12", "Kecamatan Kahayan Hilir"]
    },
    {
        "provinsi": "Kalimantan Tengah",
        "kabupaten": "Kotawaringin Timur",
        "lat_center": -2.5300,
        "lon_center": 112.9500,
        "default_land": "Semak Belukar",
        "lokasi_list": ["Jl. Jenderal Sudirman KM 8 Sampit", "Kecamatan Baamang Barat", "Kelurahan Ketapang", "Kecamatan Mentawa Baru Ketapang"]
    },
    {
        "provinsi": "Sumatera Selatan",
        "kabupaten": "Ogan Komering Ilir (OKI)",
        "lat_center": -3.4200,
        "lon_center": 105.0500,
        "default_land": "Gambut",
        "lokasi_list": ["Desa Deling, Kec. Pangkalan Lampam", "Kecamatan Cengal Area Konsesi", "Desa Cinta Jaya, Kec. Pedamaran", "Kecamatan Tulung Selapan Area Rawa"]
    },
    {
        "provinsi": "Kalimantan Barat",
        "kabupaten": "Kubu Raya",
        "lat_center": -0.1500,
        "lon_center": 109.4000,
        "default_land": "Gambut",
        "lokasi_list": ["Dekat Bandara Supadio, Kec. Sungai Raya", "Desa Rasau Jaya Tiga", "Kecamatan Kakap Parit Mayor", "Kawasan Punggur Kecil"]
    },
    {
        "provinsi": "Jambi",
        "kabupaten": "Muaro Jambi",
        "lat_center": -1.5500,
        "lon_center": 103.7500,
        "default_land": "Gambut",
        "lokasi_list": ["Desa Arifin, Kec. Kumpeh Ilir", "Kawasan Hutan Lindung Gambut Londerang", "Desa Betung Kec. Kumpeh", "Batas Taman Nasional Berbak"]
    },
    {
        "provinsi": "Jawa Timur",
        "kabupaten": "Pasuruan / Probolinggo",
        "lat_center": -7.9400,
        "lon_center": 112.9500,
        "default_land": "Hutan Lindung",
        "lokasi_list": ["Blok Savana Lembah Watangan Bromo", "Lereng Gunung Batok TNBTS", "Kawasan Hutan Pinus Ranu Regulo", "Blok Plentongan Bromo"]
    }
]

SEVERITY_LEVELS = ["Rendah", "Sedang", "Tinggi", "Kritis"]

DESCRIPTIONS_BY_SEVERITY = {
    "Kritis": [
        "Kobaran api bawah tanah di lahan gambut kedalaman 2 meter semakin meluas, asap pekat kuning pekat menyelimuti pemukiman warga jarak 200m, jarak pandang < 50 meter, warga sesak napas.",
        "Kebakaran hebat di perbatasan konsesi dan perkebunan rakyat merembet cepat terbawa angin kencang ke arah perumahan penduduk dan sekolah dasar. Api melalap lebih dari 15 hektar.",
        "Titik api aktif melingkari kawasan konservasi gambut dalam, terdengar suara gemeretak kayu terbakar dan api meloncat melompati sekat kanal, butuh water bombing segera!",
        "Lahan gambut kering terbakar hebat dekat bandara, kabut asap tebal mengganggu jadwal penerbangan dan jarak ke perumahan hanya sekitar 300 meter."
    ],
    "Tinggi": [
        "Kepulan asap membubung tinggi dari semak belukar kering bekas tebasan, api merambat ke kebun sawit produktif milik warga, warga berusaha memadamkan dengan ranting pohon.",
        "Kebakaran lahan seluas kira-kira 4 hektar di tepi jalan poros antar kecamatan, lalu lintas terganggu akibat asap pekat, potensi menjalar ke gardu listrik PLN.",
        "Titik api terpantau di 3 titik terpisah dalam radius 500 meter di lahan terbuka gambut, diduga sengaja dibakar untuk pembukaan ladang baru.",
        "Api membakar vegetasi alang-alang dan serasah kering di lereng curam, sulit dijangkau kendaraan darat karena akses jalan sempit dan tidak ada sumber air terdekat."
    ],
    "Sedang": [
        "Terlihat asap putih keabu-abuan dari sisa pembakaran tumpukan ilalang di lahan kosong warga, api masih menyala kecil namun rawan membesar jika angin kencang bertiup sore nanti.",
        "Warga melihat bekas pembakaran jerami dan tunggul kayu yang ditinggalkan tanpa pengawasan di pinggir parit, ada titik bara aktif.",
        "Kebakaran spot kecil di pinggir kebun karet sekitar 0.5 hektar, sudah mulai dilokalisir warga menggunakan cangkul tetapi butuh bantuan pompa air apung.",
        "Asap tipis mengepul di dekat tanggul kanal yang mengering, vegetasi pakis-pakisan mulai menguning dan gosong di tepi parit."
    ],
    "Rendah": [
        "Warga membersihkan pekarangan dan membakar sampah daun kering di drum besi, ada sedikit asap tapi terpantau terkendali oleh pemilik lahan.",
        "Sisa bara api unggun pemburu burung di tepi rawa sudah dipadamkan sebagian dengan air lumpur, sisa asap tipis tanpa kobaran api aktif.",
        "Titik panas kecil terpantau di lahan tanah mineral basah pasca hujan gerimis, tidak ada potensi penyebaran api.",
        "Laporan kepulan debu tebal terduga asap oleh warga dari kejauhan, setelah dicek ternyata pembersihan lahan manual dengan traktor mini."
    ]
}

NAMES = [
    "Budi Santoso", "Agus Setiawan", "Rahmat Hidayat", "Siti Aminah", "Joko Prasetyo",
    "Hendra Kurniawan", "Eko Prasojo", "Ahmad Fauzi", "Dewi Lestari", "Rian Haryanto",
    "Bambang Sutrisno", "I Wayan Subekti", "M. Yusuf", "Syarifuddin", "Dian Permata",
    "Supardi", "Nurdin Halim", "Zulkifli", "Herman Susanto", "Rudi Hartono"
]

def calculate_reference_score(keparahan: str, jarak_km: float, tipe_lahan: str, cluster_count: int, luas_ha: float) -> (float, str):
    """Menghitung skor prioritas acuan (Ground Truth 0-100) dan labelnya."""
    # Bobot Keparahan (0 - 35)
    sev_map = {"Rendah": 10, "Sedang": 20, "Tinggi": 30, "Kritis": 35}
    s_sev = sev_map.get(keparahan, 20)
    
    # Bobot Kedekatan Pemukiman (0 - 30)
    # Semakin dekat ke pemukiman, semakin berbahaya
    if jarak_km <= 0.3:
        s_prox = 30
    elif jarak_km <= 1.0:
        s_prox = 24
    elif jarak_km <= 2.5:
        s_prox = 16
    elif jarak_km <= 5.0:
        s_prox = 8
    else:
        s_prox = 3

    # Bobot Kerentanan Tipe Lahan (0 - 20)
    land_map = {
        "Gambut": 20,
        "Hutan Lindung": 18,
        "Perkebunan Sawit": 14,
        "Semak Belukar": 10,
        "Lahan Terbuka / Pertanian": 6
    }
    s_land = land_map.get(tipe_lahan, 10)

    # Bobot Klaster Laporan / Luas (0 - 15)
    s_clust = min(15, (cluster_count * 3) + min(6, int(luas_ha * 0.5)))

    total_score = round(min(100.0, s_sev + s_prox + s_land + s_clust), 1)

    if total_score >= 75.0:
        label = "Kritis"
    elif total_score >= 55.0:
        label = "Tinggi"
    elif total_score >= 35.0:
        label = "Sedang"
    else:
        label = "Rendah"

    return total_score, label

def generate_dataset(n_samples: int = 115) -> pd.DataFrame:
    """Menghasilkan dataframe simulasi karhutla berbobot realistis."""
    random.seed(42)
    records = []
    base_time = datetime.now() - timedelta(days=25)

    for i in range(1, n_samples + 1):
        reg = random.choice(REGIONS)
        # Random jitter pada koordinat sekitar pusat
        lat = round(reg["lat_center"] + random.uniform(-0.12, 0.12), 5)
        lon = round(reg["lon_center"] + random.uniform(-0.12, 0.12), 5)
        
        # Probabilitas keparahan realistis (Sedang dan Tinggi lebih sering muncul)
        keparahan = random.choices(SEVERITY_LEVELS, weights=[0.20, 0.40, 0.28, 0.12])[0]
        
        # Tipe lahan
        if random.random() < 0.65:
            tipe_lahan = reg["default_land"]
        else:
            tipe_lahan = random.choice(["Gambut", "Semak Belukar", "Perkebunan Sawit", "Hutan Lindung", "Lahan Terbuka / Pertanian"])

        # Jarak ke pemukiman (km)
        if keparahan == "Kritis":
            jarak_km = round(random.uniform(0.1, 1.2), 2)
            luas_ha = round(random.uniform(4.0, 35.0), 1)
            cluster_count = random.randint(2, 6)
        elif keparahan == "Tinggi":
            jarak_km = round(random.uniform(0.5, 3.5), 2)
            luas_ha = round(random.uniform(2.0, 15.0), 1)
            cluster_count = random.randint(1, 4)
        elif keparahan == "Sedang":
            jarak_km = round(random.uniform(1.0, 6.0), 2)
            luas_ha = round(random.uniform(0.5, 4.0), 1)
            cluster_count = random.randint(1, 2)
        else:
            jarak_km = round(random.uniform(2.0, 10.0), 2)
            luas_ha = round(random.uniform(0.1, 1.5), 1)
            cluster_count = 1

        # Tanggal lapor
        delta_seconds = random.randint(0, 25 * 86400)
        tgl = (base_time + timedelta(seconds=delta_seconds)).strftime("%Y-%m-%d %H:%M:%S")

        deskripsi = random.choice(DESCRIPTIONS_BY_SEVERITY[keparahan])
        lokasi = f"{random.choice(reg['lokasi_list'])} ({lat:.3f}, {lon:.3f})"
        pelapor = random.choice(NAMES)
        kontak = f"08{random.randint(11, 89)}{random.randint(1000000, 9999999)}"

        # Ground truth score
        score_acuan, label_acuan = calculate_reference_score(keparahan, jarak_km, tipe_lahan, cluster_count, luas_ha)

        # Status verifikasi
        if keparahan in ["Kritis", "Tinggi"] and random.random() < 0.7:
            status_petugas = "Terverifikasi Valid"
            catatan_petugas = "Dikonfirmasi langsung oleh Regu Manggala Agni / BPBD setempat."
        elif keparahan == "Rendah" and random.random() < 0.3:
            status_petugas = "Ditolak / Palsu"
            catatan_petugas = "Setelah dicek patroli drone, hanya pembakaran sampah pekarangan terkendali."
        else:
            status_petugas = random.choice(["Menunggu Verifikasi", "Terverifikasi Valid", "Perlu Investigasi Lapangan"])
            catatan_petugas = "Dalam proses pemantauan satelit dan tim reaksi cepat."

        status_sistem = "Terverifikasi Otomatis" if cluster_count == 1 else f"Terverifikasi Otomatis (Klaster {cluster_count} Laporan)"

        # Catatan rincian XAI awal
        alasan = (
            f"[Sistem XAI] Bobot Keparahan ({keparahan}), "
            f"Jarak ke Pemukiman ({jarak_km} km), "
            f"Tipe Lahan Ekologis ({tipe_lahan}), "
            f"Indeks Klaster ({cluster_count} laporan sejenis)."
        )

        records.append({
            "kode_laporan": f"IGNIS-SIM-{i:04d}",
            "tanggal_lapor": tgl,
            "nama_pelapor": pelapor,
            "kontak_pelapor": kontak,
            "lokasi": lokasi,
            "kabupaten": reg["kabupaten"],
            "provinsi": reg["provinsi"],
            "latitude": lat,
            "longitude": lon,
            "deskripsi": deskripsi,
            "keparahan": keparahan,
            "tipe_lahan": tipe_lahan,
            "jarak_pemukiman_km": jarak_km,
            "luas_estimasi_ha": luas_ha,
            "bukti_url": f"https://ignis-storage.internal/evidence/img_{i:04d}.jpg",
            "jumlah_laporan_serupa": cluster_count,
            "status_verifikasi_sistem": status_sistem,
            "status_verifikasi_petugas": status_petugas,
            "catatan_petugas": catatan_petugas,
            "skor_prioritas": score_acuan,
            "label_prioritas": label_acuan,
            "alasan_skor": alasan,
            "is_simulated": 1,
            "created_at": tgl
        })

    # Tambahkan 3 contoh kasus anomali / tepi untuk pengujian preprocessing & audit:
    # 1 kasus dengan spasi liar & html
    records.append({
        "kode_laporan": f"IGNIS-SIM-{n_samples+1:04d}",
        "tanggal_lapor": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "nama_pelapor": "<b>Warga Anonim</b>",
        "kontak_pelapor": "081234567890",
        "lokasi": "    Kecamatan Sebangau Dekat Parit 4   ",
        "kabupaten": "Pulang Pisau",
        "provinsi": "Kalimantan Tengah",
        "latitude": -2.3500,
        "longitude": 113.8000,
        "deskripsi": "  Kebakaran di lahan gambut   dalam   <script>alert(1)</script> asap sangat tebal membahayakan balita.  ",
        "keparahan": "Tinggi",
        "tipe_lahan": "Gambut",
        "jarak_pemukiman_km": 0.4,
        "luas_estimasi_ha": 3.0,
        "bukti_url": "https://ignis-storage.internal/evidence/anomali_1.jpg",
        "jumlah_laporan_serupa": 2,
        "status_verifikasi_sistem": "Menunggu Evaluasi",
        "status_verifikasi_petugas": "Menunggu Verifikasi",
        "catatan_petugas": "",
        "skor_prioritas": 78.5,
        "label_prioritas": "Kritis",
        "alasan_skor": "Evaluasi anomali input.",
        "is_simulated": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # 1 kasus duplikat koordinat untuk menguji verifier
    records.append({
        "kode_laporan": f"IGNIS-SIM-{n_samples+2:04d}",
        "tanggal_lapor": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "nama_pelapor": "Pak RT 04",
        "kontak_pelapor": "081298765432",
        "lokasi": "Desa Sepahat, Kec. Bandar Laksamana (1.480, 102.130)",
        "kabupaten": "Bengkalis",
        "provinsi": "Riau",
        "latitude": 1.4800,
        "longitude": 102.1300,
        "deskripsi": "Laporan susulan api di Desa Sepahat dekat kebun kelapa sawit makin meluas ke arah barat.",
        "keparahan": "Sedang",
        "tipe_lahan": "Gambut",
        "jarak_pemukiman_km": 1.5,
        "luas_estimasi_ha": 2.0,
        "bukti_url": "https://ignis-storage.internal/evidence/dup_2.jpg",
        "jumlah_laporan_serupa": 3,
        "status_verifikasi_sistem": "Terindikasi Duplikat",
        "status_verifikasi_petugas": "Menunggu Verifikasi",
        "catatan_petugas": "",
        "skor_prioritas": 58.0,
        "label_prioritas": "Tinggi",
        "alasan_skor": "Laporan klaster terdeteksi.",
        "is_simulated": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return pd.DataFrame(records)

def save_and_seed_database():
    """Menyimpan dataset simulasi ke file CSV dan memasukkan ke SQLite."""
    from database.db_manager import init_db, get_connection
    
    init_db()
    df = generate_dataset(115)
    
    # Simpan CSV
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_simulasi_karhutla.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset simulasi tersimpan di {csv_path} dengan {len(df)} baris.")

    # Seed ke SQLite jika tabel laporan masih kosong
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM laporan")
    count = cursor.fetchone()[0]
    
    if count == 0:
        df.to_sql("laporan", conn, if_exists="append", index=False)
        print(f"Berhasil seeding {len(df)} rekaman ke database SQLite.")
    else:
        print(f"Database sudah berisi {count} data, melewati seeding otomatis.")
    
    conn.close()

if __name__ == "__main__":
    save_and_seed_database()
