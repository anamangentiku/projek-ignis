"""
AI Chatbot View for IGNIS.
Asisten cerdas berbasis Google Gemini API yang terhubung dengan grounding data laporan real-time
dan repositori SOP mitigasi karhutla resmi. Dilengkapi fallback transparan jika API Key tidak disetel.
"""

import streamlit as st
import os
from database.db_manager import get_all_laporan
from modules.llm_service import answer_chat_query

def render_chatbot_view():
    st.markdown("""
    <div style="padding: 10px 0 15px 0;">
        <h2 style="margin: 0; color: #FFFFFF;">💬 Asisten Cerdas IGNIS (AI Grounded Chatbot)</h2>
        <p style="color: #90E0EF; margin: 5px 0 0 0;">
            Konsultasikan situasi titik api, analisis data laporan terkini, dan prosedur operasional standar (SOP)
            penanggulangan karhutla berbasis regulasi resmi (KLHK, BNPB, BMKG).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Inisialisasi riwayat chat di session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Halo! Saya adalah **Asisten Cerdas IGNIS**. Saya dapat membantu Anda menelusuri data laporan titik api di database, "
                    "memeriksa prioritas risiko, serta memberikan referensi SOP resmi penanggulangan karhutla (Permen LHK No. P.32/2016 & BRGM). "
                    "Ada yang bisa saya bantu hari ini?"
                ),
                "source": "Sistem Inisial IGNIS",
                "is_fallback": False
            }
        ]

    # Ambil data terkini untuk konteks grounding
    df = get_all_laporan(include_simulated=True)

    # Indikator Status API Key
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    is_api_set = bool(api_key and api_key != "your_gemini_api_key_here")

    status_col1, status_col2 = st.columns([2, 1])
    with status_col1:
        if is_api_set:
            st.success("🟢 **Gemini API Aktif:** Mode AI Generatif dengan Grounding Real-Time.")
        else:
            st.warning("🟠 **Mode Fallback Aktif [BUKAN HASIL LLM]:** API Key belum disetel di .env. Menggunakan Rule-Based Expert System deterministik.")

    with status_col2:
        if st.button("🧹 Bersihkan Riwayat Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()

    # Quick prompt buttons
    st.markdown("##### 💡 Pertanyaan Cepat yang Sering Diajukan:")
    q_col1, q_col2, q_col3 = st.columns(3)
    quick_query = None
    with q_col1:
        if st.button("🚨 Berapa laporan prioritas KRITIS?", use_container_width=True):
            quick_query = "Berapa jumlah laporan prioritas KRITIS saat ini dan apa tindakan darurat yang harus diambil?"
    with q_col2:
        if st.button("🌿 Apa SOP penanganan lahan gambut?", use_container_width=True):
            quick_query = "Bagaimana standar operasional prosedur penanganan kebakaran pada lahan gambut menurut BRGM dan KLHK?"
    with q_col3:
        if st.button("⚖️ Apa sanksi hukum pembakaran lahan?", use_container_width=True):
            quick_query = "Apa sanksi hukum bagi pelaku pembakaran hutan dan lahan berdasarkan undang-undang di Indonesia?"

    st.markdown("---")

    # Tampilkan percakapan yang ada
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("source"):
                badge_bg = "#2A9D8F" if not msg.get("is_fallback") else "#E76F51"
                st.markdown(
                    f"<div style='font-size: 11px; color: #A0AAB2; margin-top: 4px;'>"
                    f"Sumber: <span style='background-color: {badge_bg}; color: white; padding: 2px 6px; border-radius: 4px;'>{msg['source']}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # Input pengguna
    user_input = st.chat_input("Tanyakan sesuatu seputar laporan karhutla atau SOP mitigasi...")
    if quick_query:
        user_input = quick_query

    if user_input:
        # Tambahkan pertanyaan pengguna ke state
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "source": None,
            "is_fallback": False
        })
        with st.chat_message("user"):
            st.markdown(user_input)

        # Proses jawaban AI dengan grounding data
        with st.chat_message("assistant"):
            with st.spinner("Menganalisis basis data laporan dan referensi SOP..."):
                response = answer_chat_query(user_input, df, st.session_state.messages)
                st.markdown(response["answer"])

                badge_bg = "#2A9D8F" if not response["is_fallback"] else "#E76F51"
                st.markdown(
                    f"<div style='font-size: 11px; color: #A0AAB2; margin-top: 4px;'>"
                    f"Sumber: <span style='background-color: {badge_bg}; color: white; padding: 2px 6px; border-radius: 4px;'>{response['source']}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # Simpan jawaban ke state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "source": response["source"],
                    "is_fallback": response["is_fallback"]
                })
