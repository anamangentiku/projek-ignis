"""
Dashboard View for IGNIS.
Menampilkan statistik laporan real-time, grafik tren temporal, sebaran spasial provinsi,
kategori tipe lahan, dan ringkasan prioritas risiko kejadian.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db_manager import get_all_laporan

def render_dashboard_view():
    st.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">📊 Dashboard Intelijen & Pemantauan Karhutla</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Ringkasan analitik real-time laporan masyarakat, status verifikasi satgas, dan sebaran risiko karhutla di Indonesia.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Filter tipe data
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        data_mode = st.radio(
            "Filter Sumber Data:",
            ["Semua Laporan (Simulasi & Masyarakat)", "Hanya Laporan Nyata Masyarakat", "Hanya Data Simulasi"],
            horizontal=True
        )

    # Ambil data dari SQLite
    all_df = get_all_laporan(include_simulated=True)
    if all_df.empty:
        st.warning("Database laporan masih kosong. Silakan masuk ke tab **Dataset & Preprocessing** untuk mengisi data simulasi.")
        return

    if data_mode == "Hanya Laporan Nyata Masyarakat":
        df = all_df[all_df["is_simulated"] == 0].copy()
    elif data_mode == "Hanya Data Simulasi":
        df = all_df[all_df["is_simulated"] == 1].copy()
    else:
        df = all_df.copy()

    total_laporan = len(df)
    kritis_count = int((df["label_prioritas"] == "Kritis").sum()) if "label_prioritas" in df.columns else 0
    tinggi_count = int((df["label_prioritas"] == "Tinggi").sum()) if "label_prioritas" in df.columns else 0
    terverifikasi_valid = int((df["status_verifikasi_petugas"] == "Terverifikasi Valid").sum()) if "status_verifikasi_petugas" in df.columns else 0
    duplikat_sistem = int(df["status_verifikasi_sistem"].str.contains("Duplikat", na=False).sum()) if "status_verifikasi_sistem" in df.columns else 0

    # KPI Metrics Cards dengan styling modern
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(f"""
        <div class="ignis-card" style="border-top: 4px solid #00B4D8;">
            <div style="font-size: 12px; color: #90E0EF; font-weight: bold;">TOTAL LAPORAN</div>
            <div style="font-size: 28px; font-weight: bold; color: #FFFFFF; margin: 4px 0;">{total_laporan}</div>
            <div style="font-size: 11px; color: #A0AAB2;">Kejadian terdata</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="ignis-card" style="border-top: 4px solid #E63946;">
            <div style="font-size: 12px; color: #FFAAA6; font-weight: bold;">PRIORITAS KRITIS</div>
            <div style="font-size: 28px; font-weight: bold; color: #E63946; margin: 4px 0;">{kritis_count}</div>
            <div style="font-size: 11px; color: #A0AAB2;">Butuh helikopter & evakuasi</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="ignis-card" style="border-top: 4px solid #F4A261;">
            <div style="font-size: 12px; color: #FFD166; font-weight: bold;">PRIORITAS TINGGI</div>
            <div style="font-size: 28px; font-weight: bold; color: #F4A261; margin: 4px 0;">{tinggi_count}</div>
            <div style="font-size: 11px; color: #A0AAB2;">Pengerahan pemadam darat</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="ignis-card" style="border-top: 4px solid #2ECC71;">
            <div style="font-size: 12px; color: #99E2B4; font-weight: bold;">TERVERIFIKASI PETUGAS</div>
            <div style="font-size: 28px; font-weight: bold; color: #2ECC71; margin: 4px 0;">{terverifikasi_valid}</div>
            <div style="font-size: 11px; color: #A0AAB2;">Tervalidasi di lapangan</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="ignis-card" style="border-top: 4px solid #9B5DE5;">
            <div style="font-size: 12px; color: #D8BBFF; font-weight: bold;">KLASTER DUPLIKAT</div>
            <div style="font-size: 28px; font-weight: bold; color: #9B5DE5; margin: 4px 0;">{duplikat_sistem}</div>
            <div style="font-size: 11px; color: #A0AAB2;">Laporan kejadian serupa</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Baris Grafik 1: Distribusi Prioritas Risiko (Donut) & Sebaran Wilayah Provinsi (Bar)
    g_col1, g_col2 = st.columns([1, 1])

    with g_col1:
        st.markdown("#### 🎯 Distribusi Kategori Prioritas Risiko")
        if "label_prioritas" in df.columns and not df.empty:
            prio_counts = df["label_prioritas"].value_counts().reset_index()
            prio_counts.columns = ["Prioritas", "Jumlah"]
            color_map = {
                "Kritis": "#E63946",
                "Tinggi": "#F4A261",
                "Sedang": "#E9C46A",
                "Rendah": "#2A9D8F",
                "Belum Dihitung": "#6C757D"
            }
            fig_donut = px.pie(
                prio_counts,
                names="Prioritas",
                values="Jumlah",
                hole=0.55,
                color="Prioritas",
                color_discrete_map=color_map
            )
            fig_donut.update_layout(
                plot_bgcolor="#0A1128",
                paper_bgcolor="#070D1F",
                font=dict(color="#FFFFFF"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Data prioritas belum tersedia.")

    with g_col2:
        st.markdown("#### 📍 Sebaran Laporan per Provinsi")
        if "provinsi" in df.columns and not df.empty:
            prov_counts = df["provinsi"].value_counts().reset_index()
            prov_counts.columns = ["Provinsi", "Jumlah"]
            fig_bar = px.bar(
                prov_counts,
                x="Jumlah",
                y="Provinsi",
                orientation="h",
                color="Jumlah",
                color_continuous_scale=["#0077B6", "#00B4D8", "#F4A261", "#E63946"]
            )
            fig_bar.update_layout(
                plot_bgcolor="#0A1128",
                paper_bgcolor="#070D1F",
                font=dict(color="#FFFFFF"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=320,
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Baris Grafik 2: Kategori Tipe Lahan & Status Verifikasi
    g_col3, g_col4 = st.columns([1, 1])

    with g_col3:
        st.markdown("#### 🌿 Proporsi Kejadian Berdasarkan Tipe Lahan")
        if "tipe_lahan" in df.columns and not df.empty:
            land_counts = df["tipe_lahan"].value_counts().reset_index()
            land_counts.columns = ["Tipe Lahan", "Jumlah"]
            fig_land = px.pie(
                land_counts,
                names="Tipe Lahan",
                values="Jumlah",
                color_discrete_sequence=["#8B5E3C", "#2D6A4F", "#D4A373", "#52B788", "#74C69D"]
            )
            fig_land.update_layout(
                plot_bgcolor="#0A1128",
                paper_bgcolor="#070D1F",
                font=dict(color="#FFFFFF"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_land, use_container_width=True)

    with g_col4:
        st.markdown("#### 🛡️ Komparasi Verifikasi Sistem vs Petugas")
        if not df.empty and "status_verifikasi_petugas" in df.columns:
            verif_counts = df["status_verifikasi_petugas"].value_counts().reset_index()
            verif_counts.columns = ["Status Petugas", "Jumlah"]
            fig_verif = px.bar(
                verif_counts,
                x="Status Petugas",
                y="Jumlah",
                color="Status Petugas",
                color_discrete_map={
                    "Terverifikasi Valid": "#2ECC71",
                    "Menunggu Verifikasi": "#F39C12",
                    "Ditolak / Palsu": "#E74C3C",
                    "Perlu Investigasi Lapangan": "#3498DB"
                }
            )
            fig_verif.update_layout(
                plot_bgcolor="#0A1128",
                paper_bgcolor="#070D1F",
                font=dict(color="#FFFFFF"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=320,
                showlegend=False
            )
            st.plotly_chart(fig_verif, use_container_width=True)

    # Tabel Laporan Kejadian Terbaru
    st.markdown("---")
    st.markdown("#### 📋 10 Laporan Terkini di Lapangan")
    preview_cols = ["kode_laporan", "tanggal_lapor", "lokasi", "provinsi", "keparahan", "label_prioritas", "skor_prioritas", "status_verifikasi_petugas", "is_simulated"]
    cols_exist = [c for c in preview_cols if c in df.columns]
    
    display_df = df[cols_exist].head(10).copy()
    if "is_simulated" in display_df.columns:
        display_df["Tipe"] = display_df["is_simulated"].apply(lambda x: "Simulasi" if x == 1 else "Masyarakat")
        display_df.drop(columns=["is_simulated"], inplace=True)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
