# 🔥 IGNIS (Intelligent Geospatial and Environmental Insight System)
> **Sistem Pelaporan Masyarakat dan Pendukung Keputusan Mitigasi Kebakaran Hutan dan Lahan Berbasis AI**

Aplikasi web modern berbasis **Python**, **Streamlit**, **SQLite**, **Pandas**, **Plotly**, **Folium**, dan **Google Gemini API** dengan antarmuka bertema *Dark Navy*, *Emerald Green*, dan *Fire Orange*.

---

## 🌟 10 Fitur Utama Sistem

1. **📊 Dashboard Intelijen:** Statistik laporan real-time, grafik tren temporal, sebaran provinsi, kategori tipe lahan, dan proporsi prioritas risiko.
2. **📝 Pelaporan Masyarakat:** Formulir terintegrasi (nama, kontak, lokasi, koordinat lat/lon, tanggal, keparahan, tipe lahan, jarak pemukiman, estimasi luasan, bukti foto) langsung tersimpan ke database SQLite.
3. **🗺️ Peta Interaktif Geospasial:** Visualisasi sebaran titik api menggunakan Folium lengkap dengan layer HeatMap kepadatan, penandaan radius dampak, dan popup informatif.
4. **🛡️ Pusat Verifikasi Laporan:** Deteksi duplikasi spasio-temporal (Formula Haversine < 3.5 km & waktu < 36 jam), validasi batas wilayah kedaulatan Indonesia, dan pembedaan tegas verifikasi sistem vs keputusan petugas posko.
5. **🎯 AI Risk Scoring (Explainable AI 0–100):** Penilaian risiko berbasis aturan berbobot multi-kriteria transparan (Keparahan 30%, Kedekatan Pemukiman 25%, Kerentanan Ekologis Lahan 20%, Klaster Laporan 15%, Kelengkapan Bukti 10%) dengan visualisasi formula matematis dan grafik kontribusi faktor.
6. **🔬 Root Cause Analysis (5 Whys):** Rantai penalaran investigasi kausalitas dari gejala permukaan menuju kelemahan mendasar regulasi hidrologis atau operasional sekat kanal.
7. **🐟 Ishikawa Fishbone Diagram:** Visualisasi faktor penyebab ke dalam 5 cabang (Manusia, Lingkungan, Cuaca, Infrastruktur, Penanganan) dengan pembedaan tegas antara *Terverifikasi Empiris* vs *Dugaan Lapangan*.
8. **💬 Asisten Cerdas (AI Grounded Chatbot):** Integrasi Google Gemini API terhubung langsung ke basis data laporan lokal dan SOP Karhutla resmi (Permen LHK P.32/2016 & BRGM) dengan sistem pencegahan halusinasi.
9. **📋 Rekomendasi Mitigasi Taktis:** Penyusunan rencana mitigasi terstruktur (tindakan segera 0-6 jam, jangka pendek, jangka panjang, instansi penanggung jawab, alokasi logistik, dan landasan yuridis).
10. **🧪 Evaluasi & Pengujian AI (3 Mode Kegagalan):** Halaman khusus pengujian kegagalan AI (*Hallucination*, *Priority Misclassification*, dan *Irrelevant Context-Blind Recommendation*) lengkap dengan input pengujian, output awal gagal, ground truth, akar masalah AI, mitigasi guardrail, dan output terverifikasi pasca perbaikan.

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Prasyarat Sistem
- Python 3.10 / 3.11 / 3.12
- Akses internet (opsional jika menggunakan Gemini API, sistem tetap berfungsi 100% dengan mode fallback lokal offline).

### 2. Instalasi Dependensi
Buka terminal / PowerShell dan arahkan ke direktori proyek:
```bash
cd ignis_system
python -m pip install -r requirements.txt
```

