"""
Peta Interaktif View for IGNIS using Folium & streamlit-folium.
Visualisasi persebaran spasial titik laporan kebakaran hutan dan lahan di seluruh Indonesia,
dilengkapi kontrol layer heatmap kepadatan, filter prioritas risiko, dan popup detail insiden.
"""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from database.db_manager import get_all_laporan
from modules.geo_map import create_ignis_map

def render_peta_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">🗺️ Peta Interaktif Sebaran Karhutla</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Pantau sebaran titik api, klaster kejadian, radius ancaman, dan konsentrasi kebakaran lahan secara geospasial real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)
    if df.empty:
        st.warning("Belum ada data laporan untuk divisualisasikan pada peta.")
        return

    # Filter kontrol horizontal
    f1, f2, f3 = st.columns([1.5, 1.5, 1.2])
    with f1:
        prio_choice = st.selectbox(
            "Filter Prioritas Risiko:",
            ["Semua Prioritas", "Kritis", "Tinggi", "Sedang", "Rendah"]
        )
    with f2:
        petugas_choice = st.selectbox(
            "Filter Verifikasi Petugas:",
            ["Semua Status", "Terverifikasi Valid", "Menunggu Verifikasi", "Perlu Investigasi Lapangan", "Ditolak / Palsu"]
        )
    with f3:
        st.write("")
        st.write("")
        show_heatmap = st.checkbox("Aktifkan Layer HeatMap", value=True)

    # Buat peta Folium
    folium_map = create_ignis_map(
        df,
        filter_label=prio_choice,
        filter_petugas=petugas_choice,
        show_heatmap=show_heatmap
    )

    # Render di Streamlit dengan lebar kontainer
    st_folium(folium_map, width="100%", height=560, returned_objects=[])

    # Keterangan Legenda Peta Modern
    st.markdown("""
    <div class="ignis-card" style="margin-top: 15px;">
        <div style="font-weight: bold; font-size: 13px; color: #FFFFFF; margin-bottom: 8px;">
            📌 LEGENDA SIMBOLISASI RISIKO IGNIS:
        </div>
        <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 12px;">
            <div><span style="color: #E63946; font-size: 16px;">●</span> <b>Kritis (Skor ≥ 75):</b> Api massif / bahaya nyawa / dekat pemukiman (< 300m)</div>
            <div><span style="color: #F4A261; font-size: 16px;">●</span> <b>Tinggi (Skor 55 - 74):</b> Api cepat merambat di lahan rentan / sawit</div>
            <div><span style="color: #E9C46A; font-size: 16px;">●</span> <b>Sedang (Skor 35 - 54):</b> Titik api terisolasi / semak belukar</div>
            <div><span style="color: #2A9D8F; font-size: 16px;">●</span> <b>Rendah (Skor < 35):</b> Sisa pembakaran / titik panas kecil</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
