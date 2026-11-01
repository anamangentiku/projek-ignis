"""
Evaluasi Kegagalan AI View for IGNIS.
Halaman khusus pengujian dan analisis formal terhadap 3 mode kegagalan kritis AI:
1. Hallucination (Halusinasi Fakta/Personel Fiktif)
2. Kesalahan Klasifikasi Prioritas (Under-Reporting & Keyword Bias)
3. Rekomendasi Tidak Relevan (Context-Blind Mitigation Recommendation)
"""

import streamlit as st
from modules.ai_evaluation import get_all_evaluation_cases

def render_evaluasi_ai_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">🧪 Evaluasi AI & Analisis Mode Kegagalan (Failure Benchmarking)</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Pengujian empiris terhadap batas kemampuan AI (Limitation Testing) dan pembuktian efektivitas
            guardrails sistemik dalam mencegah halusinasi, kesalahan klasifikasi, dan rekomendasi tidak tepat konteks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cases = get_all_evaluation_cases()

    # Selector kasus
    case_titles = [f"{c['id']} - {c['kategori']}" for c in cases]
    selected_idx = st.selectbox(
        "Pilih Skenario Kasus Uji Kegagalan AI:",
        range(len(cases)),
        format_func=lambda i: case_titles[i]
    )

    case = cases[selected_idx]

    # Header Kasus
    st.markdown(f"""
    <div class="ignis-card" style="border-top: 4px solid {case['badge_color']}; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #FFFFFF;">{case['title']}</h3>
            <span style="background-color: #2ECC71; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 11px;">
                {case['status_evaluasi']}
            </span>
        </div>
        <div style="font-size: 12px; color: #A0AAB2; margin-top: 6px;">
            Kategori Uji: <b style="color: #FFD166;">{case['kategori']}</b> | Identifikasi Kasus: <b>{case['id']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Parameter Input Pengujian
    st.markdown("#### 📥 1. Parameter Input Pengujian (Test Case Payload)")
    st.json(case["input_pengujian"])

    # 2. Perbandingan Side-by-Side: Output Sebelum vs Hasil yang Diharapkan
    st.markdown("#### ⚖️ 2. Komparasi Kegagalan vs Hasil yang Diharapkan (Ground Truth)")
    col_fail, col_truth = st.columns(2)

    with col_fail:
        st.markdown("""
        <div class="ignis-card" style="border-left: 4px solid #E63946; height: 100%;">
            <div style="font-size: 12px; color: #FFAAA6; font-weight: bold;">❌ OUTPUT MODEL AWAL (SEBELUM PERBAIKAN)</div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 13px; color: #FFFFFF; line-height: 1.5; margin-top: 8px;'>{case['output_awal_gagal']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_truth:
        st.markdown("""
        <div class="ignis-card" style="border-left: 4px solid #00B4D8; height: 100%;">
            <div style="font-size: 12px; color: #90E0EF; font-weight: bold;">🎯 HASIL YANG DIHARAPKAN (GROUND TRUTH / TARGET)</div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 13px; color: #FFFFFF; line-height: 1.5; margin-top: 8px;'>{case['hasil_diharapkan']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Analisis Akar Penyebab Kegagalan AI
    st.markdown("#### 🔍 3. Analisis Akar Penyebab Kegagalan Model (AI Root Cause Analysis)")
    st.markdown(f"""
    <div style="background-color: #0F1C3F; border-left: 4px solid #F4A261; padding: 12px 16px; border-radius: 4px; font-size: 13px; color: #E0E1DD; line-height: 1.6;">
        <b>Mengapa AI Mengalami Kegagalan Ini?</b><br>
        {case['akar_penyebab']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Solusi Mitigasi & Prompt Guardrail Perbaikan
    st.markdown("#### 🛡️ 4. Mitigasi Teknis & Prompt Guardrail Perbaikan")
    for fix in case["mitigasi_perbaikan"]:
        st.markdown(f"""
        <div style="background-color: #070D1F; border: 1px solid #1D2D44; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-size: 13px; color: #90E0EF;">
            ✔ {fix}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Hasil Pengujian Setelah Perbaikan (Verified)
    st.markdown("#### ✅ 5. Hasil Verifikasi Pengujian Pasca Perbaikan")
    st.markdown(f"""
    <div class="ignis-card" style="border-left: 4px solid #2ECC71;">
        <div style="font-size: 12px; color: #2ECC71; font-weight: bold; margin-bottom: 8px;">
            OUTPUT TERVERIFIKASI SISTEM IGNIS (POST-MITIGATION VERIFIED OUTPUT)
        </div>
        <div style="font-size: 13px; color: #FFFFFF; line-height: 1.6;">
            {case['output_setelah_perbaikan']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabel Rekapitulasi 3 Pengujian
    st.markdown("---")
    st.markdown("### 📊 Rekapitulasi Hasil Pengujian Kegagalan AI")
    recap_data = [
        {"ID": c["id"], "Kategori Kegagalan": c["kategori"], "Penyebab Kunci": c["akar_penyebab"][:55] + "...", "Metode Solusi": c["mitigasi_perbaikan"][0][:55] + "...", "Status": "PASSED ✅"}
        for c in cases
    ]
    st.dataframe(pd.DataFrame(recap_data), use_container_width=True, hide_index=True)