### 3. Konfigurasi Variabel Lingkungan (.env)
Salin file template `.env.example` menjadi `.env`:
```bash
copy .env.example .env
```
Buka file `.env` dan masukkan API Key Gemini Anda (dapatkan gratis di [Google AI Studio](https://aistudio.google.com/)):
```env
GEMINI_API_KEY=AIzaSy...
```
*(Catatan: Jika API Key tidak disetel, IGNIS akan otomatis menggunakan Rule-Based Expert System dengan label transparan `[MODE FALLBACK - BUKAN HASIL LLM]` tanpa terjadi error).*

### 4. Menjalankan Test Suite Otomatis
Jalankan pengujian unit dan integrasi untuk memverifikasi seluruh komponen:
```bash
python test_ignis.py
```

### 5. Menjalankan Aplikasi Streamlit
Jalankan server aplikasi web:
```bash
python -m streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser Anda pada alamat: `http://localhost:8501`.

---

## 📂 Struktur Direktori Proyek

```
ignis_system/
├── app.py                      # Main entry point & Streamlit page routing
├── requirements.txt            # Python dependencies
├── .env.example                # Template environment variables
├── test_ignis.py               # Unit & integration automated test suite
├── DOKUMENTASI_AKADEMIK_IGNIS.md # Laporan akademik lengkap & skenario presentasi
├── README.md                   # Panduan instalasi dan penggunaan
├── database/
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection pool, DDL schema, & CRUD methods
├── data/
│   ├── __init__.py
│   ├── generate_simulation_data.py # Seeder dataset simulasi karhutla berbobot
│   └── dataset_simulasi_karhutla.csv # Backup CSV 117 kasus simulasi
├── modules/
│   ├── __init__.py
│   ├── preprocessing.py        # Pembersihan teks & validasi bounding box Indonesia
│   ├── verifier.py             # Haversine spatial-temporal cluster & consistency audit
│   ├── scoring.py              # Explainable AI multi-criteria risk scoring engine
│   ├── rca.py                  # Dynamic 5 Whys Root Cause Analysis engine
│   ├── fishbone.py             # Plotly Ishikawa fishbone diagram visualizer
│   ├── llm_service.py          # Gemini 2.5 Flash client + Local Expert System fallback
│   ├── ai_evaluation.py        # Framework pengujian 3 skenario kegagalan model AI
│   └── geo_map.py              # Folium HeatMap & interactive marker maps
└── views/
    ├── __init__.py
    ├── dashboard_view.py       # Menu 1: Dashboard metrik & grafik
    ├── lapor_view.py           # Menu 2: Form pelaporan masyarakat
    ├── peta_view.py            # Menu 3: Peta geospasial Folium
    ├── verifikasi_view.py      # Menu 4: Verifikasi sistem vs petugas
    ├── scoring_view.py         # Menu 5: Evaluasi Explainable AI (XAI)
    ├── rca_fishbone_view.py    # Menu 6: Investigasi 5 Whys & diagram tulang ikan
    ├── chatbot_view.py         # Menu 7: Asisten cerdas grounded AI
    ├── mitigasi_view.py        # Menu 8: Rencana rekomendasi mitigasi
    ├── evaluasi_ai_view.py     # Menu 9: Evaluasi 3 kegagalan AI
    └── dataset_view.py         # Menu 10: Manajemen dataset & upload CSV
```

---

## 🎓 Skenario Demonstrasi Singkat untuk Dosen

1. **Dashboard (Menu 1):** Tunjukkan 117 data laporan simulasi yang terdistribusi di hotspot Indonesia (Riau, Sumsel, Kalbar, Kalteng, Bromo Jatim).
2. **Pelaporan Masyarakat (Menu 2):** Pilih preset *Riau - Bengkalis*, input laporan baru, dan buktikan sistem langsung menghitung AI Risk Score serta memvalidasi klaster.
3. **Peta Interaktif (Menu 3):** Tampilkan peta Folium HeatMap dan klik pin merah prioritas Kritis.
4. **Explainable AI (Menu 5):** Perlihatkan formula matematis transparan dan perbandingan hasil sebelum vs sesudah analisis AI.
5. **Analisis Kausalitas (Menu 6):** Tunjukkan tahapan 5 Whys dan diagram Fishbone interaktif dengan perbedaan warna hijau (terverifikasi) vs oranye (dugaan).
6. **Evaluasi AI (Menu 9):** Uji skenario kegagalan *Hallucination* atau *Under-reporting* dan perlihatkan efektivitas guardrail sistem.
7. **Chatbot & Rekomendasi (Menu 7 & 8):** Ajukan pertanyaan seputar SOP Karhutla dan perlihatkan rekomendasi mitigasi resmi multi-instansi.

---
*Dikembangkan dengan dedikasi rekayasa AI oleh DeepMind Pair Engineering Assistant untuk keunggulan solusi mitigasi bencana lingkungan di Indonesia.*
