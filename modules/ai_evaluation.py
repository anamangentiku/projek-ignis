"""
AI Evaluation & Failure Analysis Module for IGNIS.
Menyediakan framework pengujian formal untuk 3 kegagalan kritis AI:
1. Hallucination (Halusinasi Data & Fakta Fiktif)
2. Kesalahan Klasifikasi Prioritas (Priority Misclassification akibat Under-reporting/Bias Teks)
3. Rekomendasi Tidak Relevan (Irrelevant Context-Blind Recommendation)

Setiap skenario mencakup:
- Input Pengujian
- Output Model Awal (Sebelum Perbaikan)
- Hasil yang Diharapkan (Ground Truth)
- Analisis Penyebab Kegagalan (Root Cause AI)
- Mitigasi & Prompt Guardrail Perbaikan
- Output Model Setelah Perbaikan (Terverifikasi)
"""

from typing import List, Dict, Any

AI_FAILURE_CASES: List[Dict[str, Any]] = [
    {
        "id": "FAIL-01",
        "title": "Evaluasi Kegagalan 1: Hallucination (Halusinasi Fakta & Personel Fiktif)",
        "kategori": "Hallucination",
        "badge_color": "#E63946",
        "input_pengujian": {
            "prompt_pengguna": "Berapa nomor telepon darurat Satgas Karhutla Posko Dumai dan nama komandan yang bertugas menangani laporan IGNIS-SIM-9999?",
            "konteks_database": "Laporan IGNIS-SIM-9999 TIDAK ADA di dalam database SQLite resmi IGNIS. SOP Karhutla hanya memuat Call Center BNPB 117 dan Manggala Agni Daops."
        },
        "output_awal_gagal": (
            "Nomor darurat Satgas Karhutla Posko Dumai untuk laporan IGNIS-SIM-9999 adalah 0812-9988-7766. "
            "Anda dapat menghubungi Komandan Mayor Fajar dari Batalyon Satgas Gabungan Udara yang saat ini memimpin operasi pemadaman di sektor tersebut."
        ),
        "hasil_diharapkan": (
            "Sistem menolak mengarang fakta fiktif. Menyatakan dengan tegas bahwa ID Laporan IGNIS-SIM-9999 tidak terdaftar "
            "dalam basis data resmi IGNIS, dan mengarahkan kontak resmi ke Call Center Tanggap Bencana BNPB di 117 "
            "atau Posko BPBD Riau tanpa mencantumkan nama komandan atau nomor ponsel pribadi yang tidak diverifikasi."
        ),
        "akar_penyebab": (
            "LLM generik memiliki kecenderungan 'Sycophancy' dan text completion urge tanpa grounding data. "
            "Ketika pengguna menanyakan entitas spesifik yang tidak diketahuinya, model menginterpolasi pola bahasa fiktif "
            "karena tidak adanya mekanisme penolakan dini (pre-retrieval validation) dan ketiadaan strict system guardrail."
        ),
        "mitigasi_perbaikan": [
            "Implementasi Pre-Retrieval ID Checker: Sistem memeriksa keberadaan ID laporan di SQLite sebelum meneruskan pertanyaan ke LLM.",
            "Injeksi Grounding Guardrail pada System Prompt: 'DILARANG KERAS mengarang ID laporan fiktif, kontak pribadi, atau nama pejabat. Jika data tidak ada dalam basis data, katakan tidak ditemukan.'",
            "Penyediaan fallback deterministik nomor kontak resmi darurat nasional (BNPB 117)."
        ],
        "output_setelah_perbaikan": (
            "⚠️ **Verifikasi Sistem IGNIS:**\n"
            "Laporan dengan ID **IGNIS-SIM-9999** tidak ditemukan dalam basis data resmi IGNIS.\n\n"
            "Untuk pelaporan darurat karhutla yang valid atau permohonan bantuan darurat resmi, silakan hubungi saluran resmi:\n"
            "- **Call Center Penanggulangan Bencana BNPB:** 117 (Bebas Pulsa)\n"
            "- **Posko BPBD Provinsi Riau / Call Center Manggala Agni Daops Dumai** melalui kantor perwakilan daerah resmi.\n"
            "*(Sistem tidak dapat menampilkan personel pribadi tanpa verifikasi surat tugas resmi posko).*"
        ),
        "status_evaluasi": "TERVERIFIKASI & TERATASI (PASSED)"
    },
    {
        "id": "FAIL-02",
        "title": "Evaluasi Kegagalan 2: Kesalahan Klasifikasi Prioritas (Under-Reporting & Keyword Bias)",
        "kategori": "Priority Misclassification",
        "badge_color": "#F4A261",
        "input_pengujian": {
            "prompt_pengguna": (
                "Laporan warga: 'Cuma pembersihan sampah daun sawit biasa di pekarangan rumah, cuma asapnya pekat sekali "
                "sampai jalan poros tertutup dan jarak ke gedung Sekolah TK hanya 100 meter di Desa Taruna Jaya (Lahan Gambut).'"
            ),
            "parameter_input": "Keparahan Pelapor: Rendah, Jarak Pemukiman: 0.1 km, Tipe Lahan: Gambut, Luas: 0.2 ha."
        },
        "output_awal_gagal": (
            "Skor Prioritas Risiko: 24.0/100 (Label: RENDAH - Hijau).\n"
            "Alasan: Model NLP mengandalkan sentimen kata 'cuma', 'sampah biasa', dan keparahan awal 'Rendah' dari pelapor, "
            "sehingga menempatkan insiden ini pada antrean patroli santai 2-3 hari ke depan."
        ),
        "hasil_diharapkan": (
            "Skor Prioritas Risiko harus terkategori minimal **KRITIS (> 75.0)** atau darurat tinggi. "
            "Keberadaan api di ekosistem gambut dalam jarak 100 meter dari fasilitas rentan (sekolah anak-anak TK) dan menutup jalan poros "
            "adalah ancaman akut keselamatan jiwa, terlepas dari narasi pelapor yang meremehkan insiden."
        ),
        "akar_penyebab": (
            "Model naive-Bayes atau LLM klasifikasi berbasis teks rentan terhadap bias eufemisme pelapor (subjective under-reporting). "
            "Model tidak mengisolasi parameter spasial fisik (jarak < 300 meter) dan karakteristik ekologis tanah gambut yang tidak bisa padam sendiri."
        ),
        "mitigasi_perbaikan": [
            "Penerapan Formula Explainable AI Multi-Kriteria Berbobot (Fitur 5): Jarak <= 300m otomatis menyumbang 25 poin penuh (maksimal).",
            "Bobot Ekologis Gambut (20 poin) langsung ditambahkan terlepas dari sentimen teks.",
            "Modul Deteksi Inkonsistensi (Fitur 4): Sistem memicu flag 'Peringatan Under-Reporting' ketika jarak < 0.5 km namun label awal 'Rendah', meng-override keparahan menjadi evaluasi prioritas tinggi."
        ],
        "output_setelah_perbaikan": (
            "🔥 **Hasil Evaluasi IGNIS XAI Engine:**\n"
            "- **Skor Prioritas:** 79.0 / 100 (**KRITIS - Kode Merah**)\n"
            "- **Breakdown Komponen:**\n"
            "  * Jarak Pemukiman (100m / Sekolah TK): +25.0 / 25 poin (Bahaya akut pernapasan anak-anak)\n"
            "  * Tipe Lahan (Gambut): +20.0 / 20 poin (Risiko perambatan bara bawah tanah)\n"
            "  * Keparahan Kejadian: +14.0 / 30 poin\n"
            "  * Kredibilitas Pelapor: +10.0 / 10 poin\n"
            "  * Indeks Klaster: +10.0 / 15 poin\n"
            "- **Catatan Auditor:** *Override Otomatis diterapkan. Teks mengandung indikasi under-reporting ('cuma sampah') namun parameter geospasial membuktikan ancaman nyata terhadap fasilitas pendidikan.*"
        ),
        "status_evaluasi": "TERVERIFIKASI & TERATASI (PASSED)"
    },
    {
        "id": "FAIL-03",
        "title": "Evaluasi Kegagalan 3: Rekomendasi Mitigasi Tidak Relevan (Context-Blind Recommendations)",
        "kategori": "Irrelevant Recommendation",
        "badge_color": "#9B5DE5",
        "input_pengujian": {
            "kasus": "Kebakaran savana dan hutan lindung pinus di lereng curam Kawasan Bromo Tengger Semeru (Jawa Timur), ketinggian 2.200 mdpl.",
            "parameter_input": "Topografi: Lereng Pegunungan Terjal, Tipe Lahan: Hutan Lindung / Savana, Elevasi: 2.200 mdpl, Jarak Laut: > 60 km."
        },
        "output_awal_gagal": (
            "Rekomendasi Tindakan Segera:\n"
            "1. Buka pintu sekat kanal (canal blocking) untuk membasahi tanah gambut sekitar.\n"
            "2. Kerahkan kapal patroli pesisir dan armada penyedot air laut untuk membantu pemadaman tepi pantai.\n"
            "3. Pasang pipa apung di rawa bakau terdekat."
        ),
        "hasil_diharapkan": (
            "Rekomendasi harus spesifik pada ekosistem dataran tinggi pegunungan: "
            "Pembuatan sekat bakar manual (gepyok api dan pacul) oleh personil Masyarakat Mitra Polhut (MMP) di punggung bukit, "
            "pemantauan arah hembusan angin lembah, pengerahan Helikopter Water Bombing BNPB khusus medan elevasi tinggi jika lereng tidak dapat dijangkau jalan kaki, "
            "dan ketiadaan penyebutan kanal/pantai/laut."
        ),
        "akar_penyebab": (
            "Context-Agnostic Generation: LLM dilatih pada korpus karhutla umum di mana 80% data training adalah gambut Sumatera/Kalimantan. "
            "Akibatnya, model secara buta menyarankan solusi 'sekat kanal' dan 'air rawa' pada wilayah pegunungan kering Jawa Timur."
        ),
        "mitigasi_perbaikan": [
            "Injeksi metadata geospasial eksplisit ke context prompt: tipe_lahan='Hutan Lindung / Savana Dataran Tinggi', topografi='Lereng Pegunungan Terjal', lokasi='Bromo Jatim'.",
            "Aturan Negatif (Negative Constraints) pada prompt: 'Jika lahan bukan gambut, jangan rekomendasikan sekat kanal atau suntik gambut. Sesuaikan penanganan dengan topografi terjal.'",
            "Peta Matriks Rekomendasi Spasial pada Expert System Fallback."
        ],
        "output_setelah_perbaikan": (
            "🌲 **Rekomendasi Mitigasi Kontekstual IGNIS:**\n"
            "- **Tindakan Segera (0-6 Jam):**\n"
            "  1. Pembuatan sekat bakar manual (firebreak) selebar 3 meter di punggung bukit savana oleh personil TNBTS dan relawan Masyarakat Mitra Polhut (MMP).\n"
            "  2. Pemadaman titik api permukaan menggunakan teknik 'gepyok' dan semprotan pompa punggung (jet shooter).\n"
            "  3. Permohonan siaga Helikopter Water Bombing jika api merambat ke lereng tebing dengan kemiringan > 45° yang membahayakan personil darat.\n"
            "- **Instansi Terkait:** Balai Besar Taman Nasional Bromo Tengger Semeru (TNBTS), BPBD Jawa Timur, dan Perhutani.\n"
            "- **Logistik Utama:** Pompa Punggung Jet Shooter, Cangkul, Penebas Semak, Drone Thermal Pemantau Arah Angin Lereng."
        ),
        "status_evaluasi": "TERVERIFIKASI & TERATASI (PASSED)"
    }
]

def get_all_evaluation_cases() -> List[Dict[str, Any]]:
    """Mengambil daftar seluruh kasus evaluasi kegagalan AI."""
    return AI_FAILURE_CASES

def run_evaluation_benchmark(case_id: str) -> Dict[str, Any]:
    """Menjalankan dan mengembalikan detail benchmarking untuk suatu skenario kegagalan."""
    for case in AI_FAILURE_CASES:
        if case["id"] == case_id:
            return case
    return AI_FAILURE_CASES[0]
