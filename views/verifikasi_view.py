"""
Verifikasi Laporan View for IGNIS.
Membedakan secara tegas verifikasi otomatis sistem (deteksi duplikasi, anomali koordinat, audit konsistensi)
dengan verifikasi manual petugas posko komando / investigasi lapangan.
"""

import streamlit as st
import pandas as pd
from database.db_manager import get_all_laporan, update_verifikasi_petugas, get_laporan_by_id
from modules.verifier import audit_report_consistency, check_spatial_temporal_duplicates

def render_verifikasi_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">🛡️ Pusat Verifikasi & Integritas Laporan</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Validasi multi-tingkat: Bedakan hasil analisis otomatis sistem dengan keputusan resmi petugas investigasi lapangan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)
    if df.empty:
        st.warning("Belum ada data laporan yang perlu diverifikasi.")
        return

    # Tab penyaringan status
    tab_filter = st.radio(
        "Kategori Peninjauan:",
        ["Semua Laporan", "Menunggu Verifikasi Petugas", "Terindikasi Duplikat (Klaster)", "Terverifikasi Valid", "Ditolak / Laporan Palsu"],
        horizontal=True
    )

    if tab_filter == "Menunggu Verifikasi Petugas":
        view_df = df[df["status_verifikasi_petugas"] == "Menunggu Verifikasi"].copy()
    elif tab_filter == "Terindikasi Duplikat (Klaster)":
        view_df = df[df["status_verifikasi_sistem"].str.contains("Duplikat", na=False)].copy()
    elif tab_filter == "Terverifikasi Valid":
        view_df = df[df["status_verifikasi_petugas"] == "Terverifikasi Valid"].copy()
    elif tab_filter == "Ditolak / Laporan Palsu":
        view_df = df[df["status_verifikasi_petugas"] == "Ditolak / Palsu"].copy()
    else:
        view_df = df.copy()

    st.markdown(f"**Menampilkan {len(view_df)} laporan** pada kategori *{tab_filter}*:")

    # Tabel ringkas dengan penandaan visual
    cols_to_show = ["id", "kode_laporan", "tanggal_lapor", "lokasi", "keparahan", "status_verifikasi_sistem", "status_verifikasi_petugas", "skor_prioritas"]
    st.dataframe(view_df[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🔍 Panel Evaluasi & Keputusan Petugas Posko")

    # Dropdown pemilihan laporan untuk ditindaklanjuti
    options = {f"{r['kode_laporan']} - {r['lokasi']} (Skor: {r['skor_prioritas']})": r["id"] for _, r in view_df.iterrows()}
    if not options:
        st.info("Tidak ada laporan pada filter ini.")
        return

    selected_label = st.selectbox("Pilih Laporan untuk Ditinjau:", list(options.keys()))
    selected_id = options[selected_label]
    report = get_laporan_by_id(selected_id)

    if not report:
        st.error("Data laporan tidak ditemukan.")
        return

    # Tampilkan Dua Sisi: Verifikasi Otomatis Sistem vs Tindakan Petugas
    col_sys, col_officer = st.columns([1.2, 1])

    with col_sys:
        st.markdown("""
        <div class="ignis-card">
            <h4 style="margin: 0 0 10px 0; color: #00B4D8;">🤖 Hasil Audit Otomatis Sistem</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Jalankan audit real-time
        audit = audit_report_consistency(report)
        existing_list = [r for _, r in df.iterrows() if r["id"] != report["id"]]
        is_dup, dups = check_spatial_temporal_duplicates(
            report["latitude"], report["longitude"], report["tanggal_lapor"], existing_list
        )

        st.write(f"**Status Sistem Saat Ini:** `{report.get('status_verifikasi_sistem')}`")
        st.write(f"**Validitas Koordinat:** {'✅ Valid di batas RI' if audit['coord_valid'] else '❌ Di luar batas wilayah RI'}")
        st.write(f"**Kelengkapan Bukti:** {'✅ Bukti terlampir' if audit['has_evidence'] else '⚠️ Tanpa bukti foto'}")
        
        if is_dup:
            st.warning(f"⚠️ **Deteksi Duplikasi Spasio-Temporal:** Terdapat {len(dups)} laporan serupa dalam radius < 3.5 km!")
            for d in dups[:3]:
                st.caption(f"• ID {d['kode_laporan']} oleh {d['pelapor']} (Jarak: {d['jarak_km']} km, Beda: {d['selisih_jam']} jam)")
        else:
            st.success("✅ **Laporan Tunggal / Unik:** Tidak terdeteksi duplikasi dalam radius 3.5 km.")

        if audit["warnings"]:
            st.info("ℹ️ **Peringatan Konsistensi:** " + "; ".join(audit["warnings"]))
        if audit["issues"]:
            st.error("❌ **Isu Validitas:** " + "; ".join(audit["issues"]))

        st.caption(f"Deskripsi Terlapor: \"{report.get('deskripsi')}\"")

    with col_officer:
        st.markdown("""
        <div class="ignis-card">
            <h4 style="margin: 0 0 10px 0; color: #2ECC71;">👮 Keputusan Petugas Lapangan / Posko</h4>
        </div>
        """, unsafe_allow_html=True)

        current_petugas = report.get("status_verifikasi_petugas", "Menunggu Verifikasi")
        st.write(f"Status Terkini: **{current_petugas}**")

        new_status = st.selectbox(
            "Perbarui Status Verifikasi Petugas:",
            ["Terverifikasi Valid", "Menunggu Verifikasi", "Perlu Investigasi Lapangan", "Ditolak / Palsu"],
            index=["Terverifikasi Valid", "Menunggu Verifikasi", "Perlu Investigasi Lapangan", "Ditolak / Palsu"].index(current_petugas) if current_petugas in ["Terverifikasi Valid", "Menunggu Verifikasi", "Perlu Investigasi Lapangan", "Ditolak / Palsu"] else 0
        )

        catatan_baru = st.text_area(
            "Catatan Investigasi / Temuan Lapangan:",
            value=report.get("catatan_petugas", ""),
            placeholder="Tuliskan temuan regu patroli darat, nomor personil pemantau, atau alasan penolakan..."
        )

        if st.button("💾 Simpan Keputusan Petugas", use_container_width=True):
            update_verifikasi_petugas(report["id"], new_status, catatan_baru)
            st.success(f"Status laporan {report['kode_laporan']} berhasil diperbarui menjadi '{new_status}'!")
            st.rerun()
