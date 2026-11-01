"""
Rekomendasi Mitigasi View for IGNIS.
Menyusun rekomendasi penanganan karhutla terstruktur (tindakan segera, instansi terkait, dasar pertimbangan, dan sumber daya)
menggunakan Google Gemini API atau Fallback Rule-Based Expert System dengan transparansi sumber.
"""

import streamlit as st
from database.db_manager import get_all_laporan, get_laporan_by_id, insert_mitigasi, get_mitigasi_by_laporan_id
from modules.scoring import calculate_risk_score
from modules.llm_service import generate_mitigation_recommendation

def render_mitigasi_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">📋 Rencana Rekomendasi Mitigasi Taktis</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Penyusunan rekomendasi penanganan berbasis AI dan regulasi operasional standar (SOP) lintas instansi
            (BNPB, Manggala Agni / KLHK, TNI, POLRI, BPBD, dan Dinas Kesehatan).
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)
    if df.empty:
        st.warning("Belum ada data laporan untuk disusun rencana mitigasinya.")
        return

    # Pemilihan Laporan
    options = {f"{r['kode_laporan']} - {r['lokasi']} ({r['keparahan']}, Skor: {r['skor_prioritas']})": r["id"] for _, r in df.iterrows()}
    sel_label = st.selectbox("Pilih Insiden Karhutla untuk Rencana Mitigasi:", list(options.keys()))
    sel_id = options[sel_label]
    report = get_laporan_by_id(sel_id)

    if not report:
        st.error("Data tidak ditemukan.")
        return

    score_info = calculate_risk_score(report)

    # Ringkasan Profil Kasus
    st.markdown(f"""
    <div class="ignis-card" style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 15px; font-weight: bold; color: #FFFFFF;">
                Laporan: <span style="color: #00B4D8;">{report['kode_laporan']}</span> ({report['lokasi']}, {report['kabupaten']})
            </span>
            <span style="background-color: {score_info['badge_color']}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                PRIORITAS {score_info['label'].upper()} ({score_info['total_skor']})
            </span>
        </div>
        <div style="font-size: 12px; color: #A0AAB2; margin-top: 6px;">
            Tipe Lahan: <b>{report['tipe_lahan']}</b> | Jarak Pemukiman: <b>{report['jarak_pemukiman_km']} km</b> | Estimasi Luas: <b>{report.get('luas_estimasi_ha', 1.0)} ha</b>
        </div>
        <div style="font-size: 12px; color: #E0E1DD; margin-top: 4px; font-style: italic;">
            Deskripsi: "{report['deskripsi']}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Periksa apakah ada rekomendasi yang sudah tersimpan
    existing_mitigasi = get_mitigasi_by_laporan_id(report["id"])

    btn_generate = st.button("⚡ Susun Rekomendasi Mitigasi Baru dengan AI", type="primary", use_container_width=True)

    mitigasi_data = None
    if btn_generate:
        with st.spinner("Menyusun rekomendasi mitigasi taktis berbasis SOP..."):
            mitigasi_data = generate_mitigation_recommendation(report, score_info)
            # Simpan ke DB
            insert_mitigasi({
                "laporan_id": report["id"],
                "tindakan_segera": "\n".join(mitigasi_data.get("tindakan_segera", [])),
                "instansi_terkait": str(mitigasi_data.get("instansi_terkait", [])),
                "dasar_pertimbangan": mitigasi_data.get("dasar_pertimbangan", ""),
                "sumber_rekomendasi": mitigasi_data.get("sumber_rekomendasi", "Sistem")
            })
            st.session_state[f"mitigasi_{report['id']}"] = mitigasi_data
    elif f"mitigasi_{report['id']}" in st.session_state:
        mitigasi_data = st.session_state[f"mitigasi_{report['id']}"]
    elif existing_mitigasi:
        # Gunakan dari database
        mitigasi_data = generate_mitigation_recommendation(report, score_info)

    if not mitigasi_data:
        st.info("Klik tombol di atas untuk menyusun rekomendasi mitigasi.")
        return

    # Badge Sumber Rekomendasi
    badge_bg = "#2ECC71" if not mitigasi_data.get("is_fallback") else "#E76F51"
    st.markdown(f"""
    <div style="margin-bottom: 12px; font-size: 12px; color: #E0E1DD;">
        Sumber Rekomendasi: <span style="background-color: {badge_bg}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">
            {mitigasi_data.get('sumber_rekomendasi', 'Sistem')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Tindakan Segera (0-6 Jam)
    st.markdown("#### 🚨 1. Tindakan Tanggap Darurat Segera (Fase 0 - 6 Jam)")
    for act in mitigasi_data.get("tindakan_segera", []):
        st.markdown(f"""
        <div style="background-color: #0F1C3F; border-left: 4px solid #E63946; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 13px; color: #FFFFFF;">
            • {act}
        </div>
        """, unsafe_allow_html=True)

    # 2. Tindakan Jangka Pendek & Panjang
    c_pendek, c_panjang = st.columns(2)
    with c_pendek:
        st.markdown("#### ⏳ 2. Tindakan Stabilisasi (1 - 7 Hari)")
        for act in mitigasi_data.get("tindakan_jangka_pendek", []):
            st.markdown(f"""
            <div style="background-color: #0F1C3F; border-left: 4px solid #F4A261; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 12px; color: #FFFFFF;">
                • {act}
            </div>
            """, unsafe_allow_html=True)

    with c_panjang:
        st.markdown("#### 🏛️ 3. Tindakan Pencegahan Jangka Panjang")
        for act in mitigasi_data.get("tindakan_jangka_panjang", []):
            st.markdown(f"""
            <div style="background-color: #0F1C3F; border-left: 4px solid #2A9D8F; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 12px; color: #FFFFFF;">
                • {act}
            </div>
            """, unsafe_allow_html=True)

    # 3. Instansi Terkait & Peran
    st.markdown("---")
    st.markdown("#### 👥 4. Pembagian Peran Instansi Penanggung Jawab")
    instansi_list = mitigasi_data.get("instansi_terkait", [])
    if isinstance(instansi_list, list):
        for inst in instansi_list:
            if isinstance(inst, dict):
                nama_inst = inst.get("instansi", "-")
                peran_inst = inst.get("peran", "-")
            else:
                nama_inst = str(inst)
                peran_inst = "Operasi dan dukungan teknis posko terpadu."

            st.markdown(f"""
            <div style="background-color: #070D1F; border: 1px solid #1D2D44; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 12px;">
                <b style="color: #90E0EF;">{nama_inst}:</b> <span style="color: #E0E1DD;">{peran_inst}</span>
            </div>
            """, unsafe_allow_html=True)

    # 4. Alokasi Sumber Daya Taktis
    st.markdown("#### 🚜 5. Alokasi Sumber Daya Taktis yang Disarankan")
    sumber_daya = mitigasi_data.get("alokasi_sumber_daya", [])
    if sumber_daya:
        cols = st.columns(len(sumber_daya)) if len(sumber_daya) <= 4 else st.columns(4)
        for idx, item in enumerate(sumber_daya):
            target_col = cols[idx % len(cols)]
            with target_col:
                st.markdown(f"""
                <div class="ignis-card" style="text-align: center; padding: 10px 4px; font-size: 12px; color: #FFD166;">
                    📦 {item}
                </div>
                """, unsafe_allow_html=True)

    # 5. Dasar Pertimbangan & SOP Hukum
    st.markdown("#### 📖 6. Dasar Analisis Spasial & Yuridis")
    st.info(mitigasi_data.get("dasar_pertimbangan", "Berdasarkan evaluasi spasial dan SOP KLHK/BNPB."))

    # Disclaimer Keputusan Hukum
    st.markdown("""
    <div style="background-color: rgba(230, 57, 70, 0.1); border: 1px solid #E63946; padding: 8px 12px; border-radius: 4px; margin-top: 15px; font-size: 11px; color: #FFAAA6;">
        ⚠️ <b>CATATAN PENTING & DISCLAIMER:</b> IGNIS adalah Sistem Pendukung Keputusan (Decision Support System) berbasis kecerdasan buatan.
        Rekomendasi di atas bersifat asistif dan tidak menggantikan wewenang Komandan Satuan Tugas (Dansatgas) Darat/Udara atau Surat Keputusan Status Tanggap Darurat resmi Kepala Daerah.
    </div>
    """, unsafe_allow_html=True)
