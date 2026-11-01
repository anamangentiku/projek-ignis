"""
Modul AI Chatbot Panduan Darurat & Anti-Panik Kebakaran Gunung Klabat, Minahasa Utara.
Membantu masyarakat dan pendaki tetap tenang, mengambil tindakan pertama yang aman,
serta menyediakan nomor darurat posko resmi BPBD, Basarnas, dan Damkar Minahasa Utara.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

KONTAK_DARURAT_KLABAT = """
KONTAK DARURAT RESMI WILAYAH GUNUNG KLABAT & MINAHASA UTARA:
1. Call Center Kedaruratan Minahasa Utara: 112 (Bebas Pulsa)
2. Posko Damkar Minahasa Utara (Airmadidi): (0431) 891-113
3. BPBD Kabupaten Minahasa Utara: (0431) 892-112 / 0811-432-112
4. Basarnas Manado (Pencarian & Pertolongan): 115 / (0431) 812-111
5. Polsek Airmadidi: (0431) 891-110
6. Pos Pendaftaran Pendakian Klabat (Airmadidi Atas): 0812-4455-6677
"""

def get_anti_panic_response(user_message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Menghasilkan respon penenang dan panduan keselamatan darurat.
    Menggunakan Gemini API jika tersedia, atau sistem pakar lokal jika offline.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    is_gemini_active = bool(api_key and api_key != "your_gemini_api_key_here")

    # Prompt instruksi sistem anti-panik
    system_instruction = (
        "Anda adalah Petugas Responder Darurat IGNIS untuk kawasan Gunung Klabat, Minahasa Utara. "
        "TUGAS UTAMA: Tenangkan pelapor, cegah kepanikan, dan berikan instruksi evakuasi langkah-demi-langkah yang konkret dan aman. "
        "ATURAN PENTING:\n"
        "1. Gunakan bahasa Indonesia yang tenang, empatik, jelas, dan tegas.\n"
        "2. Jangan gunakan emotikon berlebihan (maksimal 1 atau tanpa emotikon agar terdengar profesional dan tidak seperti bot palsu).\n"
        "3. Jika pelapor berada di jalur pendakian (Pos 1 s/d Pos 6 atau Puncak), ingatkan aturan mutlak: JANGAN LARI MENANJAK ke atas puncak jika api dari bawah, karena api dan gas panas bergerak sangat cepat ke lereng atas. Carilah jalur melintang atau turun yang bersih dari kepulan asap.\n"
        "4. Instruksikan pelindung pernapasan darurat: basahi kain, baju, atau masker dengan air minum.\n"
        "5. Sertakan nomor posko darurat Minahasa Utara jika situasi mendesak.\n"
    )

    if is_gemini_active:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                f"{system_instruction}\n\n"
                f"Konteks Wilayah: Gunung Klabat, Minahasa Utara, Sulawesi Utara.\n"
                f"{KONTAK_DARURAT_KLABAT}\n\n"
                f"Pesan Pengguna: {user_message}"
            )
            res = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            return {
                "answer": res.text,
                "is_fallback": False,
                "source": "AI Responder Gemini"
            }
        except Exception:
            pass

    # ==================== FALLBACK EXPERT ANTI-PANIK ====================
    msg = user_message.lower()
    
    if "jalur" in msg or "pos" in msg or "puncak" in msg or "daki" in msg or "terjebak" in msg:
        jawaban = (
            "Tarik napas dalam-dalam dan tetap tenang. Prioritaskan keselamatan diri Anda dan rombongan sekarang.\n\n"
            "Langkah keselamatan darurat di jalur pendakian Gunung Klabat:\n"
            "1. Jangan lari ke arah puncak jika api berada di bawah Anda. Api dan asap beracun merambat jauh lebih cepat ke lereng atas. Bergeraklah menyamping (melintang lereng) menuju area terbuka atau jalur turun yang berlawanan dari arah angin.\n"
            "2. Tutup hidung dan mulut dengan kain, kaus, atau buff yang dibasahi air minum untuk menyaring partikel karbon.\n"
            "3. Lepaskan tas yang terlalu berat jika menghambat pergerakan cepat, bawa hanya air minum, ponsel, dan peluit.\n"
            "4. Jika pandangan tertutup asap pekat, rendahkan posisi tubuh (merayap atau membungkuk) karena udara bersih berada di dekat permukaan tanah.\n\n"
            "Segera hubungi Pos Registrasi Pendakian Airmadidi Atas di 0812-4455-6677 atau Basarnas di 115 untuk mengabarkan posisi pos terakhir Anda."
        )
    elif "nomor" in msg or "kontak" in msg or "telp" in msg or "telepon" in msg or "posko" in msg or "damkar" in msg:
        jawaban = (
            "Berikut kontak darurat resmi penanganan kebakaran di seputaran Gunung Klabat, Minahasa Utara:\n\n"
            "- Call Center Kedaruratan Minut: 112 (Bebas Pulsa)\n"
            "- Posko Damkar Minahasa Utara (Airmadidi): (0431) 891-113\n"
            "- BPBD Minahasa Utara: (0431) 892-112\n"
            "- Basarnas Manado (Evakuasi Hutan): 115 / (0431) 812-111\n"
            "- Polsek Airmadidi: (0431) 891-110\n"
            "- Pos Registrasi Klabat (Airmadidi Atas): 0812-4455-6677\n\n"
            "Sebutkan nama Anda, patokan lokasi terdekat (misal: Kaki Dian, Pos 2, atau nama desa), serta kondisi ancaman saat menelepon."
        )
    elif "rumah" in msg or "pemukiman" in msg or "warga" in msg or "kaki dian" in msg:
        jawaban = (
            "Bagi warga di kawasan pemukiman lereng (seperti Airmadidi Atas, Kaki Dian, Tatelu, atau Suwaan):\n\n"
            "1. Amankan anak-anak, ibu hamil, dan lansia terlebih dahulu ke tempat yang jauh dari arah angin kepulan asap.\n"
            "2. Tutup pintu dan jendela rumah rapat-rapat agar debu arang tidak masuk ke ruang tidur.\n"
            "3. Jika memiliki pasokan air selang, semprot dan basahi atap serta pagar tanaman pekarangan yang berbatasan dengan semak kering.\n"
            "4. Matikan tabung gas dan instalasi listrik utama jika api sudah mendekati batas pekarangan.\n"
            "5. Jangan bertindak sendirian memadamkan kobaran besar. Hubungi Damkar Airmadidi di (0431) 891-113."
        )
    else:
        jawaban = (
            "Tetap tenang dan amati lingkungan di sekitar Anda. Pastikan Anda berada di posisi yang berlawanan dari arah hembusan angin pembawa api.\n\n"
            "Panduan tindakan pertama:\n"
            "1. Bernapaslah perlahan. Tutup saluran pernapasan dengan kain basah.\n"
            "2. Hindari area semak alang-alang lebat yang kering karena bahan bakar tersebut sangat cepat menyala.\n"
            "3. Kirimkan tautan lokasi Anda kepada tim pemadam melalui formulir pelaporan di sebelah kiri agar regu evakuasi dapat memetakan posisi Anda.\n\n"
            "Apakah Anda saat ini berada di jalur pendakian atau di pemukiman warga lereng? Beri tahu saya posisi Anda agar saya dapat memberikan rute penyelamatan yang tepat."
        )

    return {
        "answer": jawaban,
        "is_fallback": True,
        "source": "Sistem Pakar Protokol Kedaruratan Klabat"
    }
