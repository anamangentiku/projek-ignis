"""
IGNIS KLABAT - Sistem Pelaporan & Pendukung Keputusan Mitigasi Kebakaran Hutan Gunung Klabat.
Wilayah Kerja: Kawasan Gunung Klabat (1.995 mdpl), Minahasa Utara, Sulawesi Utara.
Tampilan: Clean White / Light Mode — Elegan, Modern, dan Nyaman di Mata.
"""

import os
import sys
from datetime import datetime
from PIL import Image
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import (
    init_db,
    insert_laporan,
    get_all_laporan_prioritas,
    get_laporan_aktif,
    get_riwayat_selesai,
    update_status_pemadaman,
    tandai_sudah_diatasi,
    get_laporan_detail
)
from data.generate_klabat_data import seed_klabat_database
from modules.emergency_chatbot import get_anti_panic_response, KONTAK_DARURAT_KLABAT
from modules.ai_priority_classifier import classify_fire_priority_ai
from modules.klabat_map import render_klabat_folium_map
from modules.fishbone_klabat import render_tab_fishbone

# ==============================================================================
# INISIALISASI DATABASE & KONFIGURASI HALAMAN
# ==============================================================================
init_db()
seed_klabat_database()

st.set_page_config(
    page_title="IGNIS Klabat - Mitigasi Kebakaran Minahasa Utara",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Folder upload gambar lokal
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Inisialisasi Session State Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

# ==============================================================================
# STYLING CSS CLEAN WHITE & LIGHT SLATE (NYAMAN DI MATA)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Clean White / Soft Slate Background */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1380px !important;
    }

    /* Top App Navigation Bar (Light Clean) */
    .ignis-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px 22px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 10px 15px -5px rgba(0, 0, 0, 0.02);
    }
    .ignis-brand-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ignis-brand-flame {
        background: linear-gradient(135deg, #ff6b35 0%, #ea580c 100%);
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25);
    }
    .ignis-brand-sub {
        font-size: 12.5px;
        color: #64748b;
        font-weight: 400;
        margin-top: 2px;
    }
    .ignis-badge-role {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Modern Clean White Cards */
    .ignis-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 6px 16px -2px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ignis-card:hover {
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.07);
    }

    .ignis-card-header {
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 14px;
        margin-bottom: 18px;
    }
    .ignis-card-title {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
    }
    .ignis-card-desc {
        font-size: 13px;
        color: #64748b;
        margin: 4px 0 0 0;
        line-height: 1.5;
    }

    /* KPI Metric Cards (Clean Light) */
    .ignis-kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.02);
    }
    .ignis-kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .kpi-blue::before { background: #0284c7; }
    .kpi-red::before { background: #ef4444; }
    .kpi-orange::before { background: #f97316; }
    .kpi-emerald::before { background: #10b981; }

    .kpi-label {
        font-size: 11.5px;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 6px;
        letter-spacing: -0.5px;
    }

    /* Report Priority Cards with Clean Border Left */
    .report-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.03);
        position: relative;
        overflow: hidden;
    }
    .card-critical { border-left: 5px solid #ef4444 !important; }
    .card-high { border-left: 5px solid #f97316 !important; }
    .card-medium { border-left: 5px solid #f59e0b !important; }
    .card-low { border-left: 5px solid #10b981 !important; }

    /* Priority Badges (Light Pastel Contrast) */
    .badge-prio {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.3px;
        display: inline-block;
    }
    .badge-critical { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-high { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
    .badge-medium { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
    .badge-low { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }

    /* Chatbot Bubbles (Clean Light High-Contrast) */
    .chat-bubble-assistant {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 14px;
        color: #0f172a !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .chat-bubble-assistant b, .chat-bubble-assistant strong {
        color: #0284c7 !important;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border: 1px solid #0284c7;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 14px;
        color: #ffffff !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        text-align: right;
        margin-left: 18%;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
    }

    /* Uniform Form Controls (Clean White Background) */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 9px !important;
        font-size: 13.5px !important;
        padding: 9px 12px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: #ea580c !important;
        box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.12) !important;
    }

    /* Uniform Textarea (Clean White Background) */
    .stTextArea textarea,
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        caret-color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 9px !important;
        font-size: 13.5px !important;
        line-height: 1.6 !important;
        padding: 10px 14px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .stTextArea textarea:focus {
        border-color: #ea580c !important;
        box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.12) !important;
    }

    /* Standard Buttons (Light Outline) */
    .stButton > button {
        background: #ffffff;
        color: #1e293b !important;
        border: 1px solid #cbd5e1;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13.5px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        background: #f8fafc;
        border-color: #94a3b8;
        color: #0f172a !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    }

    /* Form Submit Main Button (Vibrant Flame Orange) */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #ff6b35 0%, #ea580c 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
        border: none !important;
        border-radius: 9px !important;
        padding: 11px 24px !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.3) !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
    }
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%) !important;
        box-shadow: 0 6px 18px rgba(234, 88, 12, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* Clean Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f1f5f9;
        padding: 5px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 13px;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #ea580c !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }

    /* Emergency Contact Card Grid */
    .contact-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .contact-card:hover {
        border-color: #0284c7;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1);
    }
    .contact-icon {
        width: 36px;
        height: 36px;
        background: #f0f9ff;
        color: #0284c7;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
    }

    /* Section Step Pill */
    .step-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 700;
        color: #0284c7;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Preset Titik Patokan Kawasan Gunung Klabat
PRESET_PATOKAN_KLABAT = {
    "Pilih Titik Patokan Gunung Klabat (Opsional)...": (1.4650, 124.9900, "Kawasan Lereng Gunung Klabat", 2.0, "Semak Belukar"),
    "Kawasan Wisata Kaki Dian, Airmadidi Atas": (1.4365, 124.9820, "Kawasan Wisata Kaki Dian, Airmadidi Atas", 0.4, "Semak Kering & Kebun Cengkeh"),
    "Jalur Pendakian Pos 1 Airmadidi (Elevasi 600 mdpl)": (1.4440, 124.9850, "Jalur Pendakian Pos 1 Airmadidi", 0.5, "Kebun Campuran"),
    "Jalur Pendakian Pos 2 Airmadidi (Elevasi 850 mdpl)": (1.4502, 124.9880, "Jalur Pendakian Pos 2 Airmadidi", 1.8, "Hutan Sekunder"),
    "Jalur Pendakian Pos 3 & 4 (Elevasi 1.200 - 1.450 mdpl)": (1.4580, 124.9910, "Jalur Pos 3-4 (Batu Belah)", 2.5, "Hutan Ranting Kering"),
    "Jalur Pendakian Pos 5 & 6 (Elevasi 1.600 - 1.800 mdpl)": (1.4620, 124.9925, "Jalur Pos 5-6 Hutan Lumut", 3.5, "Hutan Lumut & Jurang"),
    "Puncak Gunung Klabat & Danau Kering (1.995 mdpl)": (1.4658, 124.9935, "Puncak Klabat & Bibir Kawah Kering", 4.5, "Savana Gunung"),
    "Lereng Utara: Desa Tatelu / Matungkas (Dimembe)": (1.4720, 124.9780, "Lereng Utara Desa Tatelu Kec. Dimembe", 0.8, "Perkebunan Cengkeh & Pala"),
    "Lereng Barat Daya: Desa Suwaan / Kolongan (Kalawat)": (1.4420, 124.9650, "Lereng Barat Desa Suwaan Kec. Kalawat", 0.6, "Semak Belukar & Perkebunan"),
    "Lereng Timur: Desa Paslaten / Treman (Kauditan)": (1.4510, 125.0150, "Lereng Timur Desa Paslaten Kec. Kauditan", 1.1, "Kebun Kelapa & Bambu")
}

# ==============================================================================
# FITUR 1: HALAMAN LOGIN SISTEM (CLEAN LIGHT)
# ==============================================================================
def render_login_view():
    st.markdown("""
    <div style="max-width: 540px; margin: 35px auto 15px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: linear-gradient(135deg, #ff6b35 0%, #ea580c 100%); border-radius: 14px; font-size: 26px; box-shadow: 0 6px 18px rgba(234, 88, 12, 0.3); margin-bottom: 14px;">
            🔥
        </div>
        <div style="font-size: 32px; font-weight: 800; color: #0f172a; letter-spacing: -0.6px; margin-bottom: 4px;">
            IGNIS <span style="color: #ea580c;">KLABAT</span>
        </div>
        <p style="color: #64748b; font-size: 13.5px; line-height: 1.5; margin: 0 auto; max-width: 460px;">
            Sistem Intelijen Geospasial & Pendukung Keputusan Mitigasi Kebakaran Hutan Gunung Klabat (1.995 mdpl), Minahasa Utara
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_center, c_right = st.columns([1, 1.8, 1])
    with c_center:
        st.markdown("""
        <div class="ignis-card" style="border-top: 3px solid #ea580c; padding: 22px 24px; margin-bottom: 16px;">
            <div style="text-align: center; margin-bottom: 14px;">
                <span style="font-size: 16px; font-weight: 700; color: #0f172a;">Portal Autentikasi Pengguna</span>
                <p style="font-size: 12.5px; color: #64748b; margin: 2px 0 0 0;">Pilih tab peran untuk mengakses sistem.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_warga, tab_damkar = st.tabs(["👤 Masyarakat & Pendaki", "🚒 Regu Pemadam & BPBD"])

        # TAB 1: LOGIN WARGA / PENDAKI
        with tab_warga:
            st.markdown("""
            <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 12px; color: #0369a1;">
                <b>Akses Publik:</b> Untuk warga desa lereng Klabat atau pendaki yang melihat kepulan asap serta membutuhkan panduan evakuasi darurat.
            </div>
            """, unsafe_allow_html=True)

            w_user = st.text_input("Nama Pengguna / Pelapor:", value="warga", key="w_user")
            w_pass = st.text_input("Kata Sandi:", type="password", value="warga123", key="w_pass")

            if st.button("Masuk Sebagai Warga / Pendaki", use_container_width=True, key="btn_login_warga"):
                if w_user.strip() and w_pass.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_role = "masyarakat"
                    st.session_state.username = w_user.strip()
                    st.rerun()
                else:
                    st.error("Silakan masukkan nama pengguna dan kata sandi.")

        # TAB 2: LOGIN PETUGAS DAMKAR & BPBD
        with tab_damkar:
            st.markdown("""
            <div style="background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 12px; color: #c2410c;">
                <b>Akses Khusus:</b> Personel Satgas Pemadam Airmadidi, BPBD Minahasa Utara, dan Pos Registrasi Klabat.
            </div>
            """, unsafe_allow_html=True)

            d_user = st.text_input("ID Personel / Username:", value="damkar", key="d_user")
            d_pass = st.text_input("Kata Sandi Petugas:", type="password", value="damkar123", key="d_pass")

            if st.button("Masuk Sebagai Regu Pemadam & BPBD", use_container_width=True, key="btn_login_damkar"):
                if d_user.strip().lower() in ["damkar", "bpbd", "petugas", "admin"] and d_pass.strip() in ["damkar123", "minut112", "admin123"]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "damkar"
                    st.session_state.username = d_user.strip().upper()
                    st.rerun()
                else:
                    st.error("Kredensial tidak valid. Silakan gunakan ID 'damkar' dan sandi 'damkar123'.")

        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-top: 16px; font-size: 12px; color: #64748b; text-align: center;">
            🔑 <b>Kredensial Pengujian:</b> Warga: <code>warga / warga123</code> • Petugas: <code>damkar / damkar123</code>
        </div>
        """, unsafe_allow_html=True)

# Guard Autentikasi
if not st.session_state.logged_in:
    render_login_view()
    st.stop()

# ==============================================================================
# HEADER NAVIGASI SAAT LOGIN (INTEGRATED LIGHT TOPBAR)
# ==============================================================================
is_masyarakat = (st.session_state.user_role == "masyarakat")
role_title = "Portal Masyarakat & Pendaki" if is_masyarakat else "Pusat Komando Satgas Damkar & BPBD"
role_badge_bg = "#f0f9ff" if is_masyarakat else "#fff7ed"
role_badge_color = "#0369a1" if is_masyarakat else "#c2410c"
role_badge_border = "#bae6fd" if is_masyarakat else "#fed7aa"
role_icon = "👤" if is_masyarakat else "🚒"

col_nav_left, col_nav_right = st.columns([4.2, 1.1])

with col_nav_left:
    st.markdown(f"""
    <div class="ignis-navbar" style="margin-bottom: 0;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div class="ignis-brand-flame">🔥</div>
            <div>
                <div class="ignis-brand-title">
                    IGNIS <span style="color: #ea580c;">KLABAT</span>
                    <span class="ignis-badge-role" style="background: {role_badge_bg}; color: {role_badge_color}; border: 1px solid {role_badge_border};">
                        {role_icon} {role_title}
                    </span>
                </div>
                <div class="ignis-brand-sub">
                    Wilayah Pantau: Gunung Klabat (1.995 mdpl) • Minahasa Utara, Sulawesi Utara • Pengguna: <b>{st.session_state.username}</b>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_nav_right:
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Keluar", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# PERAN 1: MASYARAKAT / PENDAKI (USER 1)
# ==============================================================================
if is_masyarakat:
    # Banner Petunjuk (Soft Light Tint)
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 10px; padding: 12px 18px; margin-bottom: 20px; font-size: 13px; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        💡 <b>Pelaporan Cepat & Aman:</b> Kirimkan informasi titik api di lereng atau jalur Klabat. AI akan menghitung prioritas risiko secara otomatis. Jika situasi mendesak, gunakan Asisten AI di panel kanan untuk panduan evakuasi darurat.
    </div>
    """, unsafe_allow_html=True)

    col_lapor, col_chat = st.columns([1.15, 1], gap="large")

    # ---------- FORMULIR INFORMASI KEBAKARAN (TANPA PILIH KEPARAHAN) ----------
    with col_lapor:
        st.markdown("""
        <div class="ignis-card">
            <div class="ignis-card-header">
                <h3 class="ignis-card-title">📝 Formulir Pelaporan Kebakaran Cepat</h3>
                <p class="ignis-card-desc">
                    Laporan langsung diteruskan ke Posko Damkar Minahasa Utara. AI mengotomasi penilaian keparahan sehingga Anda cukup menceritakan kondisi yang tampak.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_lapor_masyarakat_ai", clear_on_submit=False):
            st.markdown('<div class="step-pill">1. Identitas & Kontak Pelapor</div>', unsafe_allow_html=True)
            c_nama, c_telp = st.columns([1.2, 1])
            with c_nama:
                nama_user = st.text_input(
                    "Nama Lengkap Pelapor *",
                    placeholder="Contoh: Rendy Kaligis",
                    value=st.session_state.username if st.session_state.username != "warga" else ""
                )
            with c_telp:
                kontak_user = st.text_input(
                    "Nomor HP / WhatsApp Aktif *",
                    placeholder="Contoh: 081244556677"
                )

            st.markdown('<div class="step-pill" style="margin-top: 14px;">2. Titik Lokasi & Patokan Klabat</div>', unsafe_allow_html=True)
            preset_choice = st.selectbox(
                "Pilih Titik Patokan Gunung Klabat (Membantu Menentukan Posisi):",
                list(PRESET_PATOKAN_KLABAT.keys())
            )
            p_lat, p_lon, p_area, p_jarak, p_veg = PRESET_PATOKAN_KLABAT[preset_choice]

            default_gmaps = f"https://www.google.com/maps?q={p_lat:.5f},{p_lon:.5f}" if p_lat != 1.4650 else "https://www.google.com/maps?q=1.4658,124.9935"
            link_lokasi = st.text_input(
                "Tautan Lokasi (Google Maps / Share Location WhatsApp) *",
                value=default_gmaps,
                placeholder="https://maps.app.goo.gl/... atau koordinat"
            )

            c_lat, c_lon = st.columns(2)
            with c_lat:
                lat_input = st.number_input("Garis Lintang (Latitude)", value=float(p_lat), format="%.5f")
            with c_lon:
                lon_input = st.number_input("Garis Bujur (Longitude)", value=float(p_lon), format="%.5f")

            st.markdown('<div class="step-pill" style="margin-top: 14px;">3. Bukti Foto & Situasi Kebakaran</div>', unsafe_allow_html=True)

            tab_file, tab_url = st.tabs(["📁 Unggah Foto Bukti", "🔗 Gunakan Tautan Foto URL"])
            uploaded_image_path = None

            with tab_file:
                uploaded_file = st.file_uploader(
                    "Pilih foto kebakaran dari galeri atau kamera:",
                    type=["jpg", "jpeg", "png", "webp"]
                )
                if uploaded_file is not None:
                    filename = f"klb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    save_path = os.path.join(UPLOAD_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    uploaded_image_path = save_path
                    st.image(uploaded_file, caption="Pratinjau Foto Lampiran", use_container_width=True)

            with tab_url:
                foto_url_input = st.text_input(
                    "Tautan URL Gambar Bukti:",
                    value="https://images.unsplash.com/photo-1542385151-efd9000785a0?w=800&auto=format&fit=crop&q=60"
                )

            deskripsi_tempat = st.text_area(
                "Deskripsi Kejadian & Kondisi Api *",
                placeholder="Ceritakan patokan tempat (misal: dekat Pos 3 atau dekat kebun cengkeh warga), kondisi asap, apakah ada pendaki yang turun, atau jarak ke pemukiman...",
                height=110,
                value="Kepulan asap membubung tinggi di semak lereng arah jalur pendakian. Angin bertiup cukup kencang ke arah atas lereng dan dikhawatirkan membahayakan pendaki."
            )

            jarak_input = st.number_input(
                "Perkiraan Jarak Titik Api ke Pemukiman Warga Terdekat (km):",
                value=float(p_jarak),
                min_value=0.1,
                max_value=20.0,
                step=0.1
            )

            st.markdown("""
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 10px 14px; border-radius: 6px; font-size: 12px; color: #166534; margin: 12px 0 16px 0;">
                🤖 <b>Klasifikasi Otomatis AI (Gemini 3.8 Flash):</b> Prioritas bahaya akan dinilai secara instan dari analisis deskripsi, vegetasi, dan ancaman terhadap keselamatan pemukiman lereng Gunung Klabat.
            </div>
            """, unsafe_allow_html=True)

            btn_submit = st.form_submit_button("🔥 Kirim Laporan ke Posko Damkar Sekarang", use_container_width=True)

        if btn_submit:
            if not nama_user.strip() or not deskripsi_tempat.strip() or not link_lokasi.strip():
                st.error("Mohon lengkapi Nama Pelapor, Tautan Lokasi, dan Deskripsi Kejadian.")
            else:
                final_image = uploaded_image_path if uploaded_image_path else foto_url_input
                area_nama = p_area if p_lat != 1.4650 else "Kawasan Lereng Gunung Klabat"

                with st.spinner("AI sedang menganalisis tingkat prioritas risiko laporan Anda..."):
                    ai_result = classify_fire_priority_ai(
                        deskripsi=deskripsi_tempat.strip(),
                        lokasi_area=area_nama,
                        jarak_pemukiman_km=jarak_input,
                        tipe_vegetasi=p_veg,
                        gambar_kebakaran=final_image
                    )

                    payload = {
                        "tanggal_lapor": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "nama_user": nama_user.strip(),
                        "kontak_user": kontak_user.strip(),
                        "link_lokasi": link_lokasi.strip(),
                        "gambar_kebakaran": final_image,
                        "deskripsi_tempat": deskripsi_tempat.strip(),
                        "lokasi_area": area_nama,
                        "latitude": lat_input,
                        "longitude": lon_input,
                        "keparahan": ai_result["keparahan"],
                        "tipe_vegetasi": p_veg,
                        "jarak_pemukiman_km": jarak_input,
                        "skor_prioritas": ai_result["skor_prioritas"],
                        "label_prioritas": ai_result["label_prioritas"],
                        "alasan_prioritas": ai_result["alasan_prioritas"],
                        "status_penanganan": "Menunggu Penanganan",
                        "catatan_tim": "Laporan baru terverifikasi AI, menunggu pengerahan tim posko damkar.",
                        "is_simulated": 0
                    }

                    new_id = insert_laporan(payload)
                    kode_gen = f"KLB-{datetime.now().year}-{new_id:03d}"

                    st.success(f"Laporan berhasil dikirim ke Posko Damkar & BPBD Minahasa Utara! (Kode Laporan: {kode_gen})")

                    st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #ea580c; padding: 16px 18px; border-radius: 10px; margin-top: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 12px; font-weight: 700; color: #ea580c; letter-spacing: 0.5px;">HASIL ANALISIS PRIORITAS AI ({ai_result['source']})</span>
                            <span style="background: #fff7ed; color: #c2410c; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 4px; border: 1px solid #fed7aa;">KODE: {kode_gen}</span>
                        </div>
                        <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-bottom: 6px;">
                            Prioritas: <span style="color: #ea580c;">{ai_result['label_prioritas']}</span> (Skor Risiko: {ai_result['skor_prioritas']}/100)
                        </div>
                        <div style="font-size: 13.5px; color: #334155; line-height: 1.6;">
                            {ai_result['alasan_prioritas']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ---------- CHATBOT AI ANTI-PANIK (LIGHT CLEAN) ----------
    with col_chat:
        st.markdown("""
        <div class="ignis-card">
            <div class="ignis-card-header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="ignis-card-title">💬 Asisten Darurat & Anti-Panik</h3>
                    <span style="font-size: 11px; color: #047857; font-weight: 700; background: #d1fae5; padding: 3px 9px; border-radius: 12px; border: 1px solid #a7f3d0;">🟢 Online 24 Jam</span>
                </div>
                <p class="ignis-card-desc">
                    Panduan keselamatan langkah-demi-langkah bagi pendaki dan warga seputar lereng Gunung Klabat.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if "klabat_chat_messages" not in st.session_state:
            st.session_state.klabat_chat_messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Halo. Saya adalah **Asisten Siaga IGNIS** untuk kawasan Gunung Klabat.\n\n"
                        "Jika Anda melihat kepulan asap atau berada dekat kobaran api:\n"
                        "1. **Tarik napas perlahan dan tetap tenang.** Jangan panik.\n"
                        "2. **Basahi kain atau masker** dengan air minum untuk melindungi saluran pernapasan.\n"
                        "3. **Hindari berlari mendaki ke atas puncak** jika api berasal dari bawah lereng.\n\n"
                        "Silakan tanyakan panduan evakuasi atau nomor telepon posko yang dapat Anda hubungi."
                    )
                }
            ]

        # Tombol Pertanyaan Cepat
        st.markdown("<div style='font-size: 11.5px; color: #64748b; font-weight: 700; margin-bottom: 8px;'>PANDUAN CEPAT:</div>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        quick_ask = None
        with q1:
            if st.button("🧗 Jalur Pendakian", use_container_width=True):
                quick_ask = "Saya sedang berada di jalur pendakian Gunung Klabat dan melihat asap kebakaran. Apa tindakan pertama yang harus saya ambil?"
        with q2:
            if st.button("🏡 Dekat Pemukiman", use_container_width=True):
                quick_ask = "Api membakar semak dekat pekarangan rumah warga lereng. Tindakan apa yang aman untuk keluarga?"
        with q3:
            if st.button("📞 Kontak Darurat", use_container_width=True):
                quick_ask = "Berikan nomor telepon darurat Damkar, BPBD Minahasa Utara, dan Pos Registrasi Klabat."

        # Kotak Tampilan Chat Bubble Light
        chat_box = st.container(height=410)
        with chat_box:
            for m in st.session_state.klabat_chat_messages:
                if m["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        <div style="font-size: 11px; opacity: 0.9; margin-bottom: 3px; font-weight: 600;">Anda</div>
                        {m['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-bubble-assistant">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                            <span style="background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;">ASISTEN RESMI IGNIS</span>
                            <span style="font-size: 11px; color: #64748b;">SOP Evakuasi Klabat</span>
                        </div>
                        <div style="margin-top: 4px;">
                            {m['content'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Input Chat
        user_chat_input = st.chat_input("Ketik pertanyaan situasi darurat Anda di sini...")
        if quick_ask:
            user_chat_input = quick_ask

        if user_chat_input:
            st.session_state.klabat_chat_messages.append({"role": "user", "content": user_chat_input})
            with chat_box:
                st.markdown(f"""
                <div class="chat-bubble-user">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 3px; font-weight: 600;">Anda</div>
                    {user_chat_input}
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Menyiapkan panduan tindakan aman..."):
                    resp = get_anti_panic_response(user_chat_input)
                    st.markdown(f"""
                    <div class="chat-bubble-assistant">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                            <span style="background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;">ASISTEN RESMI IGNIS</span>
                            <span style="font-size: 11px; color: #64748b;">{resp['source']}</span>
                        </div>
                        <div style="margin-top: 4px;">
                            {resp['answer'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.klabat_chat_messages.append({"role": "assistant", "content": resp["answer"]})
            st.rerun()

        # Direktori Kontak Darurat Resmi
        with st.expander("📞 Kontak Darurat Resmi Wilayah Minahasa Utara", expanded=False):
            st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 6px;">
                <div class="contact-card">
                    <div class="contact-icon">🚨</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Call Center Darurat</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">112 (Bebas Pulsa)</div>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon">🚒</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Damkar Minut (Airmadidi)</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">(0431) 891-113</div>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon">🛡️</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">BPBD Minahasa Utara</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">0811-432-112</div>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon">🚁</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Basarnas Manado (Evakuasi)</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">115 / (0431) 812-111</div>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon">👮</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Polsek Airmadidi</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">(0431) 891-110</div>
                    </div>
                </div>
                <div class="contact-card">
                    <div class="contact-icon">⛺</div>
                    <div>
                        <div style="font-size: 11px; color: #64748b;">Pos Registrasi Klabat</div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">0812-4455-6677</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# PERAN 2: REGU PEMADAM & BPBD (USER 2)
# ==============================================================================
else:
    df_aktif = get_laporan_aktif()
    df_riwayat = get_riwayat_selesai()
    df_all = get_all_laporan_prioritas()

    total_aktif = len(df_aktif)
    total_selesai = len(df_riwayat)
    total_kritis = int((df_aktif["label_prioritas"] == "Kritis").sum()) if not df_aktif.empty else 0
    total_tinggi = int((df_aktif["label_prioritas"] == "Tinggi").sum()) if not df_aktif.empty else 0

    st.markdown("""
    <div class="ignis-card" style="padding: 18px 22px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h3 class="ignis-card-title">🚒 Pusat Komando & Disposisi Operasional Regu Pemadam Klabat</h3>
                <p class="ignis-card-desc">
                    Pantau laporan kebakaran aktif terurut prioritas risiko AI, kerahkan armada posko, dan arsipkan kasus setelah api berhasil dipadamkan.
                </p>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 12px; color: #64748b;">Status Siaga Armada:</span>
                <span style="background: #d1fae5; color: #065f46; font-weight: 700; font-size: 11.5px; padding: 4px 10px; border-radius: 6px; border: 1px solid #a7f3d0;">
                    🟢 SATGAS SIAGA PENUH
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 KPI Metrics Clean Light
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="ignis-kpi-card kpi-blue">
            <div class="kpi-label">
                <span>ANTREAN AKTIF</span>
                <span>📋</span>
            </div>
            <div class="kpi-value" style="color: #0284c7;">{total_aktif}</div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">Memerlukan tindakan satgas</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="ignis-kpi-card kpi-red">
            <div class="kpi-label">
                <span>PRIORITAS KRITIS</span>
                <span>🚨</span>
            </div>
            <div class="kpi-value" style="color: #ef4444;">{total_kritis}</div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">Ancaman dekat pemukiman</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="ignis-kpi-card kpi-orange">
            <div class="kpi-label">
                <span>PRIORITAS TINGGI</span>
                <span>🔥</span>
            </div>
            <div class="kpi-value" style="color: #ea580c;">{total_tinggi}</div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">Jalur pendakian / kebun</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="ignis-kpi-card kpi-emerald">
            <div class="kpi-label">
                <span>SUDAH DIATASI</span>
                <span>✅</span>
            </div>
            <div class="kpi-value" style="color: #10b981;">{total_selesai}</div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">Api berhasil dipadamkan</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    tab_aktif, tab_histori, tab_peta, tab_fishbone = st.tabs([
        f"🚨 Antrean Penanganan Aktif ({total_aktif})",
        f"✅ Riwayat Selesai Dipadamkan ({total_selesai})",
        "🗺️ Peta Geospasial Gunung Klabat",
        "🐟 Analisis Akar Masalah (Fishbone RCA)"
    ])

    # ==================== TAB 1: ANTREAN AKTIF (URUTAN AI) ====================
    with tab_aktif:
        st.markdown("#### Daftar Kejadian Kebakaran yang Membutuhkan Pengerahan Regu")
        st.caption("AI mengurutkan kejadian berdasarkan ancaman tertinggi ke pemukiman dan pendaki. Tandai 'Sudah Diatasi' begitu tim mengonfirmasi api padam.")

        if df_aktif.empty:
            st.markdown("""
            <div style="text-align: center; padding: 45px 20px; background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 12px; margin-top: 10px;">
                <div style="font-size: 38px; margin-bottom: 8px;">🎉</div>
                <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Seluruh Titik Kebakaran Telah Teratasi!</div>
                <div style="font-size: 13px; color: #64748b; max-width: 420px; margin: 4px auto 0 auto;">
                    Tidak ada antrean laporan kebakaran aktif di lereng maupun jalur pendakian Gunung Klabat saat ini.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, r in df_aktif.iterrows():
                prio_label = r["label_prioritas"]
                card_class = (
                    "card-critical" if prio_label == "Kritis" else
                    "card-high" if prio_label == "Tinggi" else
                    "card-medium" if prio_label == "Sedang" else
                    "card-low"
                )
                badge_class = (
                    "badge-critical" if prio_label == "Kritis" else
                    "badge-high" if prio_label == "Tinggi" else
                    "badge-medium" if prio_label == "Sedang" else
                    "badge-low"
                )

                st.markdown(f"""
                <div class="report-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 16px; font-weight: 800; color: #0f172a;">
                                {r['kode_laporan']} • {r['lokasi_area']}
                            </span>
                            <span style="font-size: 12px; color: #64748b; margin-left: 10px;">
                                ⏱️ {r['tanggal_lapor']}
                            </span>
                        </div>
                        <div>
                            <span class="badge-prio {badge_class}">
                                PRIORITAS {prio_label.upper()} (SKOR: {r['skor_prioritas']})
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c_info, c_media, c_action = st.columns([1.4, 1.0, 1.3])

                with c_info:
                    st.markdown(f"**Pelapor:** {r['nama_user']} | Kontak: `{r.get('kontak_user') or 'Tanpa kontak'}`")
                    st.markdown(f"**Vegetasi:** {r['tipe_vegetasi']} | **Jarak ke Rumah Warga:** {r['jarak_pemukiman_km']} km")
                    st.markdown(f"**Deskripsi Kejadian:** *\"{r['deskripsi_tempat']}\"*")
                    
                    st.markdown(f"""
                    <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 10px 12px; margin: 8px 0; font-size: 12.5px; color: #0f172a;">
                        <span style="font-weight: 700; color: #0284c7;">🧠 Analisis AI:</span> {r['alasan_prioritas']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Status Operasional Saat Ini:** <span style='color: #d97706; font-weight: 700;'>{r['status_penanganan']}</span>", unsafe_allow_html=True)

                with c_media:
                    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 4px;'>DOKUMENTASI FOTO:</div>", unsafe_allow_html=True)
                    gambar_src = r['gambar_kebakaran']
                    if gambar_src:
                        try:
                            if os.path.exists(gambar_src):
                                img = Image.open(gambar_src)
                                st.image(img, caption=r['kode_laporan'], use_container_width=True)
                            else:
                                st.image(gambar_src, caption=r['kode_laporan'], use_container_width=True)
                        except Exception:
                            st.caption("Foto bukti tidak dapat dimuat.")
                    else:
                        st.caption("Tanpa foto bukti.")

                    link_gmaps = r['link_lokasi']
                    st.markdown(f"""
                    <div style="margin-top: 6px;">
                        <a href="{link_gmaps}" target="_blank" style="display: block; text-align: center; background: #0284c7; color: #ffffff; padding: 7px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none;">
                            📍 Buka Navigasi Rute Maps
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

                with c_action:
                    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 4px;'>TINDAKAN SATGAS DAMKAR:</div>", unsafe_allow_html=True)

                    catatan_selesai = st.text_input(
                        "Catatan Penanganan Lapangan:",
                        value=r.get('catatan_tim', ''),
                        placeholder="Misal: Api berhasil dipadamkan regu Posko Airmadidi...",
                        key=f"note_active_{r['id']}"
                    )

                    # TOMBOL UTAMA: TANDAI SUDAH DIATASI
                    if st.button(f"✅ Tandai Sudah Diatasi ({r['kode_laporan']})", key=f"btn_done_{r['id']}", use_container_width=True):
                        catatan_final = catatan_selesai.strip() if catatan_selesai.strip() else "Kebakaran telah berhasil dipadamkan oleh regu lapangan."
                        tandai_sudah_diatasi(r['id'], catatan_final)
                        st.success(f"Laporan {r['kode_laporan']} telah berhasil dipadamkan dan dipindahkan ke Riwayat!")
                        st.rerun()

                    # Opsi Pembaruan Status Bertahap
                    with st.expander("Ubah Status Operasional", expanded=False):
                        status_options = ["Menunggu Penanganan", "Tim Menuju Lokasi", "Sedang Dipadamkan"]
                        cur_idx = status_options.index(r['status_penanganan']) if r['status_penanganan'] in status_options else 0
                        new_st = st.selectbox(
                            "Status Tim:",
                            status_options,
                            index=cur_idx,
                            key=f"sel_st_{r['id']}"
                        )
                        if st.button(f"Perbarui ke '{new_st}'", key=f"btn_update_{r['id']}", use_container_width=True):
                            update_status_pemadaman(r['id'], new_st, catatan_selesai)
                            st.success("Status operasional berhasil diperbarui!")
                            st.rerun()

                st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 18px 0 24px 0;'>", unsafe_allow_html=True)

    # ==================== TAB 2: RIWAYAT PENANGANAN (SUDAH DIATASI) ====================
    with tab_histori:
        st.markdown("#### Arsip Riwayat Kebakaran yang Telah Selesai Ditangani")
        st.caption("Daftar insiden kebakaran di kawasan Gunung Klabat yang berhasil dipadamkan dengan waktu penyelesaian terekam.")

        if df_riwayat.empty:
            st.info("Belum ada riwayat penanganan selesai. Laporan yang ditandai 'Sudah Diatasi' pada Tab 1 akan otomatis tercatat di sini.")
        else:
            for idx, r in df_riwayat.iterrows():
                st.markdown(f"""
                <div style="background-color: #ffffff; border: 1px solid #bbf7d0; border-left: 5px solid #10b981; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-size: 16px; font-weight: 800; color: #0f172a;">
                                {r['kode_laporan']} • {r['lokasi_area']}
                            </span>
                            <span style="font-size: 12px; color: #059669; margin-left: 10px; font-weight: 700;">
                                ✅ STATUS: PADAM / BERHASIL DIATASI
                            </span>
                        </div>
                        <div>
                            <span style="background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">
                                KASUS SELESAI
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c_h_info, c_h_media, c_h_time = st.columns([1.5, 1.0, 1.2])

                with c_h_info:
                    st.markdown(f"**Nama Pelapor:** {r['nama_user']} | Kontak: `{r.get('kontak_user') or 'Tanpa kontak'}`")
                    st.markdown(f"**Vegetasi:** {r['tipe_vegetasi']} | **Jarak Pemukiman:** {r['jarak_pemukiman_km']} km")
                    st.markdown(f"**Deskripsi Awal:** *\"{r['deskripsi_tempat']}\"*")
                    st.markdown(f"**Catatan Petugas:** <span style='color: #059669; font-weight: 600;'>\"{r.get('catatan_tim') or 'Penanganan selesai dan kondisi lereng aman.'}\"</span>", unsafe_allow_html=True)

                with c_h_media:
                    gambar_src = r['gambar_kebakaran']
                    if gambar_src:
                        try:
                            if os.path.exists(gambar_src):
                                img = Image.open(gambar_src)
                                st.image(img, caption=f"Dokumentasi {r['kode_laporan']}", use_container_width=True)
                            else:
                                st.image(gambar_src, caption=f"Dokumentasi {r['kode_laporan']}", use_container_width=True)
                        except Exception:
                            st.caption("Foto dokumentasi.")
                    else:
                        st.caption("Tanpa foto.")

                with c_h_time:
                    st.markdown(f"""
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 14px; border-radius: 8px; font-size: 12px; color: #334155;">
                        <div style="margin-bottom: 6px;"><b>Waktu Lapor Masuk:</b><br>{r['tanggal_lapor']}</div>
                        <div style="margin-bottom: 6px;"><b>Waktu Selesai Pemadaman:</b><br><span style="color: #059669; font-weight: 700;">{r.get('waktu_selesai') or 'Telah diselesaikan'}</span></div>
                        <div><b>Skor Prioritas Awal:</b> {r['skor_prioritas']} ({r['label_prioritas']})</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"🔄 Buka Kembali Kasus", key=f"btn_reopen_{r['id']}", use_container_width=True):
                        update_status_pemadaman(r['id'], "Sedang Dipadamkan", "Kasus dibuka kembali karena titik api menyala kembali.")
                        st.warning(f"Kasus {r['kode_laporan']} telah dikembalikan ke Antrean Aktif.")
                        st.rerun()

                st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 18px 0 24px 0;'>", unsafe_allow_html=True)

    # ==================== TAB 3: PETA GEOSPASIAL GUNUNG KLABAT ====================
    with tab_peta:
        st.markdown("#### Peta Interaktif Sebaran Titik Api Gunung Klabat")
        st.caption("Pusat pantauan: Puncak Gunung Klabat (1.995 mdpl) serta koridor lereng desa Airmadidi, Kalawat, Dimembe, dan Kauditan.")

        klabat_map = render_klabat_folium_map(df_all)
        st_folium(klabat_map, width="100%", height=560, returned_objects=[])

        st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 14px 18px; border-radius: 10px; font-size: 12.5px; margin-top: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px;">Legenda Status Marker Peta Geospasial:</div>
            <div style="display: flex; gap: 18px; flex-wrap: wrap; color: #334155;">
                <div><span style="color: #ef4444; font-weight: 800;">● Merah:</span> Prioritas Kritis Aktif (Dekat Pemukiman / Kaki Dian)</div>
                <div><span style="color: #f97316; font-weight: 800;">● Oranye:</span> Prioritas Tinggi Aktif (Jalur Pendakian Pos 1-6)</div>
                <div><span style="color: #f59e0b; font-weight: 800;">● Kuning:</span> Prioritas Sedang Aktif (Lereng Terisolasi / Savana)</div>
                <div><span style="color: #10b981; font-weight: 800;">● Hijau:</span> Sudah Berhasil Diatasi / Api Padam</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==================== TAB 4: FISHBONE RCA ====================
    with tab_fishbone:
        render_tab_fishbone(df_all)