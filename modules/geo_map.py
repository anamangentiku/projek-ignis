"""
Interactive Geospatial Map Module for IGNIS using Folium.
Memvisualisasikan persebaran laporan kebakaran hutan dan lahan di seluruh Indonesia
dengan penandaan multi-kategori, radius dampak, layer heatmap, dan popup detail informatif.
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
from typing import Optional

# Palet warna status prioritas risiko
PRIORITY_COLORS = {
    "Kritis": "#E63946",   # Merah cerah
    "Tinggi": "#F4A261",   # Oranye
    "Sedang": "#E9C46A",   # Kuning emas
    "Rendah": "#2A9D8F"    # Hijau zamrud
}

def create_ignis_map(
    df: pd.DataFrame, 
    filter_label: Optional[str] = None, 
    filter_petugas: Optional[str] = None,
    show_heatmap: bool = True
) -> folium.Map:
    """
    Membuat objek peta Folium interaktif berbasis data laporan.
    """
    # Filter data jika diminta
    filtered_df = df.copy()
    if filter_label and filter_label != "Semua Prioritas":
        filtered_df = filtered_df[filtered_df["label_prioritas"] == filter_label]
    if filter_petugas and filter_petugas != "Semua Status":
        filtered_df = filtered_df[filtered_df["status_verifikasi_petugas"] == filter_petugas]

    # Titik tengah Indonesia (Sekitar Selat Makassar / Kalimantan)
    center_lat = -0.7893
    center_lon = 113.9213
    zoom_start = 5

    if not filtered_df.empty:
        # Jika ada data, gunakan rata-rata posisi laporan sebagai pusat awal
        try:
            center_lat = float(filtered_df["latitude"].mean())
            center_lon = float(filtered_df["longitude"].mean())
            zoom_start = 6
        except Exception:
            pass

    # Inisialisasi peta dasar tema Dark Navy yang elegan
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Tambahkan alternatif layer satelit / dark mode
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/attributions'>CARTO</a>",
        name="Tema Dark Navy",
        control=True
    ).add_to(m)

    # Layer HeatMap untuk visualisasi kepadatan titik api
    if show_heatmap and not filtered_df.empty:
        heat_data = []
        for _, row in filtered_df.iterrows():
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                weight = 1.0
                if row.get("label_prioritas") == "Kritis":
                    weight = 2.5
                elif row.get("label_prioritas") == "Tinggi":
                    weight = 1.8
                heat_data.append([lat, lon, weight])
            except Exception:
                continue

        if heat_data:
            HeatMap(
                heat_data,
                name="Intensitas Karhutla (HeatMap)",
                radius=18,
                blur=14,
                max_zoom=10,
                min_opacity=0.35,
                gradient={0.2: "#2A9D8F", 0.5: "#E9C46A", 0.75: "#F4A261", 1.0: "#E63946"}
            ).add_to(m)

    # FeatureGroup untuk marker titik laporan
    marker_group = folium.FeatureGroup(name="Pin Laporan Kejadian").add_to(m)

    for _, row in filtered_df.iterrows():
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        except Exception:
            continue

        label_prio = str(row.get("label_prioritas", "Sedang"))
        color = PRIORITY_COLORS.get(label_prio, "#E9C46A")
        kode = row.get("kode_laporan", "IGNIS-N/A")
        lokasi = row.get("lokasi", "Tidak teridentifikasi")
        tgl = row.get("tanggal_lapor", "-")
        keparahan = row.get("keparahan", "Sedang")
        skor = row.get("skor_prioritas", 0.0)
        tipe_lahan = row.get("tipe_lahan", "Umum")
        status_petugas = row.get("status_verifikasi_petugas", "Menunggu Verifikasi")
        status_sistem = row.get("status_verifikasi_sistem", "Terverifikasi Otomatis")
        pelapor = row.get("nama_pelapor", "Masyarakat")
        deskripsi = str(row.get("deskripsi", ""))[:120] + "..."

        # HTML Popup berdesain modern dengan tema IGNIS
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 260px; color: #222;">
            <div style="background-color: {color}; color: white; padding: 6px 10px; border-radius: 4px; font-weight: bold;">
                🔥 {kode} | Prioritas: {label_prio} ({skor:.1f})
            </div>
            <div style="padding: 8px 4px;">
                <p style="margin: 4px 0;"><b>Lokasi:</b> {lokasi}</p>
                <p style="margin: 4px 0;"><b>Tipe Lahan:</b> {tipe_lahan}</p>
                <p style="margin: 4px 0;"><b>Waktu:</b> {tgl}</p>
                <p style="margin: 4px 0;"><b>Pelapor:</b> {pelapor}</p>
                <hr style="border: 0.5px solid #eee; margin: 6px 0;">
                <p style="margin: 4px 0;"><b>Verif Sistem:</b> <span style="color: #0077B6;">{status_sistem}</span></p>
                <p style="margin: 4px 0;"><b>Verif Petugas:</b> <span style="color: {'#2ECC71' if 'Valid' in status_petugas else '#E67E22'}; font-weight: bold;">{status_petugas}</span></p>
                <p style="margin: 6px 0; font-style: italic; color: #555;">"{deskripsi}"</p>
            </div>
        </div>
        """

        # CircleMarker dengan efek radius gelombang
        folium.CircleMarker(
            location=[lat, lon],
            radius=9 if label_prio in ["Kritis", "Tinggi"] else 7,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{kode} | Prioritas: {label_prio} ({skor:.1f}) - {lokasi}"
        ).add_to(marker_group)

    folium.LayerControl(position="topright").add_to(m)
    return m
