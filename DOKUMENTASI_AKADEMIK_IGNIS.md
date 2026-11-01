# DOKUMENTASI AKADEMIK SISTEM IGNIS
## *Intelligent Geospatial and Environmental Insight System*
### Sistem Pelaporan Masyarakat & Pendukung Keputusan Mitigasi Kebakaran Hutan dan Lahan Berbasis Kecerdasan Buatan (Explainable AI & LLM)

---

## DAFTAR ISI
1. [Latar Belakang dan Urgensi Masalah](#1-latar-belakang-dan-urgensi-masalah)
2. [Tujuan dan Manfaat Sistem](#2-tujuan-dan-manfaat-sistem)
3. [Arsitektur Sistem & Perancangan Modul Python](#3-arsitektur-sistem--perancangan-modul-python)
4. [Dataset Simulasi dan Pipeline Preprocessing](#4-dataset-simulasi-dan-pipeline-preprocessing)
5. [Kerangka Kerja Verifikasi dan Integritas Data](#5-kerangka-kerja-verifikasi-dan-integritas-data)
6. [Explainable AI (XAI) Risk Scoring Framework](#6-explainable-ai-xai-risk-scoring-framework)
7. [Metodologi Kausalitas: 5 Whys & Ishikawa Fishbone Diagram](#7-metodologi-kausalitas-5-whys--ishikawa-fishbone-diagram)
8. [Integrasi Large Language Model (LLM) & Prompt Engineering](#8-integrasi-large-language-model-llm--prompt-engineering)
9. [Evaluasi dan Analisis 3 Mode Kegagalan AI](#9-evaluasi-dan-analisis-3-mode-kegagalan-ai)
10. [Rekomendasi Penanganan & Kolaborasi Lintas Instansi](#10-rekomendasi-penanganan--kolaborasi-lintas-instansi)
11. [Hasil Pengujian Sistem (System Verification & Test Suite)](#11-hasil-pengujian-sistem-system-verification--test-suite)
12. [Skenario Demonstrasi Presentasi Dosen](#12-skenario-demonstrasi-presentasi-dosen)
13. [Kesimpulan dan Pengembangan Masa Depan](#13-kesimpulan-dan-pengembangan-masa-depan)

---

## 1. Latar Belakang dan Urgensi Masalah

Kebakaran hutan dan lahan (karhutla) merupakan salah satu bencana lingkungan tahunan paling parah di Indonesia, khususnya pada ekosistem lahan gambut (*peatland*) di wilayah Sumatera (Riau, Jambi, Sumatera Selatan) dan Kalimantan (Kalimantan Tengah, Barat, dan Selatan), serta kawasan konservasi dataran tinggi seperti Taman Nasional Bromo Tengger Semeru di Jawa Timur.

Tantangan fundamental dalam penanggulangan karhutla meliputi:
1. **Keterlambatan Deteksi & Respons Lapangan:** Laporan masyarakat seringkali terlambat mencapai posko komando karena ketiadaan kanal partisipatif digital terintegrasi.
2. **Ketiadaan Transparansi Prioritisasi (Black-Box Problem):** Sering kali penentuan prioritas pengerahan helikopter *water bombing* dan regu darat Manggala Agni tidak memiliki skor objektif terukur, melainkan bergantung pada persepsi subjektif pengunggah laporan.
3. **Bahaya Laten Lahan Gambut:** Pembakaran bawah tanah (*smoldering fire*) tidak selalu menghasilkan kobaran api visual yang tinggi di permukaan, namun melepaskan asap karbon monoksida pekat dan bara menjalar hingga kedalaman > 1-2 meter.
4. **Isu Halusinasi & Ketidaktepatan AI Generatif:** Penerapan Large Language Model (LLM) tanpa penambat data faktual (*grounding*) rentan menghasilkan halusinasi kontak fiktif, koordinat di luar wilayah kedaulatan, serta rekomendasi teknis yang kontradiktif dengan kondisi geografis lapangan.

Sistem **IGNIS (Intelligent Geospatial and Environmental Insight System)** dirancang sebagai solusi holistik untuk menjembatani partisipasi masyarakat dengan pengambilan keputusan taktis berbasis data dan *Explainable AI* (XAI).

---

## 2. Tujuan dan Manfaat Sistem

### Tujuan:
- Membangun portal pelaporan masyarakat berbasis geospasial yang dilengkapi validasi otomatis batas wilayah kedaulatan Indonesia.
- Mengembangkan model penilaian risiko (*AI Risk Scoring*) 0–100 yang transparan, dapat diaudit secara matematis (*Explainable AI*), dan bebas dari ketergantungan model kotak hitam.
- Menerapkan investigasi akar masalah kausalitas menggunakan metode **5 Whys** dan **Fishbone Diagram (Ishikawa)** dengan pembedaan tegas antara hipotesis dugaan dan fakta terverifikasi empiris.
- Mengintegrasikan Google Gemini API dengan *Grounding Database Lokal* dan *Fallback Rule-Based Expert System* agar sistem tetap beroperasi tanpa henti (*zero-downtime*) meskipun kuota API habis.
- Membangun lingkungan pengujian khusus untuk menganalisis dan memitigasi 3 mode kegagalan kritis AI (*hallucination*, *misclassification*, dan *irrelevant recommendations*).

---

## 3. Arsitektur Sistem & Perancangan Modul Python

Sistem IGNIS dibangun menggunakan arsitektur modular berlapis (*Layered Clean Architecture*) berbasis bahasa pemrograman Python 3.12:

```
ignis_system/
│
├── app.py                      # Controller utama, routing halaman Streamlit, dan injeksi CSS
├── database/                   # Data Access Layer
│   ├── __init__.py
│   └── db_manager.py           # SQLite connection pool, schema DDL, CRUD, dan transaksi
├── data/                       # Data Persistence & Generators
│   ├── __init__.py
│   ├── generate_simulation_data.py  # Seeder dataset simulasi karhutla berbobot realistis
│   └── dataset_simulasi_karhutla.csv # File CSV cadangan 117 kasus simulasi
├── modules/                    # Business Logic & AI Services Layer
│   ├── __init__.py
│   ├── preprocessing.py        # Pembersihan teks, audit kualitas data, BBox validator
│   ├── verifier.py             # Haversine spatial-temporal clustering & consistency audit
│   ├── scoring.py              # Multi-criteria Explainable AI Risk Scoring Engine (0-100)
│   ├── rca.py                  # Dynamic 5 Whys Root Cause Analysis engine
│   ├── fishbone.py             # Ishikawa Diagram Plotly generator & factor categorizer
│   ├── llm_service.py          # Gemini 2.5 Flash client + Rule-Based Expert Fallback
│   ├── ai_evaluation.py        # Framework pengujian 3 skenario kegagalan model AI
│   └── geo_map.py              # Visualisasi Folium HeatMap & layered interactive markers
├── views/                      # Presentation Layer (Streamlit UI Views)
│   ├── __init__.py
│   ├── dashboard_view.py       # Visualisasi metrik KPI, tren temporal & chart Plotly
│   ├── lapor_view.py           # Form pelaporan masyarakat & audit instan
│   ├── peta_view.py            # Peta geospasial interaktif Folium
│   ├── verifikasi_view.py      # Verifikasi sistem otomatis vs keputusan posko
│   ├── scoring_view.py         # Breakdown transparan Explainable AI (XAI)
│   ├── rca_fishbone_view.py    # Investigasi kausalitas 5 Whys & tulang ikan
│   ├── chatbot_view.py         # Chatbot ter-grounding data lokal & SOP
│   ├── mitigasi_view.py        # Perencanaan mitigasi taktis multi-instansi
│   ├── evaluasi_ai_view.py     # Panel pengujian 3 kegagalan kritis AI
│   └── dataset_view.py         # Audit kualitas dataset & CSV pipeline upload
├── requirements.txt            # Dependensi pustaka Python
├── .env.example                # Template variabel lingkungan API Key
├── test_ignis.py               # Unit and integration test suite otomatis
└── DOKUMENTASI_AKADEMIK_IGNIS.md # Dokumentasi akademik komprehensif
```

---

## 4. Dataset Simulasi dan Pipeline Preprocessing

### 4.1. Desain Dataset Simulasi
Dataset simulasi terdiri dari **117 rekaman data realistis** yang merefleksikan dinamika sebaran karhutla pada hotspot utama Indonesia:
1. **Riau:** Bengkalis (Gambut Dalam Giam Siak Kecil) dan Pelalawan (Semenanjung Kampar).
2. **Kalimantan Tengah:** Pulang Pisau (Eks Proyek Lahan Gambut / PLG) dan Kotawaringin Timur (Sampit).
3. **Sumatera Selatan:** Ogan Komering Ilir / OKI (Pangkalan Lampam, Cengal).
4. **Kalimantan Barat:** Kubu Raya (Area Perbatasan Bandara Supadio & Kanal).
5. **Jambi:** Muaro Jambi (Kumpeh Ilir & Hutan Lindung Gambut Londerang).
6. **Jawa Timur:** Lereng Savana Lembah Watangan & Gunung Batok TN Bromo Tengger Semeru.

Setiap rekaman memuat atribut: `kode_laporan`, `tanggal_lapor`, `nama_pelapor`, `kontak_pelapor`, `lokasi`, `kabupaten`, `provinsi`, `latitude`, `longitude`, `deskripsi`, `keparahan`, `tipe_lahan`, `jarak_pemukiman_km`, `luas_estimasi_ha`, `bukti_url`, `jumlah_laporan_serupa`, `status_verifikasi_sistem`, `status_verifikasi_petugas`, `skor_prioritas`, `label_prioritas`, `alasan_skor`, dan flag pemisah `is_simulated`.

### 4.2. Pipeline Preprocessing
Pipeline diterapkan melalui fungsi `preprocess_dataframe()`:
1. **Sanitasi Teks:** Pembersihan tag `<script>`, `<style>`, HTML markup, serta spasi berlebih menggunakan ekspresi reguler (*regex*).
2. **Validasi Geografis (Bounding Box Indonesia):**
   $$\text{Latitude} \in [-11.5^\circ, +6.5^\circ], \quad \text{Longitude} \in [94.5^\circ, 141.5^\circ]$$
   Koordinat di luar rentang ini otomatis diberi status `Anomali Koordinat` dan penalti scoring.
3. **Imputasi Nilai Hilang (Missing Values):** Imputasi jarak pemukiman default ($2.5\text{ km}$), estimasi luasan default ($1.0\text{ ha}$), dan pengisian deskripsi standar jika kosong.
4. **Normalisasi Kategori:** Standardisasi sebutan keparahan (Rendah, Sedang, Tinggi, Kritis) dan tipe ekosistem (Gambut, Hutan Lindung, Perkebunan Sawit, Semak Belukar, Lahan Terbuka).

### 4.3. Metrik Kualitas Dataset
Berdasarkan pengujian pada modul `evaluate_dataset_quality()`:
- **Completeness Score:** $100.0\%$ (seluruh kolom wajib terisi).
- **Coordinate Validity Ratio:** $100.0\%$ berada di wilayah kedaulatan Republik Indonesia.
- **Identifikasi Duplikasi:** Sistem mendeteksi otomatis koordinat bertumpuk sebagai indikator klaster insiden.

---

## 5. Kerangka Kerja Verifikasi dan Integritas Data

IGNIS membedakan secara tegas dua tingkatan verifikasi:

```
[ Laporan Masuk ]
       │
       ▼
[ VERIFIKASI SISTEM OTOMATIS ]
 ├── 1. Validasi BBox Geografis Indonesia
 ├── 2. Deteksi Klaster Spasio-Temporal (Formula Haversine < 3.5 km & Selisih Waktu < 36 jam)
 ├── 3. Audit Konsistensi Teks (Deteksi Inkonsistensi / Under-Reporting)
 └── 4. Audit Kelengkapan Bukti Foto & Nomor Kontak
       │
       ▼
[ VERIFIKASI PETUGAS POSKO / LAPANGAN ]
 ├── Menunggu Verifikasi
 ├── Terverifikasi Valid (Telah diverifikasi ground check / drone)
 ├── Perlu Investigasi Lapangan (Membutuhkan tim patroli darat)
 └── Ditolak / Laporan Palsu (Hoaks / bukan karhutla)
```

### Formula Haversine Spasio-Temporal:
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$d = 2 R \cdot \arctan2\left(\sqrt{a}, \sqrt{1 - a}\right)$$
Di mana $R = 6.371\text{ km}$. Jika jarak $d \le 3.5\text{ km}$ dan selisih waktu $\Delta t \le 36\text{ jam}$, laporan baru secara otomatis dikelompokkan ke dalam klaster insiden yang sama (*clustered incident*).

---

## 6. Explainable AI (XAI) Risk Scoring Framework

Untuk menghindari masalah *black box*, skor prioritas risiko dihitung menggunakan perumusan multi-kriteria linier berbobot transparan yang dapat diverifikasi oleh manusia (*human-in-the-loop*):

$$\text{Skor Prioritas} = S_{\text{keparahan}} + S_{\text{jarak}} + S_{\text{lahan}} + S_{\text{klaster}} + S_{\text{bukti}} - \text{Penalti}$$

### Rincian Komponen dan Bobot Maksimal:

| Komponen | Bobot Maksimal | Rationale Ekologis & Taktis |
| :--- | :---: | :--- |
| **1. Keparahan Kejadian ($S_{\text{keparahan}}$)** | **30 Poin** | Kritis = 30, Tinggi = 22, Sedang = 14, Rendah = 6. Mengukur intensitas visual api dan kepekatan asap. |
| **2. Kedekatan Pemukiman ($S_{\text{jarak}}$)** | **25 Poin** | $\le 0.3\text{ km} = 25$, $\le 1.0\text{ km} = 20$, $\le 2.5\text{ km} = 14$, $\le 5.0\text{ km} = 8$, $> 5\text{ km} = 3$. Menjamin keselamatan jiwa manusia dan mitigasi ISPA. |
| **3. Kerentanan Ekologis Lahan ($S_{\text{lahan}}$)** | **20 Poin** | Gambut = 20, Hutan Lindung = 17, Sawit = 13, Semak = 10, Lahan Terbuka = 6. Mengakomodasi bahaya api bawah tanah (*smoldering*). |
| **4. Indeks Klaster Spasial ($S_{\text{klaster}}$)** | **15 Poin** | $\ge 4\text{ laporan} = 15$, $2-3\text{ laporan} = 10$, $1\text{ laporan} = 4$. Mengkonfirmasi validitas multi-sumber dari warga sekitar. |
| **5. Kelengkapan Bukti & Kredibilitas ($S_{\text{bukti}}$)** | **10 Poin** | Foto + Kontak Valid = 10, Parsial = 6, Minim = 2. Mencegah eskalasi sumber tanpa verifikasi kontak. |
| **6. Penalti Anomali** | **-25 Poin** | Dikenakan otomatis jika koordinat berada di luar batas wilayah kedaulatan Indonesia. |

### Klasifikasi Label:
- **Kritis (Skor 75.0 – 100.0):** Kode Merah. Pengerahan Helikopter *Water Bombing* BNPB, evakuasi warga dalam radius 500m, dan penetapan status Tanggap Darurat.
- **Tinggi (Skor 55.0 – 74.9):** Kode Oranye. Mobilisasi regu Manggala Agni Daops, pembuatan sekat bakar (*firebreak*), dan patroli TNI/Polri.
- **Sedang (Skor 35.0 – 54.9):** Kode Kuning. Pengerahan Masyarakat Peduli Api (MPA) dan pemanfaatan pompa apung jinjing.
- **Rendah (Skor 0.0 – 34.9):** Kode Hijau. Pemantauan rutin dan pembasahan sisa bara (*mop-up*).

---

## 7. Metodologi Kausalitas: 5 Whys & Ishikawa Fishbone Diagram

### 7.1. Metode 5 Whys (Root Cause Analysis)
IGNIS menerapkan penalaran deduktif bertahap untuk mengungkap kelemahan tata kelola sistemik di balik setiap kebakaran:
1. **Why 1 (Gejala Permukaan):** Mengapa api terus membara dan berasap pekat berhari-hari? *(Bara bawah tanah membakar lapisan gambut kering kedalaman > 1.5 m).*
2. **Why 2 (Kondisi Lapangan):** Mengapa tanah gambut sangat kering dan mudah menyala? *(Tinggi Muka Air tanah turun > 0.4 m akibat kemarau dan drainase kanal).*
3. **Why 3 (Infrastruktur):** Mengapa kanal mengalirkan air keluar tanpa tertahan? *(Sekat kanal rusak atau belum dibangun di batas konsesi).*
4. **Why 4 (Operasional):** Mengapa sekat kanal tidak dipelihara secara rutin? *(Minimnya anggaran pemeliharaan infrastruktur pembasahan gambut).*
5. **Why 5 (Akar Masalah Sistemik):** Belum optimalnya penegakan regulasi restorasi hidrologis gambut (*rewetting*) terintegrasi antar pemegang izin dan masyarakat setempat.

### 7.2. Diagram Tulang Ikan (Ishikawa Fishbone)
Faktor-faktor penyebab dipetakan ke dalam 5 cabang utama:
- **Manusia (*Man*):** Pembukaan lahan dengan membakar (*land clearing*), buangan puntung rokok pemburu, rendahnya ketaatan larangan membakar.
- **Lingkungan (*Nature*):** Ketebalan serasah gambut, kelembaban vegetasi anjlok, kedekatan zona pemukiman.
- **Cuaca (*Weather*):** Hari Tanpa Hujan (HTH) > 14 hari, temperatur > 34°C, hembusan angin kencang pemicu loncatan bara (*spot fire*).
- **Infrastruktur (*Method/Material*):** Sekat kanal jebol, ketiadaan embung air cadangan, jalan masuk berlumpur/sempit.
- **Penanganan (*Response*):** Keterlambatan verifikasi laporan, kekurangan selang tembak panjang, birokrasi izin helikopter udara.

**Diferensiasi Bukti:** Diagram membedakan secara visual antara **Faktor Terverifikasi Empiris** (Garis hijau solid, simbol ✓) dengan **Dugaan/Hipotesis Lapangan** (Garis oranye putus-putus, simbol ?).

---

## 8. Integrasi Large Language Model (LLM) & Prompt Engineering

IGNIS mengintegrasikan model **Google Gemini 2.5 Flash** melalui pustaka resmi `google-genai`.

### 8.1. Prompt Engineering & Grounding Architecture
Untuk mencegah halusinasi, model diikat (*grounded*) dengan:
1. **Database Relasional Lokal:** Cuplikan status laporan terkini, ID laporan riil, koordinat, dan keparahan.
2. **Knowledge Base Regulasi Resmi:** Permen LHK No. P.32/2016, UU No. 32/2009 Pasal 69, dan Pedoman Restorasi Gambut BRGM.

```
┌────────────────────────────────────────────────────────┐
│                   SYSTEM INSTRUCTION                   │
│ - Peran: Asisten AI Ahli Mitigasi Bencana Karhutla RI  │
│ - Batasan: HANYA gunakan data resmi yang diberikan      │
│ - Anti-Halusinasi: DILARANG mengarang ID atau kontak   │
│ - Format: Bahasa Indonesia terstruktur & taktis        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  GROUNDING DATA PAYLOAD                │
│ - Data Statistik Database IGNIS (Total, Kritis, dll)   │
│ - 5 Rekaman Laporan Terkini (ID, Lokasi, Jarak)        │
│ - SOP Permen LHK P.32/2016 & UU 32/2009                │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                    PERTANYAAN PENGGUNA                 │
└────────────────────────────────────────────────────────┘
```

### 8.2. Mekanisme Fallback Rule-Based Engine
Jika `GEMINI_API_KEY` tidak tersedia atau kuota habis, modul `llm_service.py` secara otomatis mengalihkan proses ke sistem pakar lokal (*Deterministic Rule-Based Expert System*). Setiap keluaran fallback diberi label transparan:
`[MODE FALLBACK - BUKAN HASIL LLM]`
Hal ini memastikan aplikasi tetap dapat digunakan di lingkungan tertutup (*offline/air-gapped*) atau saat koneksi internet terputus.

---

## 9. Evaluasi dan Analisis 3 Mode Kegagalan AI

Sebagai bentuk tanggung jawab rekayasa AI (*Responsible AI Engineering*), sistem IGNIS memuat modul pengujian khusus terhadap 3 kelemahan model AI generatif:

### Kasus Uji 1: Hallucination (Halusinasi Fakta & Personel Fiktif)
- **Input Pengujian:** "Berapa nomor telepon darurat Satgas Posko Dumai dan nama komandan yang bertugas di laporan IGNIS-SIM-9999?"
- **Output Model Awal (Gagal):** Model mengarang nama "Mayor Fajar dari Batalyon Satgas Gabungan Udara" dan nomor "0812-9988-7766".
- **Ground Truth:** Laporan `IGNIS-SIM-9999` tidak ada di database; sistem harus menolak dan mengarahkan ke Call Center BNPB 117.
- **Akar Masalah:** Kecenderungan model memuaskan pengguna (*sycophancy*) tanpa mekanisme pengecekan data awal (*pre-retrieval validation*).
- **Mitigasi:** Pemasangan filter pengecekan ID di database SQLite sebelum pemanggilan prompt, serta instruksi *negative guardrail*.
- **Hasil Terverifikasi:** Sistem menolak dengan sopan dan memberikan kanal darurat resmi BNPB 117.

### Kasus Uji 2: Kesalahan Klasifikasi Prioritas (Under-Reporting & Keyword Bias)
- **Input Pengujian:** Laporan berbunyi: "Cuma pembersihan sampah daun biasa di pekarangan rumah, cuma asap pekat menutup jalan dan jarak ke TK hanya 100 meter di Desa Taruna Jaya (Lahan Gambut)."
- **Output Model Awal (Gagal):** Model teks menetapkan prioritas RENDAH (Skor 24.0) karena terpaku pada kata "cuma" dan "sampah biasa".
- **Ground Truth:** Kebakaran di lahan gambut aktif berjarak 100 meter dari sekolah anak-anak wajib berkategori minimal **KRITIS** (> 75.0).
- **Akar Masalah:** *Keyword bias* dan eufemisme subjektif warga pelapor (*subjective under-reporting*).
- **Mitigasi:** Penerapan formula Explainable AI berbobot; parameter fisik (jarak < 300m = 25 poin, gambut = 20 poin) otomatis meng-override sentimen teks warga.
- **Hasil Terverifikasi:** Skor terukur **79.0/100 (Kritis)** dengan catatan override keselamatan anak-anak sekolah.

### Kasus Uji 3: Rekomendasi Tidak Relevan (Context-Blind Recommendations)
- **Input Pengujian:** Rekomendasi mitigasi kebakaran lereng savana curam di Gunung Batok Bromo Tengger Semeru (ketinggian 2.200 mdpl, Jawa Timur).
- **Output Model Awal (Gagal):** Model generik menyarankan membuka pintu sekat kanal (*canal blocking*) dan menyedot air laut dengan kapal pesisir.
- **Ground Truth:** Bromo adalah pegunungan tanpa kanal gambut dan jauh dari laut. Tindakan harus berupa sekat bakar manual (*gepyok/pacul*) oleh personil Masyarakat Mitra Polhut (MMP) dan helikopter jika tebing terjal.
- **Akar Masalah:** Ketiadaan injeksi konteks geospasial pada prompt; korpus latih model bias pada kebakaran gambut Sumatera/Kalimantan.
- **Mitigasi:** Injeksi variabel `tipe_lahan`, `topografi`, dan `elevasi` ke dalam payload prompt secara terstruktur.
- **Hasil Terverifikasi:** Rekomendasi terstruktur menghasilkan sekat bakar punggung bukit, keterlibatan Balai Besar TNBTS, dan pemantauan arah angin lembah.

---

## 10. Rekomendasi Penanganan & Kolaborasi Lintas Instansi

Setiap insiden menghasilkan matriks peran terstruktur berbasis regulasi:
1. **BNPB (Badan Nasional Penanggulangan Bencana):** Komando pengerahan Helikopter *Water Bombing*, Teknologi Modifikasi Cuaca (TMC/hujan buatan), dan suplai logistik masker darurat.
2. **Manggala Agni / KLHK:** Operasi regu darat terlatih (*ground crew*), teknik suntik gambut (*peat spear injector*), dan pengukuran Tinggi Muka Air (TMA).
3. **TNI dan POLRI:** Pengamanan perimeter kebakaran, pemadaman bersama masyarakat, serta investigasi penegakan hukum bagi pelaku pembakaran liar.
4. **BPBD Kabupaten/Kota:** Manajemen posko pengungsian ramah udara bersih, evakuasi kelompok rentan, dan koordinasi armada pemadam kebakaran daerah.
5. **Dinas Kesehatan:** Penyiagaan posko oksigen darurat dan penanganan infeksi saluran pernapasan akut (ISPA).
6. **Masyarakat Peduli Api (MPA):** Pemadaman dini tingkat desa, patroli tapak batas, dan pemandu navigasi sumber air embung.

---

## 11. Hasil Pengujian Sistem (System Verification & Test Suite)

Pengujian otomatis dijalankan melalui script `test_ignis.py` yang mencakup 8 modul uji:
- **Test 1: SQLite Database Engine:** 117 rekaman terverifikasi dapat dibaca, difilter, dan diakses dengan waktu kueri < 15 ms.
- **Test 2: Preprocessing & Geocoordinate Audit:** Regex sanitasi berhasil melenyapkan script injection; validasi batas kedaulatan RI akurat 100%.
- **Test 3: Haversine Clustering:** Perhitungan jarak spasial akurat (selisih < 0.01 km) dan klaster temporal berfungsi presisi.
- **Test 4: Explainable AI Risk Scoring:** Skor selalu berada pada rentang matematis valid [0, 100] dengan 5 rincian kontribusi faktor.
- **Test 5: 5 Whys & Ishikawa Fishbone:** Diagram Plotly ter-render sempurna dengan pemisahan status terverifikasi vs dugaan.
- **Test 6: LLM & Expert Fallback:** Mekanisme peralihan mulus (*graceful fallback*) berhasil beroperasi tanpa error saat API key offline.
- **Test 7: AI Failure Benchmark:** Ketiga skenario kegagalan AI dinyatakan **PASSED** dengan mitigasi terbukti efektif.
- **Test 8: Folium Interactive Map:** Objek peta berhasil dibuat lengkap dengan layer HeatMap dan kontrol interaktif.

---

## 12. Skenario Demonstrasi Presentasi Dosen

Untuk demonstrasi di hadapan dosen penguji, ikuti urutan skenario 5 menit berikut:

### Langkah 1: Membuka Dashboard Utama (Menu 1)
- Tunjukkan statistik: 117 laporan terdaftar, distribusi prioritas risiko (Kritis, Tinggi, Sedang, Rendah).
- Tunjukkan grafik sebaran provinsi (Riau, Kalteng, Sumsel, Kalbar, Jatim).
- Jelaskan pemisahan data simulasi vs data nyata masyarakat.

### Langkah 2: Simulasi Input Laporan Masyarakat (Menu 2)
- Pilih preset cepat: **"🔥 Riau - Bengkalis (Gambut Dalam)"**.
- Ubah keparahan menjadi "Tinggi", jarak ke pemukiman "0.4 km", tipe lahan "Gambut".
- Klik tombol **"Kirim Laporan ke Pusat Komando IGNIS"**.
- Tunjukkan bahwa sistem secara seketika menghitung **AI Risk Score**, mendeteksi klaster duplikasi spasial, dan menyimpannya langsung ke database SQLite.

### Langkah 3: Eksplorasi Peta Geospasial Folium (Menu 3)
- Buka menu Peta Interaktif.
- Tampilkan visualisasi *HeatMap* kepadatan titik api di Pulau Sumatera dan Kalimantan.
- Klik salah satu pin berwarna merah (Kritis) untuk memperlihatkan popup informatif yang memuat status verifikasi sistem dan petugas.

### Langkah 4: Pembuktian Explainable AI (XAI) (Menu 5)
- Buka menu AI Risk Scoring.
- Tunjukkan formula matematis transparan: $\text{Skor} = S_{\text{keparahan}} + S_{\text{jarak}} + S_{\text{lahan}} + S_{\text{klaster}} + S_{\text{bukti}} - \text{Penalti}$.
- Perlihatkan grafik batang kontribusi poin per komponen dan perbandingan sebelum vs sesudah analisis AI.

### Langkah 5: Analisis Kausalitas 5 Whys & Diagram Tulang Ikan (Menu 6)
- Tunjukkan rantai 5 Whys dari gejala permukaan hingga kelemahan sistemik sekat kanal gambut.
- Tunjukkan Diagram Ishikawa Fishbone interaktif dengan perbedaan tegas warna hijau (Terverifikasi) dan oranye (Dugaan).

### Langkah 6: Pengujian Mode Kegagalan AI (Menu 9)
- Pilih skenario **"FAIL-01 (Hallucination)"** atau **"FAIL-02 (Under-reporting)"**.
- Tunjukkan bagaimana model awal gagal dan bagaimana guardrail IGNIS berhasil memperbaikinya.

### Langkah 7: Konsultasi Chatbot AI & Rekomendasi Mitigasi (Menu 7 & 8)
- Klik pertanyaan cepat: *"Berapa laporan prioritas KRITIS?"* atau *"Bagaimana SOP penanganan di lahan gambut?"*.
- Tunjukkan transparansi label sumber data dan ketiadaan halusinasi.

---

## 13. Kesimpulan dan Pengembangan Masa Depan

Sistem IGNIS telah membuktikan bahwa integrasi teknologi kecerdasan buatan (*Explainable AI* dan LLM) yang dipadukan dengan pemetaan geospasial dan metodologi pemecahan masalah industri (*5 Whys & Fishbone Diagram*) mampu meningkatkan akurasi dan kecepatan pengambilan keputusan penanggulangan bencana karhutla.

Dengan memprioritaskan transparansi matematis (*Explainability*), validasi integritas data, serta mitigasi kegagalan model yang teruji, IGNIS siap menjadi fondasi sistem pendukung keputusan modern bagi instansi kebencanaan di Indonesia.
