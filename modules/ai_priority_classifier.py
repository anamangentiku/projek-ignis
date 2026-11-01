"""
AI Priority Classifier & Risk Scoring menggunakan Gemini API (gemini-3.8-flash).
Menganalisis otomatis laporan kebakaran masyarakat di seputaran Gunung Klabat, Minahasa Utara,
sehingga masyarakat TIDAK PERLU lagi memilih tingkat keparahan secara manual.
"""

import os
import json
import re
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

def classify_fire_priority_ai(
    deskripsi: str,
    lokasi_area: str,
    jarak_pemukiman_km: float,
    tipe_vegetasi: str,
    gambar_kebakaran: str = ""
) -> Dict[str, Any]:
    """
    Menggunakan Google Gemini 3.8 Flash untuk menentukan secara otomatis:
    - Tingkat keparahan (Kritis, Tinggi, Sedang, Rendah)
    - Skor prioritas (0.0 - 100.0)
    - Label prioritas penanganan
    - Alasan analisis prioritas yang logis dan taktis untuk regu pemadam
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    prompt = f"""
Anda adalah Sistem AI Penilai Prioritas Risiko Kebakaran Hutan Gunung Klabat (Minahasa Utara).
Tugas Anda: Analisis laporan masyarakat berikut secara objektif dan tentukan tingkat urgensi penanganan untuk Regu Pemadam & BPBD Minahasa Utara.

Konteks Laporan:
- Lokasi Kejadian: {lokasi_area}
- Deskripsi dari Masyarakat: "{deskripsi}"
- Estimasi Jarak ke Pemukiman: {jarak_pemukiman_km} km
- Karakteristik Vegetasi: {tipe_vegetasi}

Kriteria Penilaian Gunung Klabat:
1. KRITIS (Skor 75 - 100): Api sangat dekat dengan pemukiman warga (< 500m seperti kawasan Kaki Dian / Airmadidi Atas / Suwaan), asap tebal membahayakan balita/lansia, atau api memutus jalur evakuasi pendaki.
2. TINGGI (Skor 55 - 74): Api aktif merambat di jalur pendakian (Pos 1 s/d Pos 6), membakar kebun produktif cengkeh/pala, atau angin kencang berpotensi memperluas kebakaran.
3. SEDANG (Skor 35 - 54): Api terlokalisir di savana puncak (Danau Kering Klabat 1.995 mdpl) yang jauh dari pemukiman (> 2 km) atau vegetasi basah.
4. RENDAH (Skor 0 - 34): Sisa pembakaran terkendali, abu, atau titik panas kecil yang sudah mulai dilokalisir warga.

Format Balasan WAJIB berupa JSON murni tanpa markdown wrapper:
{{
  "keparahan": "Kritis" | "Tinggi" | "Sedang" | "Rendah",
  "skor_prioritas": float_antara_0_sampai_100,
  "label_prioritas": "Kritis" | "Tinggi" | "Sedang" | "Rendah",
  "alasan_prioritas": "penjelasan padat taktis mengapa laporan ini harus didahulukan dan apa potensi bahaya terbesarnya"
}}
"""

    if api_key and api_key != "your_gemini_api_key_here":
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            raw_text = response.text.strip()
            
            # Ekstrak JSON
            if "{" in raw_text and "}" in raw_text:
                json_str = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
                data = json.loads(json_str)
                return {
                    "keparahan": data.get("keparahan", "Tinggi"),
                    "skor_prioritas": round(float(data.get("skor_prioritas", 70.0)), 1),
                    "label_prioritas": data.get("label_prioritas", "Tinggi"),
                    "alasan_prioritas": data.get("alasan_prioritas", "Analisis otomatis Gemini 3.8 Flash."),
                    "source": "AI Gemini 3.8 Flash"
                }
        except Exception:
            pass

    # ==================== FALLBACK HEURISTIC KLABAT ====================
    # Jika API mengalami kendala jaringan, jalankan rule-based scoring akurat
    desc_l = deskripsi.lower()
    
    # 1. Deteksi Keparahan Otomatis dari Kata Kunci
    if any(k in desc_l for k in ["besar", "merambat cepat", "hebat", "terjebak", "sesak", "kaki dian", "rumah", "sekolah", "panik"]):
        keparahan = "Kritis"
        s_sev = 38.0
    elif any(k in desc_l for k in ["jalur", "pos", "tebal", "membara", "cengkeh", "pala", "kebun"]):
        keparahan = "Tinggi"
        s_sev = 28.0
    elif any(k in desc_l for k in ["puncak", "savana", "kawah", "danau", "sedang"]):
        keparahan = "Sedang"
        s_sev = 18.0
    else:
        keparahan = "Rendah"
        s_sev = 10.0

    # 2. Bobot Jarak Pemukiman
    if jarak_pemukiman_km <= 0.4:
        s_dst = 35.0
        ket_dst = f"Sangat dekat pemukiman ({jarak_pemukiman_km} km), bahaya asap dan kobaran langsung ke warga."
    elif jarak_pemukiman_km <= 1.0:
        s_dst = 25.0
        ket_dst = f"Dekat pemukiman lereng ({jarak_pemukiman_km} km)."
    elif jarak_pemukiman_km <= 2.5:
        s_dst = 18.0
        ket_dst = f"Di zona pendakian lereng ({jarak_pemukiman_km} km dari desa)."
    else:
        s_dst = 8.0
        ket_dst = f"Jauh dari pemukiman ({jarak_pemukiman_km} km)."

    # 3. Bobot Vegetasi
    if "semak" in tipe_vegetasi.lower() or "alang" in tipe_vegetasi.lower():
        s_veg = 25.0
    elif "cengkeh" in tipe_vegetasi.lower() or "pala" in tipe_vegetasi.lower():
        s_veg = 20.0
    else:
        s_veg = 14.0

    total_skor = round(min(100.0, s_sev + s_dst + s_veg), 1)

    if total_skor >= 75.0:
        label = "Kritis"
    elif total_skor >= 55.0:
        label = "Tinggi"
    elif total_skor >= 35.0:
        label = "Sedang"
    else:
        label = "Rendah"

    alasan = f"Skor Prioritas {total_skor}/100 ({label}). Berdasarkan analisis teks '{deskripsi[:45]}...', {ket_dst}"

    return {
        "keparahan": keparahan,
        "skor_prioritas": total_skor,
        "label_prioritas": label,
        "alasan_prioritas": alasan,
        "source": "AI Heuristic Klabat"
    }
