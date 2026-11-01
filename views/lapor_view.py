"""
Pelaporan Masyarakat View for IGNIS.
Formulir pelaporan partisipatif masyarakat terhadap kejadian kebakaran hutan dan lahan.
Terintegrasi langsung dengan validasi geografis, deteksi duplikasi, AI risk scoring, dan persistensi SQLite.
"""

import streamlit as st
from datetime import datetime
from database.db_manager import insert_laporan, get_all_laporan
from modules.preprocessing import clean_text, validate_coordinates
from modules.verifier import run_system_verification
from modules.scoring import calculate_risk_score

# Preset koordinat titik rawan karhutla populer di Indonesia untuk memudahkan uji coba pengguna
HOTSPOT_PRESETS = {
    "Pilih Preset Koordinat Cepat...": (0.0, 0.0, "", "", ""),
    "🔥 Riau - Bengkalis (Gambut Dalam)": (1.4800, 102.1300, "Desa Sepahat, Kec. Bandar Laksamana", "Bengkalis", "Riau"),
    "🔥 Riau - Pelalawan (Semenanjung Kampar)": (0.3500, 102.0500, "Desa Teluk Meranti", "Pelalawan", "Riau"),
    "🔥 Kalteng - Pulang Pisau (Ex-PLG Gambut)": (-2.7500, 114.2500, "Desa Taruna Jaya, Kec. Jabiren", "Pulang Pisau", "Kalimantan Tengah"),
    "🔥 Kalteng - Kotawaringin Timur (Sampit)": (-2.5300, 112.9500, "Jl. Sudirman KM 8 Baamang", "Kotawaringin Timur", "Kalimantan Tengah"),
    "🔥 Sumsel - OKI (Rawa Gambut Pangkalan Lampam)": (-3.4200, 105.0500, "Desa Deling, Kec. Pangkalan Lampam", "Ogan Komering Ilir (OKI)", "Sumatera Selatan"),
    "🔥 Kalbar - Kubu Raya (Dekat Bandara)": (-0.1500, 109.4000, "Kec. Sungai Raya Parit Mayor", "Kubu Raya", "Kalimantan Barat"),
    "🔥 Jatim - Bromo Tengger Semeru (Savana/Hutan)": (-7.9400, 112.9500, "Blok Savana Lembah Watangan TNBTS", "Pasuruan / Probolinggo", "Jawa Timur")
}

