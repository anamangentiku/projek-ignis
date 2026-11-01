"""
Root Cause Analysis (RCA) - 5 Whys Module for IGNIS.
Menerapkan metodologi 5 Whys terstruktur untuk menginvestigasi akar masalah karhutla.
Menyediakan penalaran bertahap dari gejala permukaan hingga kelemahan sistemik/akar penyebab.
"""

from typing import Dict, Any, List

# Template rantai 5 Whys berbasis skenario empiris Karhutla Indonesia
RCA_SCENARIOS = {
    "Gambut_Kering": {
        "title": "Kebakaran Lahan Gambut Dalam Akibat Penurunan Tinggi Muka Air (TMA)",
        "why1": "Mengapa api terus membakar dan berasap pekat berhari-hari? (Gejala: Api bawah tanah / smoldering membakar lapisan gambut kering hingga kedalaman 2 meter)",
        "why2": "Mengapa gambut menjadi sangat kering dan mudah terbakar? (Kondisi: Tinggi Muka Air tanah gambut anjlok > 0.4 meter akibat musim kemarau dan drainase kanal)",
        "why3": "Mengapa kanal-kanal di kawasan tersebut mengalirkan air keluar tanpa sekat? (Fisik: Sekat kanal (canal blocking) rusak atau belum dibangun oleh pemegang konsesi/masyarakat)",
        "why4": "Mengapa restorasi hidrologis dan tata kelola sekat kanal tidak terpelihara? (Operasional: Kurangnya pengawasan berkala dan minimnya alokasi dana pemeliharaan infrastruktur pembasahan gambut)",
        "why5": "Akar Masalah Sistemik (Root Cause): Belum optimalnya penegakan regulasi pembasahan gambut (rewetting) serta integrasi pemantauan sensor TMA terpadu antar instansi dan masyarakat setempat."
    },
    "Pembukaan_Lahan": {
        "title": "Pembakaran Liar untuk Land Clearing Kebun Tanpa Bakar (PLTB) yang Terabaikan",
        "why1": "Mengapa titik api muncul serentak di tepian semak belukar dan perkebunan? (Gejala: Ditemukan pola pembakaran sengaja dalam petak-petak teratur)",
        "why2": "Mengapa oknum melakukan pembakaran lahan secara sengaja? (Kondisi: Membakar adalah metode pembersihan lahan paling murah dan cepat dibandingkan alat berat mekanis)",
        "why3": "Mengapa insentif atau bantuan mekanis Pembukaan Lahan Tanpa Bakar (PLTB) tidak digunakan? (Ekonomi: Biaya sewa ekskavator tinggi dan petani swadaya belum mendapatkan akses subsidi alat pengolah tanah)",
        "why4": "Mengapa aturan larangan membakar tidak ditaati oleh kelompok perambah/pelaku? (Sosial: Rendahnya kesadaran hukum dan persepsi bahwa api dapat dikendalikan dengan sekat sederhana)",
        "why5": "Akar Masalah Sistemik (Root Cause): Keterbatasan akses teknologi ramah lingkungan terjangkau bagi petani skala mikro serta lemahnya patroli terpadu penegakan hukum di perbatasan kawasan lindung."
    },
    "Akses_Pemadaman": {
        "title": "Eskalasi Api Menjadi Kritis Akibat Keterlambatan Respon Awal",
        "why1": "Mengapa api kecil di semak belukar cepat membesar meluas hingga 10 hektar? (Gejala: Petugas pemadam terlambat tiba di titik api 3 jam setelah laporan)",
        "why2": "Mengapa petugas pemadam darat terlambat mencapai titik kobaran? (Kondisi: Jalur darat tertutup rawa dan jalan setapak tidak bisa dilewati mobil tangki pemadam)",
        "why3": "Mengapa tidak digunakan pompa portabel dan selang panjang darurat? (Fasilitas: Sumber air alami (embung/parit) di sekitar lokasi mengering akibat kemarau panjang)",
        "why4": "Mengapa tidak dilakukan water bombing helikopter pada fase awal kebakaran? (Komunikasi: Informasi laporan terlambat diverifikasi dan koordinasi antar posko belum terintegrasi)",
        "why5": "Akar Masalah Sistemik (Root Cause): Belum adanya sistem peringatan dini berbasis geospasial real-time yang langsung mengkoneksikan laporan masyarakat dengan armada satgas udara."
    },
    "Kelalaian_Manusia": {
        "title": "Penyalaan Api Akibat Kelalaian Aktivitas Manusia di Kawasan Wisata/Hutan",
        "why1": "Mengapa savana atau semak kering terbakar tiba-tiba di siang hari yang terik? (Gejala: Muncul kobaran api dari bekas aktivitas manusia/pengunjung)",
        "why2": "Mengapa sumber api ditinggalkan dalam keadaan menyala? (Perilaku: Pengunjung membuang puntung rokok sembarangan atau menggunakan flare/api unggun)",
        "why3": "Mengapa pengunjung bebas membawa dan menyalakan material pemicu kebakaran? (Pengawasan: SOP pemeriksaan barang bawaan di pintu masuk kawasan belum ketat)",
        "why4": "Mengapa rambu larangan dan edukasi bahaya kebakaran tidak diindahkan? (Sosial: Rendahnya kesadaran ekologis dan persepsi risiko kebakaran savana kering yang minim)",
        "why5": "Akar Masalah Sistemik (Root Cause): Kelemahan sistem manajemen pengunjung kawasan konservasi dan ketiadaan sanksi preventif yang tegas pada musim kemarau ekstrem."
    }
}

def generate_5whys_analysis(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menghasilkan analisis 5 Whys yang relevan secara kontekstual berdasarkan
    tipe lahan, keparahan, dan deskripsi laporan.
    """
    tipe_lahan = report.get("tipe_lahan", "")
    desc = str(report.get("deskripsi", "")).lower()
    
    # Pilih skenario acuan yang paling cocok
    if "gambut" in tipe_lahan.lower() or "gambut" in desc:
        scenario_key = "Gambut_Kering"
    elif "sawit" in tipe_lahan.lower() or "bakar" in desc or "ladang" in desc or "tebasan" in desc:
        scenario_key = "Pembukaan_Lahan"
    elif "wisata" in desc or "bromo" in desc or "rokok" in desc or "flare" in desc or "unggun" in desc:
        scenario_key = "Kelalaian_Manusia"
    else:
        scenario_key = "Akses_Pemadaman"

    sc = RCA_SCENARIOS[scenario_key]

    return {
        "scenario_key": scenario_key,
        "title": sc["title"],
        "why1": sc["why1"],
        "why2": sc["why2"],
        "why3": sc["why3"],
        "why4": sc["why4"],
        "why5": sc["why5"],
        "root_cause_summary": sc["why5"]
    }
