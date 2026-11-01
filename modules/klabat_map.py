"""
Modul Peta Geospasial Khusus Kawasan Gunung Klabat, Minahasa Utara.
Fokus pada jalur pendakian, kawasan wisata Kaki Dian, dan lereng desa di seputaran Klabat.
"""

import folium
import pandas as pd
from typing import Optional

PRIORITY_COLOR_MAP = {
    "Kritis": "#D90429",   # Merah tegas
    "Tinggi": "#F77F00",   # Oranye
    "Sedang": "#FCBF49",   # Kuning
    "Rendah": "#2A9D8F"    # Hijau
}

def render_klabat_folium_map(df: pd.DataFrame, selected_id: Optional[int] = None) -> folium.Map:
    """
    Membuat peta interaktif Gunung Klabat, Minahasa Utara.
    Pusat koordinat: Puncak Gunung Klabat (1.4650, 124.9900).
    """
    center_lat = 1.4650
    center_lon = 124.9900
    zoom = 13

    if selected_id and not df.empty:
        sel_row = df[df["id"] == selected_id]
        if not sel_row.empty:
            center_lat = float(sel_row.iloc[0]["latitude"])
            center_lon = float(sel_row.iloc[0]["longitude"])
            zoom = 14

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Tambahkan layer kontur / terrain
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Peta Topografi / Kontur Gunung Klabat"
    ).add_to(m)

    # Pin Puncak Gunung Klabat sebagai patokan utama
    folium.Marker(
        location=[1.4658, 124.9935],
        popup="<b>Puncak Gunung Klabat (1.995 mdpl)</b><br>Titik tertinggi Sulawesi Utara",
        tooltip="Puncak Gunung Klabat (1.995 mdpl)",
        icon=folium.Icon(color="darkblue", icon="info-sign")
    ).add_to(m)

    # Pin Kaki Dian sebagai patokan wisata utama
    folium.Marker(
        location=[1.4365, 124.9820],
        popup="<b>Kawasan Wisata Kaki Dian, Airmadidi</b>",
        tooltip="Kawasan Wisata Kaki Dian (Airmadidi)",
        icon=folium.Icon(color="blue", icon="bookmark")
    ).add_to(m)

    # Tambahkan titik-titik laporan kebakaran
    for _, r in df.iterrows():
        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except Exception:
            continue

        label_prio = str(r.get("label_prioritas", "Sedang"))
        color = PRIORITY_COLOR_MAP.get(label_prio, "#FCBF49")
        kode = r.get("kode_laporan", "KLB")
        area = r.get("lokasi_area", "Gunung Klabat")
        pelapor = r.get("nama_user", "Warga")
        skor = r.get("skor_prioritas", 50.0)
        status = r.get("status_penanganan", "Menunggu Penanganan")
        gmaps = r.get("link_lokasi", f"https://www.google.com/maps?q={lat},{lon}")

        is_resolved = (status in ["Sudah Diatasi", "Selesai / Padam"])
        marker_color = "#10B981" if is_resolved else color
        badge_header = f"SUDAH DIATASI" if is_resolved else f"Prioritas {label_prio} ({skor:.1f})"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 230px; line-height: 1.4;">
            <div style="background-color: {marker_color}; color: #fff; padding: 4px 8px; font-weight: bold; border-radius: 3px;">
                {kode} - {badge_header}
            </div>
            <div style="padding: 6px 2px;">
                <b>Lokasi:</b> {area}<br>
                <b>Pelapor:</b> {pelapor}<br>
                <b>Status:</b> <span style="font-weight: bold; color: {'#10B981' if is_resolved else '#F59E0B'};">{status}</span><br>
                <hr style="margin: 6px 0; border: none; border-top: 1px solid #ddd;">
                <a href="{gmaps}" target="_blank" style="color: #0077B6; font-weight: bold;">Buka Google Maps</a>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=9 if label_prio in ["Kritis", "Tinggi"] and not is_resolved else 6,
            color=marker_color,
            weight=2,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{kode}: {area} | Status: {status}"
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    return m
