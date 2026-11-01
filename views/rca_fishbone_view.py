"""
Root Cause Analysis (5 Whys) & Ishikawa Fishbone Diagram View for IGNIS.
Menerapkan metodologi investigasi sebab-akibat terstruktur untuk mengungkap akar permasalahan karhutla
dan memetakan faktor Manusia, Lingkungan, Cuaca, Infrastruktur, dan Penanganan.
"""

import streamlit as st
import pandas as pd
from database.db_manager import get_all_laporan, get_laporan_by_id, insert_rca, get_rca_by_laporan_id
from modules.rca import generate_5whys_analysis, RCA_SCENARIOS
from modules.fishbone import get_fishbone_factors, render_fishbone_plotly

def render_rca_fishbone_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">🔬 Investigasi Kausalitas: 5 Whys & Diagram Fishbone</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Metodologi investigasi akar masalah sistemik (5 Whys) dan pemetaan diagram tulang ikan (Ishikawa)
            untuk membedakan fakta terverifikasi empiris dengan dugaan awal di lapangan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)
    if df.empty:
        st.warning("Belum ada data laporan untuk diinvestigasi.")
        return

    # Pemilihan Laporan yang akan dianalisis
    options = {f"{r['kode_laporan']} - {r['lokasi']} ({r['keparahan']}, {r['tipe_lahan']})": r["id"] for _, r in df.iterrows()}
    sel_label = st.selectbox("Pilih Kasus Kejadian Karhutla untuk Investigasi:", list(options.keys()))
    sel_id = options[sel_label]
    report = get_laporan_by_id(sel_id)

    if not report:
        st.error("Data tidak ditemukan.")
        return

    # Informasi Laporan Terpilih
    st.markdown(f"""
    <div class="ignis-card" style="margin-bottom: 15px;">
        <div style="font-size: 14px; font-weight: bold; color: #FFFFFF;">
            Kasus: <span style="color: #00B4D8;">{report['kode_laporan']}</span> | Lokasi: {report['lokasi']} ({report['kabupaten']}, {report['provinsi']})
        </div>
        <div style="font-size: 12px; color: #A0AAB2; margin-top: 4px;">
            Tipe Lahan: <b>{report['tipe_lahan']}</b> | Jarak Pemukiman: <b>{report['jarak_pemukiman_km']} km</b> | Status Petugas: <b>{report['status_verifikasi_petugas']}</b>
        </div>
        <div style="font-size: 12px; color: #E0E1DD; margin-top: 6px; font-style: italic;">
            "{report['deskripsi']}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_rca, tab_fishbone = st.tabs(["📌 Analisis Akar Masalah (Metode 5 Whys)", "🐟 Diagram Tulang Ikan (Ishikawa Fishbone)"])

    # ==================== TAB 1: 5 WHYS METHOD ====================
    with tab_rca:
        st.markdown("### 🔍 Rantai Investigasi Kausalitas 5 Whys")
        st.caption("Penalaran bertahap dari gejala permukaan menuju kelemahan mendasar pada level regulasi, hidrologi, atau operasional.")

        # Ambil atau generate 5 Whys
        existing_rca = get_rca_by_laporan_id(report["id"])
        auto_rca = generate_5whys_analysis(report)

        st.markdown(f"**Topik Analisis Otomatis:** *{auto_rca['title']}*")

        with st.form("form_5whys"):
            w1 = st.text_area("Why 1: Gejala Permukaan Langsung (Direct Symptom):", value=existing_rca["why1"] if existing_rca else auto_rca["why1"], height=70)
            w2 = st.text_area("Why 2: Kondisi Fisik Lapangan (Physical Condition):", value=existing_rca["why2"] if existing_rca else auto_rca["why2"], height=70)
            w3 = st.text_area("Why 3: Kegagalan Infrastruktur / Fasilitas (Infrastructure Failure):", value=existing_rca["why3"] if existing_rca else auto_rca["why3"], height=70)
            w4 = st.text_area("Why 4: Kelemahan Operasional / Pengawasan (Operational Oversight):", value=existing_rca["why4"] if existing_rca else auto_rca["why4"], height=70)
            w5 = st.text_area("Why 5: Akar Masalah Sistemik & Regulasi (Systemic Root Cause):", value=existing_rca["why5"] if existing_rca else auto_rca["why5"], height=75)

            simpan_rca = st.form_submit_button("💾 Simpan Hasil Analisis 5 Whys ke Database", use_container_width=True)

        if simpan_rca:
            rca_data = {
                "laporan_id": report["id"],
                "why1": w1,
                "why2": w2,
                "why3": w3,
                "why4": w4,
                "why5": w5,
                "root_cause_summary": w5
            }
            insert_rca(rca_data)
            st.success("✅ Rekaman Root Cause Analysis (5 Whys) berhasil diperbarui dan disimpan ke database SQLite!")

    # ==================== TAB 2: FISHBONE DIAGRAM ====================
    with tab_fishbone:
        st.markdown("### 🐟 Pemetaan Faktor Penyebab (Diagram Ishikawa)")
        st.caption("Klasifikasi faktor ke dalam 5 cabang tulang ikan dengan pembedaan tegas antara fakta terverifikasi dan dugaan sementara.")

        factors = get_fishbone_factors(report)

        # Plotly Diagram
        fish_fig = render_fishbone_plotly(factors, f"Fishbone Diagram: {report['kode_laporan']} - {report['tipe_lahan']}")
        st.plotly_chart(fish_fig, use_container_width=True)

        st.markdown("#### 📋 Matriks Verifikasi Bukti Faktor Kausalitas")
        
        # Render tabel per kategori dengan styling status
        cat_tabs = st.tabs(["👤 Manusia", "🌿 Lingkungan", "☀️ Cuaca", "🏗️ Infrastruktur", "🚒 Penanganan"])
        cat_names = ["Manusia", "Lingkungan", "Cuaca", "Infrastruktur", "Penanganan"]

        for i, cat in enumerate(cat_names):
            with cat_tabs[i]:
                cat_factors = factors.get(cat, [])
                for f in cat_factors:
                    is_verif = (f["status"] == "Terverifikasi")
                    badge_color = "#2ECC71" if is_verif else "#F39C12"
                    badge_label = "TERVERIFIKASI (DATA EMPIRIS)" if is_verif else "DUGAAN (HIPOTESIS LAPANGAN)"

                    st.markdown(f"""
                    <div style="background-color: #0F1C3F; border-left: 4px solid {badge_color}; padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: bold; color: #FFFFFF; font-size: 13px;">{f['faktor']}</span>
                            <span style="background-color: {badge_color}; color: #FFFFFF; font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 8px;">
                                {badge_label}
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #90E0EF; margin-top: 4px;">
                            Dasar Bukti: {f['keterangan']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