def render_lapor_view():
    st.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">📝 Formulir Pelaporan Karhutla Masyarakat</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Laporkan kejadian titik api, kebakaran lahan, atau kepulan asap tebal di sekitar Anda.
            Sistem cerdas IGNIS akan memvalidasi data dan menghitung prioritas penanganan secara instan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("##### ⚡ Bantuan Cepat Pengisian Koordinat Hotspot")
        preset_choice = st.selectbox(
            "Gunakan Preset Koordinat Wilayah Rawan (Opsional):",
            list(HOTSPOT_PRESETS.keys())
        )
        default_lat, default_lon, default_lok, default_kab, default_prov = HOTSPOT_PRESETS[preset_choice]

    st.markdown("---")

    with st.form("form_pelaporan_karhutla", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            nama_pelapor = st.text_input("Nama Lengkap Pelapor *", placeholder="Contoh: Hendra Wijaya")
            kontak_pelapor = st.text_input("Nomor HP / WhatsApp Aktif *", placeholder="Contoh: 081234567890")
            provinsi = st.text_input("Provinsi *", value=default_prov if default_prov else "Riau")
            kabupaten = st.text_input("Kabupaten / Kota *", value=default_kab if default_kab else "Bengkalis")
            lokasi = st.text_input("Nama Desa / Dusun / Titik Patokan *", value=default_lok if default_lok else "Desa Sepahat")

        with c2:
            lat_input = st.number_input(
                "Latitude (Garis Lintang RI: -11 s/d 6) *",
                value=float(default_lat) if default_lat != 0.0 else 1.4800,
                format="%.5f"
            )
            lon_input = st.number_input(
                "Longitude (Garis Bujur RI: 95 s/d 141) *",
                value=float(default_lon) if default_lon != 0.0 else 102.1300,
                format="%.5f"
            )
            tanggal_lapor = st.text_input(
                "Tanggal & Jam Kejadian (YYYY-MM-DD HH:MM:SS) *",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            keparahan = st.selectbox(
                "Tingkat Keparahan Pengamatan Awal *",
                ["Sedang", "Tinggi", "Kritis", "Rendah"],
                index=1
            )
            tipe_lahan = st.selectbox(
                "Tipe Ekosistem / Karakteristik Lahan *",
                ["Gambut", "Semak Belukar", "Perkebunan Sawit", "Hutan Lindung", "Lahan Terbuka / Pertanian"]
            )

        c3, c4 = st.columns(2)
        with c3:
            jarak_km = st.number_input(
                "Estimasi Jarak Api ke Pemukiman Terdekat (km) *",
                min_value=0.05,
                max_value=100.0,
                value=1.2,
                step=0.1
            )
            luas_ha = st.number_input(
                "Estimasi Luas Area Terbakar (Hektar)",
                min_value=0.1,
                max_value=1000.0,
                value=2.5,
                step=0.5
            )

        with c4:
            bukti_url = st.text_input(
                "Tautan Dokumentasi / Foto Bukti (URL / Catatan Foto)",
                value="https://storage.internal/user_upload/bukti_lapangan.jpg"
            )

        deskripsi = st.text_area(
            "Deskripsi Detail Kejadian & Bahaya *",
            placeholder="Jelaskan kondisi api (warna asap, arah angin, sumber air, kepulan menutup jalan, dsb)...",
            value="Kobaran api terlihat membesar di lahan gambut kering dekat parit batas desa. Asap pekat mulai mengarah ke rumah penduduk dan mengganggu jarak pandang.",
            height=110
        )

        submitted = st.form_submit_button("🚀 Kirim Laporan ke Pusat Komando IGNIS", use_container_width=True)

    if submitted:
        # Validasi input
        if not nama_pelapor.strip() or not lokasi.strip() or not deskripsi.strip():
            st.error("⚠️ Mohon lengkapi Nama Pelapor, Lokasi, dan Deskripsi Kejadian.")
            return

        is_valid_coord, coord_err = validate_coordinates(lat_input, lon_input)
        if not is_valid_coord:
            st.error(f"❌ Koordinat tidak valid: {coord_err}. Pastikan berada di dalam wilayah Indonesia.")
            return

        cleaned_desc = clean_text(deskripsi)
        cleaned_lokasi = clean_text(lokasi)

        # Siapkan payload laporan sementara
        temp_report = {
            "tanggal_lapor": tanggal_lapor,
            "nama_pelapor": clean_text(nama_pelapor),
            "kontak_pelapor": clean_text(kontak_pelapor),
            "lokasi": cleaned_lokasi,
            "kabupaten": clean_text(kabupaten),
            "provinsi": clean_text(provinsi),
            "latitude": lat_input,
            "longitude": lon_input,
            "deskripsi": cleaned_desc,
            "keparahan": keparahan,
            "tipe_lahan": tipe_lahan,
            "jarak_pemukiman_km": jarak_km,
            "luas_estimasi_ha": luas_ha,
            "bukti_url": bukti_url,
            "is_simulated": 0
        }

        # 1. Jalankan Verifikasi Sistem (Duplikasi Spasio-Temporal)
        existing_df = get_all_laporan(include_simulated=True)
        existing_list = existing_df.to_dict(orient="records") if not existing_df.empty else []
        verif_result = run_system_verification(temp_report, existing_list)

        temp_report["status_verifikasi_sistem"] = verif_result["system_status"]
        temp_report["jumlah_laporan_serupa"] = verif_result["cluster_count"]
        temp_report["status_verifikasi_petugas"] = "Menunggu Verifikasi"
        temp_report["catatan_petugas"] = "Laporan baru masuk melalui portal masyarakat, menunggu investigasi petugas posko."

        # 2. Hitung AI Risk Scoring (Explainable AI)
        score_res = calculate_risk_score(temp_report)
        temp_report["skor_prioritas"] = score_res["total_skor"]
        temp_report["label_prioritas"] = score_res["label"]
        temp_report["alasan_skor"] = score_res["narasi_xai"]

        # 3. Simpan ke SQLite
        new_id = insert_laporan(temp_report)

        st.success(f"🎉 Laporan Berhasil Diterima dan Disimpan ke Sistem! (Kode: {temp_report.get('kode_laporan', f'ID-{new_id}')})")

        # Tampilkan Hasil Penilaian Otomatis Instan
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.markdown(f"""
            <div class="ignis-card" style="text-align: center; border: 2px solid {score_res['badge_color']};">
                <div style="font-size: 13px; color: #A0AAB2;">SKOR PRIORITAS AI</div>
                <div style="font-size: 42px; font-weight: bold; color: {score_res['badge_color']}; margin: 8px 0;">
                    {score_res['total_skor']}
                </div>
                <div style="background-color: {score_res['badge_color']}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; display: inline-block;">
                    {score_res['label']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with res_col2:
            st.markdown(f"""
            <div class="ignis-card">
                <div style="font-size: 14px; font-weight: bold; color: #FFFFFF; margin-bottom: 6px;">
                    🛡️ Status Verifikasi Sistem: <span style="color: #00B4D8;">{verif_result['system_status']}</span>
                </div>
                <p style="font-size: 13px; color: #E0E1DD; line-height: 1.5; margin-bottom: 8px;">
                    {score_res['narasi_xai']}
                </p>
                <div style="font-size: 12px; color: #FFD166; font-weight: bold;">
                    Rekomendasi Respons: {score_res['rekomendasi_aksi']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if verif_result["is_duplicate"]:
            st.info(f"ℹ️ Sistem mendeteksi **{len(verif_result['duplicates'])} laporan serupa** dalam radius < 3.5 km. Laporan ini otomatis dikelompokkan ke dalam klaster insiden yang sama.")
