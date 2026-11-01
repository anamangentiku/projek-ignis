"""
LLM Service & Mitigasi Module for IGNIS.
Mengintegrasikan Google Gemini API dengan Guardrails Anti-Halusinasi,
Grounding Data Laporan Lokal, dan SOP Mitigasi Karhutla (KLHK/BNPB/BMKG).
Dilengkapi Fallback Rule-Based Expert System transparan jika API Key tidak disetel.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env jika ada
load_dotenv()

# Standard SOP Karhutla Nasional (Knowledge Base untuk Grounding)
SOP_KARHUTLA_KNOWLEDGE_BASE = """
REFERENSI RESMI STANDAR OPERASIONAL PROSEDUR (SOP) KARHUTLA INDONESIA:
1. Peraturan Menteri Lingkungan Hidup dan Kehutanan No. P.32/MenLHK/Setjen/Kum.1/3/2016 tentang Pengendalian Kebakaran Hutan dan Lahan.
2. Peraturan Kepala BNPB No. 03 Tahun 2016 tentang Sistem Komando Penanganan Darurat Bencana.
3. Pedoman Pengendalian Kebakaran Lahan Gambut (BRGM - Badan Restorasi Gambut dan Mangrove):
   - Prioritas 1 (Kritis): Kebakaran pada lahan gambut aktif kedalaman > 1m atau jarak < 500m dari pemukiman warga. Mobilisasi Helikopter Water Bombing BNPB, Satgas Udara, dan penetapan status Tanggap Darurat oleh Kepala Daerah.
   - Prioritas 2 (Tinggi): Kebakaran semak belukar / konsesi > 3 hektar dengan potensi rembetan. Pengerahan Regu Manggala Agni Daops, TNI/Polri, pembuatan parit isolasi / sekat bakar (firebreaks).
   - Prioritas 3 (Sedang): Kebakaran vegetasi permukaan kecil. Pengerahan Masyarakat Peduli Api (MPA), Damkar Pemda, dan pemanfaatan pompa apung jinjing serta embung penampungan.
   - Prioritas 4 (Rendah): Pengawasan pasca pemadaman (mop-up), pendinginan bara laten tanah gambut agar tidak menyala kembali (rekurensi).
4. Larangan Tegas UU No. 32 Tahun 2009 Pasal 69 ayat (1) huruf h: Setiap orang dilarang melakukan pembukaan lahan dengan cara membakar.
"""

def get_gemini_client():
    """Menginisialisasi klien Gemini SDK jika API Key tersedia."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None, "API Key belum disetel di file .env atau variabel lingkungan."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Gagal menginisialisasi Google GenAI Client: {str(e)}"

class Tuple_Result:
    def __init__(self, text: str, is_fallback: bool, model_name: str, error_msg: Optional[str] = None):
        self.text = text
        self.is_fallback = is_fallback
        self.model_name = model_name
        self.error_msg = error_msg

def call_gemini_api(prompt: str, system_instruction: str = "") -> Tuple_Result:
    """Memanggil model Gemini dengan penanganan error dan fallback."""
    client, err = get_gemini_client()
    if not client:
        return Tuple_Result(
            text="",
            is_fallback=True,
            model_name="Fallback Rule-Based Engine",
            error_msg=err
        )

    try:
        # Gunakan model Gemini 2.5 Flash yang cepat dan andal
        full_prompt = f"System Instruction:\n{system_instruction}\n\nUser Request:\n{prompt}" if system_instruction else prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return Tuple_Result(
            text=response.text,
            is_fallback=False,
            model_name="Google Gemini 2.5 Flash",
            error_msg=None
        )
    except Exception as e:
        return Tuple_Result(
            text="",
            is_fallback=True,
            model_name="Fallback Rule-Based Engine",
            error_msg=f"Error pemanggilan Gemini API: {str(e)}"
        )

# ==================== FITUR 8: CHATBOT BERBASIS DATA ====================

