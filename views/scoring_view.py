"""
AI Risk Scoring & Explainable AI (XAI) View for IGNIS.
Menghitung skor prioritas risiko (0-100) menggunakan formula berbobot multi-kriteria yang transparan.
Menampilkan visualisasi kontribusi faktor, formula matematis, narasi penjelasan logis,
serta perbandingan sebelum dan sesudah analisis AI.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db_manager import get_all_laporan, get_laporan_by_id, update_scoring
from modules.scoring import calculate_risk_score

def render_scoring_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">🎯 AI Risk Scoring & Explainable AI (XAI)</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Sistem pendukung keputusan transparan: Setiap skor prioritas 0–100 memiliki dasar matematis,
            bobot terkalibrasi, serta penjelasan logis tanpa 'kotak hitam' (black box).
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_laporan(include_simulated=True)
    if df.empty:
        st.warning("Belum ada data laporan untuk dihitung skor risikonya.")
        return

    # Pemilihan Laporan
    options = {f"{r['kode_laporan']} - {r['lokasi']} ({r['keparahan']}, {r['tipe_lahan']})": r["id"] for _, r in df.iterrows()}
    sel_label = st.selectbox("Pilih Laporan untuk Evaluasi XAI:", list(options.keys()))
    sel_id = options[sel_label]
    report = get_laporan_by_id(sel_id)

    if not report:
        st.error("Data tidak ditemukan.")
        return

    # Hitung skor menggunakan engine XAI
    score_res = calculate_risk_score(report)
    breakdown = score_res["breakdown"]

    st.markdown("---")

    # Header Metric Skor
    m1, m2 = st.columns([1, 2])
    with m1:
        st.markdown(f"""
        <div class="ignis-card" style="text-align: center; border: 2px solid {score_res['badge_color']};">
            <div style="font-size: 13px; color: #A0AAB2; font-weight: bold;">SKOR PRIORITAS RISIKO</div>
            <div style="font-size: 54px; font-weight: bold; color: {score_res['badge_color']}; margin: 4px 0;">
                {score_res['total_skor']}<span style="font-size: 20px; color: #A0AAB2;">/100</span>
            </div>
            <div style="background-color: {score_res['badge_color']}; color: white; padding: 6px 18px; border-radius: 16px; font-weight: bold; font-size: 14px; display: inline-block;">
                PRIORITAS {score_res['label'].upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="ignis-card">
            <h4 style="margin: 0 0 8px 0; color: #FFFFFF;">📋 Rangkuman Keputusan Sistem</h4>
            <p style="font-size: 13px; color: #E0E1DD; line-height: 1.6; margin-bottom: 10px;">
                {score_res['narasi_xai']}
            </p>
            <div style="background: rgba(244, 162, 97, 0.15); border-left: 4px solid #F4A261; padding: 8px 12px; border-radius: 4px;">
                <div style="font-size: 11px; color: #FFD166; font-weight: bold;">TINDAKAN MITIGASI YANG DIREKOMENDASIKAN:</div>
                <div style="font-size: 13px; color: #FFFFFF; font-weight: 500;">{score_res['rekomendasi_aksi']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Formula Matematis Transparan (KaTeX Math rendering)
    with st.expander("📐 Lihat Formula Pembobotan Multi-Kriteria (XAI Mathematical Framework)", expanded=True):
        st.markdown(r"""
        $$\text{Skor Prioritas} = S_{\text{keparahan}} \,(30\%) + S_{\text{jarak\_pemukiman}} \,(25\%) + S_{\text{tipe\_lahan}} \,(20\%) + S_{\text{klaster\_laporan}} \,(15\%) + S_{\text{bukti\_kredibilitas}} \,(10\%) - \text{Penalti}$$
        
        *Setiap bobot dirancang selaras dengan Pedoman Pengendalian Karhutla KLHK dan BNPB untuk memastikan perlindungan jiwa warga dan preservasi ekosistem gambut.*
        """)

    # Visualisasi Rincian Kontribusi Faktor (Chart)
    c_chart, c_table = st.columns([1.2, 1])

    with c_chart:
        st.markdown("#### 📊 Kontribusi Poin per Komponen")
        chart_data = []
        for k, v in breakdown.items():
            chart_data.append({
                "Komponen": v["nama"],
                "Skor Didapat": v["skor_didapat"],
                "Bobot Maksimal": v["bobot_maks"]
            })
        cdf = pd.DataFrame(chart_data)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=cdf["Komponen"],
            x=cdf["Skor Didapat"],
            orientation="h",
            name="Skor Diperoleh",
            marker=dict(color="#00B4D8")
        ))
        fig_bar.add_trace(go.Bar(
            y=cdf["Komponen"],
            x=cdf["Bobot Maksimal"] - cdf["Skor Didapat"],
            orientation="h",
            name="Sisa Potensi Bobot",
            marker=dict(color="#1D2D44")
        ))
        fig_bar.update_layout(
            barmode="stack",
            plot_bgcolor="#0A1128",
            paper_bgcolor="#070D1F",
            font=dict(color="#FFFFFF"),
            height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_table:
        st.markdown("#### 📝 Rincian Penjelasan Komponen")
        for k, v in breakdown.items():
            st.markdown(f"""
            <div style="background-color: #0F1C3F; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px; font-size: 12px;">
                <b style="color: #90E0EF;">{v['nama']}</b>: 
                <span style="color: #2ECC71; font-weight: bold;">+{v['skor_didapat']} poin</span> 
                <span style="color: #A0AAB2;">(Input: {v['nilai_input']})</span><br>
                <span style="color: #E0E1DD;">{v['alasan']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    # Perbandingan Sebelum vs Sesudah Analisis AI
    st.markdown("### ⚖️ Perbandingan Sebelum vs Sesudah Analisis AI")
    cmp_col1, cmp_col2 = st.columns(2)

    with cmp_col1:
        st.markdown(f"""
        <div class="ignis-card" style="border-left: 4px solid #E67E22;">
            <div style="font-size: 12px; color: #F4A261; font-weight: bold;">SEBELUM ANALISIS (LAPORAN MENTAH MASYARAKAT)</div>
            <ul style="font-size: 13px; color: #E0E1DD; margin-top: 8px;">
                <li><b>Sumber:</b> {score_res['perbandingan']['sebelum']['sumber']}</li>
                <li><b>Keparahan Awal:</b> {score_res['perbandingan']['sebelum']['keparahan_lapor']}</li>
                <li><b>Karakteristik:</b> {score_res['perbandingan']['sebelum']['asumsi_prioritas']}</li>
                <li><b>Kelemahan:</b> Rentan bias eufemisme warga, persepsi personal, dan ketidaksesuaian skala spasial.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with cmp_col2:
        st.markdown(f"""
        <div class="ignis-card" style="border-left: 4px solid #2ECC71;">
            <div style="font-size: 12px; color: #2ECC71; font-weight: bold;">SESUDAH ANALISIS (SISTEM CERDAS IGNIS)</div>
            <ul style="font-size: 13px; color: #E0E1DD; margin-top: 8px;">
                <li><b>Sumber:</b> {score_res['perbandingan']['sesudah']['sumber']}</li>
                <li><b>Skor Terukur:</b> <b>{score_res['total_skor']}/100</b> ({score_res['label']})</li>
                <li><b>Kalibrasi:</b> {score_res['perbandingan']['sesudah']['kalibrasi']}</li>
                <li><b>Keunggulan:</b> Objektif, transparan, terintegrasi bahaya gambut dan radius ancaman warga.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Sinkronisasi ke DB
    if st.button("🔄 Perbarui & Simpan Skor Terkalibrasi ke Database", use_container_width=True):
        update_scoring(report["id"], score_res["total_skor"], score_res["label"], score_res["narasi_xai"])
        st.success(f"Skor laporan {report['kode_laporan']} berhasil disinkronisasi ke database!")
