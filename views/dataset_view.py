"""
Dataset & Preprocessing View for IGNIS.
Menangani manajemen dataset simulasi (>=100 data) vs data nyata masyarakat,
evaluasi kualitas data (completeness, koordinat valid, duplikasi),
serta antarmuka upload file CSV dengan pipeline preprocessing sebelum vs sesudah.
"""

import streamlit as st
import pandas as pd
import os
from database.db_manager import get_all_laporan, get_connection
from modules.preprocessing import preprocess_dataframe, evaluate_dataset_quality
from data.generate_simulation_data import save_and_seed_database, generate_dataset

def render_dataset_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">📁 Manajemen Dataset & Pipeline Preprocessing</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Audit kualitas data, pembersihan teks otomatis, validasi geospasial,
            serta upload CSV dengan visualisasi komparasi sebelum dan sesudah preprocessing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)

    # 1. Metrik Kualitas Dataset Saat Ini
    st.markdown("### 📊 1. Evaluasi Kualitas Dataset Aktif")
    if not df.empty:
        quality = evaluate_dataset_quality(df)
        sim_count = int((df["is_simulated"] == 1).sum()) if "is_simulated" in df.columns else 0
        real_count = len(df) - sim_count

        q1, q2, q3, q4 = st.columns(4)
        with q1:
            st.metric("Total Data di SQLite", f"{len(df)} Baris", f"{real_count} data masyarakat")
        with q2:
            st.metric("Completeness Score", f"{quality.get('completeness_score', 0)}%", "Kelengkapan atribut")
        with q3:
            st.metric("Validitas Koordinat RI", f"{quality.get('coord_validity_ratio', 0)}%", "Dalam BBox Indonesia")
        with q4:
            st.metric("Duplikasi Koordinat", f"{quality.get('duplicate_coordinates', 0)}", "Klaster spasial")
    else:
        st.warning("Database masih kosong. Gunakan tombol 'Inisialisasi Data Simulasi' di bawah.")

    st.markdown("---")

    # 2. Tab Data Simulasi vs Data Nyata
    st.markdown("### 📋 2. Penjelajah Data: Simulasi vs Nyata Masyarakat")
    tab_sim, tab_real = st.tabs(["🧪 Data Simulasi Karhutla (Hotspot RI)", "👤 Data Nyata Laporan Masyarakat"])

    with tab_sim:
        sim_df = df[df["is_simulated"] == 1] if not df.empty and "is_simulated" in df.columns else pd.DataFrame()
        st.write(f"Menampilkan **{len(sim_df)} data simulasi** yang tersebar di Riau, Sumsel, Jambi, Kalbar, Kalteng, Kalsel, dan Jatim:")
        if not sim_df.empty:
            st.dataframe(sim_df.head(25), use_container_width=True, hide_index=True)
            csv_bytes = sim_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Unduh Dataset Simulasi (CSV)",
                data=csv_bytes,
                file_name="ignis_dataset_simulasi.csv",
                mime="text/csv"
            )

    with tab_real:
        real_df = df[df["is_simulated"] == 0] if not df.empty and "is_simulated" in df.columns else pd.DataFrame()
        st.write(f"Menampilkan **{len(real_df)} laporan nyata** yang diinput melalui formulir pelaporan masyarakat:")
        if not real_df.empty:
            st.dataframe(real_df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada laporan langsung dari masyarakat. Coba buat laporan baru melalui menu **'Pelaporan Masyarakat'**.")

    st.markdown("---")

    # 3. Fitur Upload CSV & Pipeline Preprocessing
    st.markdown("### 📤 3. Pipeline Preprocessing Data Eksternal (Upload CSV)")
    st.caption("Unggah file CSV berisi data laporan mentah untuk dibersihkan, dinormalisasi, dan divalidasi koordinatnya secara otomatis.")

    uploaded_file = st.file_uploader("Pilih file CSV laporan karhutla:", type=["csv"])

    if uploaded_file is not None:
        try:
            raw_upload_df = pd.read_csv(uploaded_file)
            st.markdown("#### 📄 Data Mentah Sebelum Preprocessing (Raw Input):")
            st.dataframe(raw_upload_df.head(5), use_container_width=True)

            if st.button("⚙️ Jalankan Preprocessing Pipeline", type="primary"):
                with st.spinner("Memproses pembersihan teks, validasi geografis, dan normalisasi..."):
                    cleaned_df, stats = preprocess_dataframe(raw_upload_df)

                    st.success("✅ Preprocessing Selesai Dijalankan!")

                    # Ringkasan statistik perbaikan
                    st.markdown("##### 📈 Ringkasan Metrik Perbaikan:")
                    s1, s2, s3 = st.columns(3)
                    with s1:
                        st.metric("Nilai Hilang Diimputasi", f"{stats['missing_values_imputed']}")
                    with s2:
                        st.metric("Teks Dibersihkan", f"{stats['text_cleaned_count']}")
                    with s3:
                        st.metric("Koordinat Anomali Dideteksi", f"{stats['invalid_coords_flagged']}")

                    st.markdown("#### ✨ Data Setelah Preprocessing:")
                    st.dataframe(cleaned_df.head(5), use_container_width=True)

                    # Tombol simpan ke database
                    if st.button("💾 Simpan Data Hasil Preprocessing ke Database SQLite"):
                        conn = get_connection()
                        # Tambahkan kolom created_at dan is_simulated jika belum ada
                        cleaned_df["is_simulated"] = 1
                        from datetime import datetime
                        cleaned_df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Pastikan kolom sesuai
                        cleaned_df.to_sql("laporan", conn, if_exists="append", index=False)
                        conn.close()
                        st.success(f"Berhasil mengimpor {len(cleaned_df)} data baru ke database SQLite!")
                        st.rerun()

        except Exception as e:
            st.error(f"Gagal memproses file CSV: {str(e)}")

    st.markdown("---")

    # 4. Re-seeding Action
    st.markdown("### 🔄 4. Opsi Penyetelan Ulang Database")
    if st.button("⚠️ Re-generate & Re-seed Dataset Simulasi (115+ Kasus)", help="Menghasilkan ulang dataset simulasi awal"):
        with st.spinner("Membuat ulang dataset simulasi..."):
            save_and_seed_database()
            st.success("Dataset simulasi berhasil dibuat ulang dan disinkronkan ke SQLite!")
            st.rerun()