def answer_chat_query(user_query: str, context_reports_df: Any, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Menjawab pertanyaan pengguna melalui grounding data laporan karhutla yang tersedia
    dan referensi regulasi SOP resmi, menghindari halusinasi.
    """
    # 1. Ringkas konteks laporan yang relevan dari DataFrame
    total_laporan = len(context_reports_df) if context_reports_df is not None else 0
    kritis_count = 0
    tinggi_count = 0
    top_lokasi = []
    
    if total_laporan > 0:
        kritis_count = int((context_reports_df["label_prioritas"] == "Kritis").sum()) if "label_prioritas" in context_reports_df.columns else 0
        tinggi_count = int((context_reports_df["label_prioritas"] == "Tinggi").sum()) if "label_prioritas" in context_reports_df.columns else 0
        
        # Ambil sampel 5 laporan terbaru untuk grounding
        sample_reports = context_reports_df.head(5)[
            ["kode_laporan", "lokasi", "keparahan", "label_prioritas", "tipe_lahan", "jarak_pemukiman_km"]
        ].to_dict(orient="records")
        sample_str = json.dumps(sample_reports, indent=2, ensure_ascii=False)
    else:
        sample_str = "[]"

    # Context prompt untuk AI
    system_instruction = (
        "Anda adalah IGNIS Intelligent AI Assistant, asisten sistem pendukung keputusan mitigasi karhutla di Indonesia. "
        "ATURAN INTEGRITAS:\n"
        "1. Jawab HANYA berdasarkan data faktual yang diberikan dan SOP penanggulangan karhutla resmi.\n"
        "2. DILARANG KERAS mengarang ID laporan fiktif, koordinat palsu, atau nama instansi asing di luar konteks.\n"
        "3. Selalu sebutkan ID laporan (contoh: IGNIS-SIM-001) atau dasar SOP saat memberikan bukti informasi.\n"
        "4. Gunakan Bahasa Indonesia formal, taktis, dan solutif.\n"
        "5. Jika data tidak ada dalam database, katakan dengan jujur bahwa informasi tersebut tidak ditemukan.\n"
    )

    grounding_data = (
        f"DATA SISTEM IGNIS SAAT INI:\n"
        f"- Total Laporan Terdaftar: {total_laporan}\n"
        f"- Laporan Status Kritis: {kritis_count}\n"
        f"- Laporan Status Tinggi: {tinggi_count}\n"
        f"- Cuplikan Laporan Terbaru:\n{sample_str}\n\n"
        f"{SOP_KARHUTLA_KNOWLEDGE_BASE}\n"
    )

    full_prompt = f"{grounding_data}\n\nPertanyaan Pengguna: {user_query}"

    # Coba panggil Gemini
    res = call_gemini_api(full_prompt, system_instruction)

    if not res.is_fallback:
        return {
            "answer": res.text,
            "source": f"Gemini API ({res.model_name})",
            "is_fallback": False,
            "warning": None
        }

    # ==================== FALLBACK ENGINE JIKA GEMINI TIDAK AKTIF ====================
    query_lower = user_query.lower()
    fallback_response = ""

    if "kritis" in query_lower or "darurat" in query_lower or "paling parah" in query_lower:
        fallback_response = (
            f"**[ANALISIS DATASET SISTEM]**\n"
            f"Berdasarkan rekaman database IGNIS, saat ini terdapat **{kritis_count} laporan** dengan prioritas risiko **KRITIS** dari total {total_laporan} laporan.\n\n"
            f"**SOP Penanganan Segera (Permen LHK No. P.32/2016):**\n"
            f"- Laporan Kritis memerlukan pengerahan Helikopter Water Bombing BNPB dan tim Manggala Agni Daops dalam kurun waktu < 2 jam.\n"
            f"- Evaluasi jarak ke pemukiman (< 500 meter) mewajibkan koordinasi posko kesehatan untuk pembagian masker N95 dan evakuasi balita/lansia rawan ISPA."
        )
    elif "sop" in query_lower or "aturan" in query_lower or "prosedur" in query_lower:
        fallback_response = (
            f"**[REFERENSI REGULASI & SOP PENANGGULANGAN KARHUTLA]**\n"
            f"1. **Tingkat Kritis:** Komando di bawah Satgas Karhutla Terpadu (TNI, Polri, BPBD, Manggala Agni) dengan operasi pemadaman udara.\n"
            f"2. **Tingkat Tinggi:** Pembuatan sekat bakar darurat selebar minimal 4 meter untuk menghentikan perambatan api permukaan.\n"
            f"3. **Tingkat Sedang:** Mobilisasi Masyarakat Peduli Api (MPA) desa dan pengecekan pasokan air embung.\n"
            f"4. **Landasan Hukum:** UU No. 32/2009 Pasal 69 ayat (1) huruf h (Larangan membakar lahan) ancaman pidana hingga 10 tahun penjara."
        )
    elif "gambut" in query_lower:
        fallback_response = (
            f"**[KARAKTERISTIK LAHAN GAMBUT - BRGM & KLHK]**\n"
            f"Lahan gambut memiliki risiko kebakaran bawah tanah (*smoldering*) yang tidak tampak di permukaan namun menghasilkan asap tebal karbon monoksida.\n\n"
            f"**Langkah Mitigasi Kunci:**\n"
            f"- Pemadaman harus menggunakan teknik suntik gambut (*peat spear injector*) bertekanan tinggi hingga kedalaman 1-2 meter.\n"
            f"- Pembasahan kembali (*rewetting*) melalui penutupan sekat kanal untuk menaikkan Tinggi Muka Air (TMA) di atas -0.4 meter."
        )
    else:
        fallback_response = (
            f"**[DATA DATABASE IGNIS]**\n"
            f"Sistem mencatat {total_laporan} laporan karhutla aktif (Kritis: {kritis_count}, Tinggi: {tinggi_count}).\n\n"
            f"Anda dapat menanyakan informasi mengenai statistik kebakaran, prosedur SOP KLHK/BNPB, tindakan mitigasi lahan gambut, maupun rincian prioritas risiko laporan tertentu."
        )

    return {
        "answer": fallback_response,
        "source": "Fallback Rule-Based Expert System [MODE FALLBACK - BUKAN HASIL LLM]",
        "is_fallback": True,
        "warning": f"Gemini API tidak aktif ({res.error_msg}). Menggunakan penalaran deterministik lokal."
    }

# ==================== FITUR 9: REKOMENDASI MITIGASI TERSTRUKTUR ====================

def generate_mitigation_recommendation(report: Dict[str, Any], score_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menyusun rekomendasi penanganan komprehensif:
    1. Prioritas tindakan (Segera / Jangka Pendek / Jangka Panjang)
    2. Instansi penanggung jawab terkait
    3. Dasar pertimbangan & SOP hukum
    4. Alokasi sumber daya taktis
    """
    kode = report.get("kode_laporan", "IGNIS-N/A")
    lokasi = report.get("lokasi", "N/A")
    kab = report.get("kabupaten", "N/A")
    prov = report.get("provinsi", "N/A")
    tipe_lahan = report.get("tipe_lahan", "Semak Belukar")
    jarak = float(report.get("jarak_pemukiman_km", 2.0))
    skor = score_info.get("total_skor", 50.0)
    label = score_info.get("label", "Sedang")

    # Prompt terstruktur LLM
    system_instruction = (
        "Anda adalah Ahli Perencanaan Strategis Mitigasi Bencana Kebakaran Hutan dan Lahan di Indonesia (KLHK/BNPB). "
        "Tugas Anda: Buat rekomendasi penanganan karhutla yang taktis, berdasar hukum, terstruktur, dan spesifik pada konteks lokasi. "
        "Format Output HARUS berupa JSON valid dengan kunci:\n"
        "- tindakan_segera (array of string, tindakan darurat 0-6 jam)\n"
        "- tindakan_jangka_pendek (array of string, pencegahan 1-7 hari)\n"
        "- tindakan_jangka_panjang (array of string, kebijakan restorasi/hukum)\n"
        "- instansi_terkait (array of object: {'instansi': string, 'peran': string})\n"
        "- dasar_pertimbangan (string, analisis risiko spasial & ekologis)\n"
        "- alokasi_sumber_daya (array of string, logistik/armada yang dibutuhkan)\n"
    )

    user_prompt = (
        f"Laporan Karhutla:\n"
        f"- ID Laporan: {kode}\n"
        f"- Wilayah: {lokasi}, Kabupaten {kab}, {prov}\n"
        f"- Tipe Lahan: {tipe_lahan}\n"
        f"- Jarak ke Pemukiman: {jarak} km\n"
        f"- AI Risk Score: {skor}/100 (Label: {label})\n"
        f"- Deskripsi Kejadian: {report.get('deskripsi', '')}\n\n"
        f"Berikan rekomendasi mitigasi resmi berbasis SOP Karhutla Indonesia dalam format JSON murni tanpa markdown wrapper."
    )

    res = call_gemini_api(user_prompt, system_instruction)

    if not res.is_fallback:
        try:
            # Bersihkan markdown jika ada
            raw_text = res.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(raw_text)
            parsed["sumber_rekomendasi"] = f"Google Gemini 2.5 Flash ({res.model_name})"
            parsed["is_fallback"] = False
            return parsed
        except Exception:
            # Jika parsing JSON gagal, lanjutkan ke fallback terstruktur
            pass

    # ==================== FALLBACK EXPERT MITIGATION ENGINE ====================
    # Aturan deterministik berbasis skor dan tipe ekosistem
    if label == "Kritis":
        tindakan_segera = [
            f"Mobilisasi darurat Satgas Udara BNPB untuk operasi Water Bombing helikopter di koordinat {report.get('latitude', 0):.4f}, {report.get('longitude', 0):.4f}.",
            f"Evakuasi warga rentan (bayi, ibu hamil, lansia) dalam radius {jarak:.1f} km dari garis asap menuju posko pengungsian ramah udara bersih.",
            "Penyekatan api aktif (firebreak) menggunakan ekskavator untuk memutus jalur bara gambut menuju perumahan."
        ]
        instansi = [
            {"instansi": "BNPB (Badan Nasional Penanggulangan Bencana)", "peran": "Pengerahan armada udara Water Bombing dan dukungan logistik masker."},
            {"instansi": "BPBD Kabupaten " + kab, "peran": "Komando tanggap darurat daerah dan manajemen posko evakuasi pengungsi."},
            {"instansi": "Manggala Agni Daops", "peran": "Pemadaman regu darat dan teknik suntik gambut pada lapisan tanah dalam."},
            {"instansi": "Dinas Kesehatan Kab. " + kab, "peran": "Penyediaan posko oksigen darurat dan pembagian masker N95."}
        ]
        alokasi = [
            "2 Unit Helikopter Water Bombing",
            "4 Unit Pompa Bertekanan Tinggi Mark-3 dengan Peat Spear Nozzle",
            "1.000 Meter Selang Tembak Sintetis 1.5 inch",
            "5.000 Lembar Masker Standar N95"
        ]
    elif label == "Tinggi":
        tindakan_segera = [
            "Pengerahan 3 regu gabungan Manggala Agni dan Damkar daerah untuk melokalisir perimeter kebakaran.",
            f"Pembuatan parit basah darurat di perbatasan lahan {tipe_lahan} dengan area perkebunan warga.",
            "Pemasangan rambu bahaya asap tebal di jalan akses terdekat untuk keselamatan pengguna jalan."
        ]
        instansi = [
            {"instansi": "Manggala Agni KLHK", "peran": "Pemadaman pemadatan bara permukaan dan penetrasi serasah."},
            {"instansi": "TNI / POLRI (Koramil & Polsek)", "peran": "Pengamanan perimeter lokasi dan investigasi saksi asal usul api."},
            {"instansi": "Kelompok Masyarakat Peduli Api (MPA)", "peran": "Pemandu medan dan suplai air dari kanal/embung terdekat."}
        ]
        alokasi = [
            "2 Unit Mobil Tangki Damkar 4x4",
            "6 Unit Pompa Jinjing Apung (Floating Pump)",
            "Drone Thermal Pemantau Persebaran Titik Panas"
        ]
    else:
        tindakan_segera = [
            "Patroli pemantauan darat berkala oleh Masyarakat Peduli Api (MPA) setempat.",
            "Pendinginan sisa arang dan pembasahan vegetasi kering (mop-up) agar tidak tersulut angin.",
            "Edukasi lisan kepada pemilik lahan sekitar mengenai larangan membakar saat cuaca terik."
        ]
        instansi = [
            {"instansi": "Pemerintah Desa & MPA", "peran": "Patroli rutin dan penyediaan embung air desa."},
            {"instansi": "Babinsa / Bhabinkamtibmas", "peran": "Sosialisasi sanksi hukum pembakaran lahan."}
        ]
        alokasi = [
            "1 Unit Pompa Portable Jinjing",
            "Alat pelindung diri standar (sepatu safety, kacamata goggle, cangkul sekat)"
        ]

    jangka_pendek = [
        "Pemeriksaan kelembaban serasah dan Tinggi Muka Air (TMA) gambut secara harian pasca insiden.",
        "Penyelidikan forensik kepolisian untuk mendeteksi unsur kesengajaan land clearing.",
        "Pengaktifan posko siaga darurat desa selama cuaca kering berturut-turut."
    ]

    jangka_panjang = [
        "Pembangunan infrastruktur sekat kanal permanen (canal blocking) dan embung penampungan air hujan.",
        "Pemberian bantuan alat pencacah rumput/vegetasi (mulcher) mekanis untuk pertanian tanpa bakar (PLTB).",
        "Penetapan zonasi kawasan perlindungan ekosistem gambut dan penegakan sanksi perdata/pidana bagi perusak lingkungan."
    ]

    dasar_pertimbangan = (
        f"Keputusan mitigasi ini disusun berdasarkan analisis risiko spasial IGNIS dengan skor {skor}/100 ({label}). "
        f"Karakteristik ekologis lahan berjenis {tipe_lahan} dan kedekatan pemukiman sejauh {jarak:.1f} km mewajibkan "
        f"tindakan pengamanan berdasar Permen LHK No. P.32/2016 serta UU No. 32/2009 Pasal 69."
    )

    return {
        "tindakan_segera": tindakan_segera,
        "tindakan_jangka_pendek": jangka_pendek,
        "tindakan_jangka_panjang": jangka_panjang,
        "instansi_terkait": instansi,
        "dasar_pertimbangan": dasar_pertimbangan,
        "alokasi_sumber_daya": alokasi,
        "sumber_rekomendasi": "Fallback Rule-Based Expert System [MODE FALLBACK - BUKAN HASIL LLM]",
        "is_fallback": True
    }
