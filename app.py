"""
IGNIS - Sistem Pelaporan & Pendukung Keputusan Mitigasi Kebakaran Gunung Klabat, Minahasa Utara.
Dilengkapi:
1. Autentikasi Login Peran (Masyarakat/Pendaki vs Regu Pemadam/BPBD)
2. UI Modern & Eye-Catching dengan kontras tinggi pada chatbot
3. Otomasi Penentuan Prioritas AI Menggunakan Gemini 3.8 Flash (Masyarakat tidak perlu memilih keparahan)
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime
from PIL import Image

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
from streamlit_folium import st_folium
import re
import textwrap
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go

STATUS_DATA = "Didukung data"
STATUS_DUGAAN = "Dugaan"

# Ambang untuk analisis seluruh laporan (agregat)
MIN_KASUS_AGREGAT = 2        # minimal jumlah laporan yang cocok
MIN_PERSEN_AGREGAT = 10.0    # minimal persentase laporan yang cocok
MIN_SELESAI_DURASI = 3       # minimal laporan selesai agar median durasi dianggap bermakna

EFEK = "Kebakaran Hutan & Lahan<br>Gunung Klabat"

# ----------------------------------------------------------------------------
# DEFINISI FAKTOR (edit di sini jika ingin menambah / mengganti faktor)
# tipe: "kata_kunci" | "vegetasi" | "area" | "jarak" | "durasi" | "antrean" | "dugaan"
# ----------------------------------------------------------------------------
FAKTOR = [
    # ---------------- MANUSIA ----------------
    {"kategori": "Manusia", "singkat": "Puntung rokok / api unggun",
     "faktor": "Puntung rokok, api unggun, atau sisa perapian pendaki",
     "tipe": "kata_kunci",
     "kata": ["rokok", "puntung", "api unggun", "perapian", "bara"],
     "keterangan": "Aktivitas pendaki atau pengunjung yang meninggalkan sumber api."},
    {"kategori": "Manusia", "singkat": "Pembakaran sampah/serasah",
     "faktor": "Pembakaran sampah atau serasah kebun oleh warga",
     "tipe": "kata_kunci",
     "kata": ["bakar sampah", "membakar sampah", "pembakaran serasah", "membakar serasah",
              "pembakaran ranting", "membakar ranting", "sisa pembakaran", "bakar ranting"],
     "keterangan": "Pembakaran terbuka di batas kebun yang merambat ke semak sekitarnya."},
    {"kategori": "Manusia", "singkat": "Pengawasan pendaki lemah",
     "faktor": "Pengawasan dan edukasi pendaki di pos registrasi terbatas",
     "tipe": "dugaan",
     "keterangan": "Belum ada data pengawasan di sistem. Perlu wawancara dengan pengelola pos."},

    # ---------------- LINGKUNGAN ----------------
    {"kategori": "Lingkungan", "singkat": "Semak/alang-alang kering",
     "faktor": "Vegetasi mudah terbakar (semak, alang-alang, ilalang kering)",
     "tipe": "vegetasi", "kata": ["semak", "alang", "ilalang"],
     "keterangan": "Bahan bakar halus yang cepat kering dan cepat merambat."},
    {"kategori": "Lingkungan", "singkat": "Kebun cengkeh/pala/kelapa",
     "faktor": "Kebun produktif (cengkeh, pala, kelapa) di batas hutan",
     "tipe": "vegetasi", "kata": ["cengkeh", "pala", "kelapa", "kebun"],
     "keterangan": "Serasah kebun menjadi bahan bakar dan api mengancam aset warga."},
    {"kategori": "Lingkungan", "singkat": "Lereng curam & jurang",
     "faktor": "Medan lereng curam, berbatu, dan jurang",
     "tipe": "kata_kunci", "kata": ["jurang", "terjal", "curam", "berbatu", "licin"],
     "keterangan": "Medan sulit memperlambat pergerakan regu darat."},

    # ---------------- CUACA ----------------
    {"kategori": "Cuaca", "singkat": "Angin kencang",
     "faktor": "Angin kencang yang memperluas dan melompatkan api",
     "tipe": "kata_kunci", "kata": ["angin kencang", "angin cukup kencang", "tersapu angin",
                                    "angin bertiup", "angin puncak"],
     "keterangan": "Angin lereng mempercepat rambatan api ke atas dan ke arah pemukiman."},
    {"kategori": "Cuaca", "singkat": "Kemarau / hari tanpa hujan",
     "faktor": "Musim kemarau dan hari tanpa hujan berturut-turut",
     "tipe": "dugaan",
     "keterangan": "Tidak ada data cuaca di sistem. Perlu data curah hujan BMKG."},
    {"kategori": "Cuaca", "singkat": "Suhu & kelembaban rendah",
     "faktor": "Suhu tinggi dan kelembaban udara rendah",
     "tipe": "dugaan",
     "keterangan": "Tidak ada data suhu/kelembaban di sistem. Perlu data BMKG."},

    # ---------------- INFRASTRUKTUR ----------------
    {"kategori": "Infrastruktur", "singkat": "Kejadian di jalur pendakian",
     "faktor": "Titik api di jalur pendakian (akses evakuasi terbatas)",
     "tipe": "area", "kata": ["jalur", "pos "],
     "keterangan": "Jalur setapak sempit menyulitkan evakuasi pendaki dan akses regu."},
    {"kategori": "Infrastruktur", "singkat": "Dekat pemukiman (<= 1 km)",
     "faktor": "Titik api sangat dekat pemukiman (<= 1 km)",
     "tipe": "jarak", "batas_km": 1.0,
     "keterangan": "Zona penyangga antara hutan dan rumah warga sempit."},
    {"kategori": "Infrastruktur", "singkat": "Sumber air pemadam terbatas",
     "faktor": "Sumber air pemadam di lereng terbatas",
     "tipe": "dugaan",
     "keterangan": "Belum ada data titik air di sistem. Perlu survei lapangan."},

    # ---------------- PENANGANAN ----------------
    {"kategori": "Penanganan", "singkat": "Durasi laporan sampai padam",
     "faktor": "Durasi penanganan dari laporan masuk sampai api padam",
     "tipe": "durasi",
     "keterangan": "Diukur dari selisih tanggal_lapor dan waktu_selesai."},
    {"kategori": "Penanganan", "singkat": "Antrean menunggu penanganan",
     "faktor": "Laporan menumpuk dan masih menunggu penanganan",
     "tipe": "antrean", "batas_persen": 30.0,
     "keterangan": "Persentase laporan berstatus 'Menunggu Penanganan'."},
    {"kategori": "Penanganan", "singkat": "Personel & peralatan terbatas",
     "faktor": "Keterbatasan personel dan peralatan pemadam di lereng",
     "tipe": "dugaan",
     "keterangan": "Belum ada data sumber daya di sistem. Perlu data inventaris Damkar/BPBD."},
]

URUTAN_ATAS = ["Manusia", "Lingkungan", "Cuaca"]
URUTAN_BAWAH = ["Infrastruktur", "Penanganan"]


# ----------------------------------------------------------------------------
# EVALUASI FAKTOR TERHADAP DATA
# ----------------------------------------------------------------------------
def _teks(df: pd.DataFrame, kolom: str) -> pd.Series:
    if kolom not in df.columns:
        return pd.Series([""] * len(df), index=df.index)
    return df[kolom].fillna("").astype(str).str.lower()


def _cocok(df: pd.DataFrame, kolom: str, kata: List[str]) -> pd.Series:
    # \b = batas awal kata. Mencegah "bara" cocok dengan "kobaran" atau "membara",
    # dan "pala" cocok dengan "kepala". Awalan kata tetap cocok ("alang" -> "alang-alang").
    pola = "|".join(r"\b" + re.escape(k) for k in kata)
    return _teks(df, kolom).str.contains(pola, regex=True)


def _ambang_terpenuhi(n: int, total: int) -> bool:
    if total <= 0:
        return False
    if total == 1:  # mode satu laporan
        return n >= 1
    return n >= MIN_KASUS_AGREGAT and (100.0 * n / total) >= MIN_PERSEN_AGREGAT


def _evaluasi(rule: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
    total = len(df)
    tipe = rule["tipe"]
    status, bukti = STATUS_DUGAAN, "Belum ada data pendukung di sistem."

    if total == 0:
        return {"status": status, "bukti": "Tidak ada data."}

    if tipe in ("kata_kunci", "vegetasi", "area"):
        kolom = {"kata_kunci": "deskripsi_tempat", "vegetasi": "tipe_vegetasi", "area": "lokasi_area"}[tipe]
        n = int(_cocok(df, kolom, rule["kata"]).sum())
        persen = 100.0 * n / total
        bukti = f"{n} dari {total} laporan ({persen:.0f}%)"
        if _ambang_terpenuhi(n, total):
            status = STATUS_DATA
        else:
            bukti += " (di bawah ambang)"

    elif tipe == "jarak":
        jarak = pd.to_numeric(df.get("jarak_pemukiman_km"), errors="coerce")
        n = int((jarak <= rule["batas_km"]).sum())
        persen = 100.0 * n / total
        bukti = f"{n} dari {total} laporan ({persen:.0f}%) berjarak <= {rule['batas_km']} km"
        if _ambang_terpenuhi(n, total):
            status = STATUS_DATA
        else:
            bukti += " (di bawah ambang)"

    elif tipe == "durasi":
        if "waktu_selesai" in df.columns and "tanggal_lapor" in df.columns:
            mulai = pd.to_datetime(df["tanggal_lapor"], errors="coerce")
            selesai = pd.to_datetime(df["waktu_selesai"], errors="coerce")
            jam = ((selesai - mulai).dt.total_seconds() / 3600.0).dropna()
            jam = jam[jam >= 0]
            batas = 1 if total == 1 else MIN_SELESAI_DURASI
            if len(jam) >= batas:
                status = STATUS_DATA
                bukti = f"Median {jam.median():.1f} jam (n={len(jam)} laporan selesai)"
            else:
                bukti = f"Baru {len(jam)} laporan selesai (butuh minimal {batas})"

    elif tipe == "antrean":
        n = int((df.get("status_penanganan") == "Menunggu Penanganan").sum())
        persen = 100.0 * n / total
        bukti = f"{n} dari {total} laporan ({persen:.0f}%) menunggu penanganan"
        if persen >= rule["batas_persen"]:
            status = STATUS_DATA
        else:
            bukti += f" (di bawah ambang {rule['batas_persen']:.0f}%)"

    # tipe "dugaan": tidak dievaluasi, selalu Dugaan
    return {"status": status, "bukti": bukti}


def bangun_faktor(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Mengembalikan daftar faktor lengkap dengan status dan bukti dari data."""
    hasil = []
    for rule in FAKTOR:
        ev = _evaluasi(rule, df)
        hasil.append({
            "kategori": rule["kategori"],
            "singkat": rule["singkat"],
            "faktor": rule["faktor"],
            "keterangan": rule["keterangan"],
            "status": ev["status"],
            "bukti": ev["bukti"],
        })
    return hasil


def ringkas_faktor(faktor: List[Dict[str, Any]]) -> Dict[str, int]:
    n_data = sum(1 for f in faktor if f["status"] == STATUS_DATA)
    return {"total": len(faktor), "didukung_data": n_data, "dugaan": len(faktor) - n_data}


# ----------------------------------------------------------------------------
# VISUALISASI PLOTLY
# ----------------------------------------------------------------------------
def render_fishbone_plotly(faktor: List[Dict[str, Any]], judul: str = "Fishbone Diagram Kebakaran Gunung Klabat") -> go.Figure:
    """Menggambar diagram tulang ikan. Hijau solid = didukung data; oranye titik-titik = dugaan."""
    WARNA_DATA, WARNA_DUGAAN = "#2ECC71", "#F39C12"
    WARNA_TULANG, WARNA_EFEK = "#48CAE4", "#E63946"

    fig = go.Figure()

    # Tulang belakang
    fig.add_trace(go.Scatter(x=[0, 11], y=[0, 0], mode="lines",
                             line=dict(color=WARNA_EFEK, width=6),
                             hoverinfo="none", showlegend=False))
    fig.add_annotation(x=11.15, y=0, xanchor="left", showarrow=False,
                       text=f"<b>{EFEK}</b>", font=dict(size=12, color="#FFFFFF"),
                       bgcolor=WARNA_EFEK, bordercolor="#FFFFFF", borderwidth=2, borderpad=6)

    # Posisi cabang
    cabang = []
    for i, nama in enumerate(URUTAN_ATAS):
        cabang.append({"nama": nama, "x_base": 3.6 + i * 3.4, "arah": 1})
    for i, nama in enumerate(URUTAN_BAWAH):
        cabang.append({"nama": nama, "x_base": 5.3 + i * 3.4, "arah": -1})

    TINGGI, GESER = 3.4, 1.4   # tinggi cabang dan pergeseran ke kiri
    legend_data, legend_dugaan = False, False

    for c in cabang:
        xb, arah = c["x_base"], c["arah"]
        x_ujung, y_ujung = xb - GESER, arah * TINGGI
        fig.add_trace(go.Scatter(x=[xb, x_ujung], y=[0, y_ujung], mode="lines",
                                 line=dict(color=WARNA_TULANG, width=3),
                                 hoverinfo="none", showlegend=False))
        fig.add_annotation(x=x_ujung, y=y_ujung + arah * 0.4, showarrow=False,
                           text=f"<b>{c['nama'].upper()}</b>",
                           font=dict(size=12, color="#90E0EF"),
                           bgcolor="#0B192C", bordercolor=WARNA_TULANG, borderwidth=1, borderpad=4)

        sub = [f for f in faktor if f["kategori"] == c["nama"]]
        for idx, f in enumerate(sub):
            frac = (idx + 1) / (len(sub) + 1)
            fx = xb - GESER * frac
            fy = arah * TINGGI * frac
            ada_data = f["status"] == STATUS_DATA
            warna = WARNA_DATA if ada_data else WARNA_DUGAAN
            nama_legend = "Didukung data" if ada_data else "Dugaan (perlu verifikasi)"
            tampil_legend = (ada_data and not legend_data) or ((not ada_data) and not legend_dugaan)
            if ada_data:
                legend_data = True
            else:
                legend_dugaan = True

            hover = (f"<b>[{f['kategori']}] {f['faktor']}</b><br>"
                     f"Status: {f['status']}<br>Bukti: {f['bukti']}<br>{f['keterangan']}")
            fig.add_trace(go.Scatter(
                x=[fx - 0.35, fx], y=[fy, fy], mode="lines+markers",
                line=dict(color=warna, width=2, dash="solid" if ada_data else "dot"),
                marker=dict(size=[1, 8], color=warna),
                hovertext=hover, hoverinfo="text",
                name=nama_legend, legendgroup=nama_legend, showlegend=tampil_legend))

            label = "<br>".join(textwrap.wrap(f["singkat"], 24))
            fig.add_annotation(x=fx - 0.4, y=fy, xanchor="right", yanchor="middle",
                               showarrow=False, align="right", text=label,
                               font=dict(size=10, color="#E0E1DD"))

    fig.update_layout(
        title=dict(text=judul, font=dict(size=15, color="#FFFFFF")),
        plot_bgcolor="#0A1128", paper_bgcolor="#070D1F",
        xaxis=dict(visible=False, range=[-0.5, 13.8]),
        yaxis=dict(visible=False, range=[-4.6, 4.6]),
        margin=dict(l=10, r=10, t=50, b=10), height=640,
        legend=dict(orientation="h", yanchor="bottom", y=-0.02, xanchor="center", x=0.5,
                    font=dict(color="#FFFFFF", size=11)))
    return fig


# ----------------------------------------------------------------------------
# TAMPILAN STREAMLIT (dipanggil dari app.py, khusus peran Regu Pemadam & BPBD)
# ----------------------------------------------------------------------------
def render_tab_fishbone(df_all: pd.DataFrame) -> None:
    import streamlit as st

    st.markdown("#### Analisis Akar Masalah: Fishbone Diagram")
    st.caption(
        "Alat analisis untuk perencanaan pencegahan dan evaluasi penanganan, bukan untuk "
        "menentukan pengerahan regu. Status faktor dihitung otomatis dari data laporan."
    )

    if df_all is None or df_all.empty:
        st.info("Belum ada data laporan untuk dianalisis.")
        return

    if "is_simulated" in df_all.columns and int(df_all["is_simulated"].fillna(0).min()) == 1:
        st.warning("Seluruh data saat ini adalah simulasi. Diagram ini hanya mendemonstrasikan metode, "
                   "bukan temuan lapangan.")

    mode = st.radio("Cakupan analisis:", ["Seluruh laporan", "Satu laporan"], horizontal=True,
                    key="fishbone_mode")

    if mode == "Satu laporan":
        opsi = {f"{r['kode_laporan']} | {r['lokasi_area']} | {r['label_prioritas']}": r["id"]
                for _, r in df_all.iterrows()}
        pilihan = st.selectbox("Pilih laporan:", list(opsi.keys()), key="fishbone_laporan")
        df_pakai = df_all[df_all["id"] == opsi[pilihan]]
        judul = f"Fishbone: {pilihan.split(' | ')[0]}"
    else:
        df_pakai = df_all
        judul = f"Fishbone: seluruh laporan Gunung Klabat (n={len(df_all)})"

    faktor = bangun_faktor(df_pakai)
    ring = ringkas_faktor(faktor)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total faktor", ring["total"])
    c2.metric("Didukung data", ring["didukung_data"])
    c3.metric("Masih dugaan", ring["dugaan"])

    st.plotly_chart(render_fishbone_plotly(faktor, judul), use_container_width=True)

    tabel = pd.DataFrame(faktor)[["kategori", "faktor", "status", "bukti"]]
    tabel.columns = ["Kategori", "Faktor", "Status", "Bukti dari data"]
    st.dataframe(tabel, use_container_width=True, hide_index=True)

    with st.expander("Cara membaca dan batasan analisis"):
        st.markdown(
            f"- **Didukung data**: faktor muncul pada minimal {MIN_KASUS_AGREGAT} laporan dan "
            f"{MIN_PERSEN_AGREGAT:.0f}% data (mode seluruh laporan), atau minimal 1 kasus (mode satu laporan).\n"
            "- **Dugaan**: belum ada data di sistem. Faktor cuaca, sumber air, dan sumber daya "
            "selalu berstatus dugaan sampai ada sumber datanya (misalnya BMKG).\n"
            "- Pencocokan teks memakai kata kunci dan **belum menangani negasi**.\n"
            "- 'Didukung data' berarti muncul di laporan masyarakat, **bukan** terbukti sebagai penyebab. "
            "Penyebab pasti membutuhkan investigasi petugas."
        )
# Inisialisasi Database
init_db()
seed_klabat_database()

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="IGNIS Gunung Klabat - Minahasa Utara",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Folder upload gambar
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Inisialisasi Session State Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

# ==================== STYLING UI EYE-CATCHING & KONTRAS TINGGI ====================
st.markdown("""
<style>
    /* Global Base Styling */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d1b2a 0%, #08111e 90%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main Modern Header */
    .ignis-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-left: 6px solid #ff6b35;
        border-radius: 12px;
        padding: 20px 26px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    /* Cards */
    .ignis-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }

    /* Report Priority Cards with Vibrant Glowing Left Borders */
    .card-critical {
        background: #1e293b;
        border: 1px solid #475569;
        border-left: 6px solid #ef4444 !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2);
    }
    .card-high {
        background: #1e293b;
        border: 1px solid #475569;
        border-left: 6px solid #f97316 !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.2);
    }
    .card-medium {
        background: #1e293b;
        border: 1px solid #475569;
        border-left: 6px solid #f59e0b !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.15);
    }
    .card-low {
        background: #1e293b;
        border: 1px solid #475569;
        border-left: 6px solid #10b981 !important;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.15);
    }

    /* Badges */
    .badge-critical {
        background-color: #ef4444;
        color: #ffffff;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }
    .badge-high {
        background-color: #f97316;
        color: #ffffff;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }
    .badge-medium {
        background-color: #f59e0b;
        color: #0f172a;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }
    .badge-low {
        background-color: #10b981;
        color: #ffffff;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }

    /* CHATBOT HIGH-CONTRAST BUBBLE STYLING */
    .chat-bubble-assistant {
        background-color: #0f172a;
        border: 1px solid #38bdf8;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #ffffff !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
    }
    .chat-bubble-assistant b, .chat-bubble-assistant strong {
        color: #38bdf8 !important;
    }

    .chat-bubble-user {
        background-color: #0369a1;
        border: 1px solid #0284c7;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 12px;
        color: #ffffff !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        text-align: right;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b35 0%, #ea580c 100%);
        color: #ffffff !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 9px 20px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        box-shadow: 0 4px 14px rgba(255, 107, 53, 0.35);
        transform: translateY(-1px);
    }

    /* Form Submit Button — Selalu Terang Tanpa Perlu Hover */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #fb923c 0%, #ff6b35 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.55) !important;
        letter-spacing: 0.3px !important;
    }
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%) !important;
        box-shadow: 0 6px 24px rgba(255, 107, 53, 0.7) !important;
        transform: translateY(-1px) !important;
    }

    /* Input Fields */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        font-size: 14px;
    }

    /* Textarea — latar terang, teks hitam */
    .stTextArea textarea,
    div[data-testid="stTextArea"] textarea,
    .stTextArea div[data-baseweb="textarea"],
    .stTextArea div[data-baseweb="base-input"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        caret-color: #0f172a !important;
        opacity: 1 !important;
    }
    .stTextArea textarea {
        border: 1px solid #94a3b8 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        pointer-events: auto !important;
    }
    .stTextArea textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.5) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        border-radius: 6px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
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
# FITUR 1: HALAMAN LOGIN SISTEM
# ==============================================================================
def render_login_view():
    st.markdown("""
    <div style="max-width: 580px; margin: 40px auto 20px auto; text-align: center;">
        <div style="font-size: 38px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
            IGNIS <span style="color: #ff6b35;">KLABAT</span>
        </div>
        <p style="color: #94a3b8; font-size: 14px; margin-top: 6px;">
            Sistem Informasi Mitigasi Kebakaran Hutan Gunung Klabat, Minahasa Utara
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_center = st.columns([1, 1.8, 1])[1]
    with c_center:
        st.markdown("""
        <div class="ignis-card" style="border-top: 4px solid #ff6b35;">
            <h3 style="margin: 0 0 6px 0; color: #ffffff; font-size: 18px; text-align: center;">Autentikasi Pengguna</h3>
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin-bottom: 20px;">
                Silakan masuk sesuai dengan kewenangan peran Anda.
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_warga, tab_damkar = st.tabs(["Masyarakat & Pendaki", "Regu Pemadam & BPBD"])

        # TAB 1: LOGIN WARGA / PENDAKI
        with tab_warga:
            st.markdown("<p style='font-size: 13px; color: #cbd5e1;'>Akses untuk warga lereng atau pendaki yang hendak melapor kebakaran serta konsultasi evakuasi darurat.</p>", unsafe_allow_html=True)
            w_user = st.text_input("Username:", value="warga", key="w_user")
            w_pass = st.text_input("Kata Sandi:", type="password", value="warga123", key="w_pass")
            
            if st.button("Masuk Sebagai Masyarakat / Pendaki", use_container_width=True, key="btn_login_warga"):
                if w_user.strip() and w_pass.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_role = "masyarakat"
                    st.session_state.username = w_user.strip()
                    st.success("Berhasil masuk ke Portal Masyarakat!")
                    st.rerun()
                else:
                    st.error("Silakan masukkan username dan kata sandi.")

        # TAB 2: LOGIN PETUGAS DAMKAR & BPBD
        with tab_damkar:
            st.markdown("<p style='font-size: 13px; color: #cbd5e1;'>Akses khusus personel Satgas Damkar Airmadidi, BPBD Minahasa Utara, dan Pos Registrasi Klabat.</p>", unsafe_allow_html=True)
            d_user = st.text_input("ID Personel / Username:", value="damkar", key="d_user")
            d_pass = st.text_input("Kata Sandi Petugas:", type="password", value="damkar123", key="d_pass")
            
            if st.button("Masuk Sebagai Regu Pemadam & BPBD", use_container_width=True, key="btn_login_damkar"):
                if d_user.strip() in ["damkar", "bpbd", "petugas", "admin"] and d_pass.strip() in ["damkar123", "minut112", "admin123"]:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "damkar"
                    st.session_state.username = d_user.strip().upper()
                    st.success("Autentikasi Petugas Berhasil!")
                    st.rerun()
                else:
                    st.error("Kredensial tidak valid. Gunakan username 'damkar' dan sandi 'damkar123'.")

        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 6px; border: 1px solid #334155; margin-top: 15px; font-size: 11px; color: #94a3b8; text-align: center;">
            Kredensial Pengujian: <b>warga</b> (sandi: warga123) | <b>damkar</b> (sandi: damkar123)
        </div>
        """, unsafe_allow_html=True)

# Jika belum login, tampilkan halaman login
if not st.session_state.logged_in:
    render_login_view()
    st.stop()

# ==============================================================================
# HEADER SAAT LOGIN (DILENGKAPI TOMBOL LOGOUT)
# ==============================================================================
role_badge_text = "PORTAL MASYARAKAT & PENDAKI" if st.session_state.user_role == "masyarakat" else "PUSAT KOMANDO REGU PEMADAM & BPBD"
role_badge_color = "#38bdf8" if st.session_state.user_role == "masyarakat" else "#ff6b35"

st.markdown(f"""
<div class="ignis-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff;">
                IGNIS - Mitigasi Kebakaran Hutan Gunung Klabat
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                Ruang Lingkup: Kawasan Gunung Klabat (1.995 mdpl), Minahasa Utara, Sulawesi Utara
            </div>
        </div>
        <div style="text-align: right;">
            <span style="background-color: {role_badge_color}; color: #0f172a; font-weight: 800; font-size: 11px; padding: 4px 10px; border-radius: 4px; letter-spacing: 0.5px;">
                {role_badge_text}
            </span>
            <div style="font-size: 12px; color: #f1f5f9; margin-top: 5px;">
                Pengguna: <b>{st.session_state.username}</b>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tombol Logout di baris navigasi
col_head_space, col_logout = st.columns([6, 1])
with col_logout:
    if st.button("Keluar (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()

st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

# ==============================================================================
# PERAN 1: MASYARAKAT / PENDAKI (USER 1)
# ==============================================================================
if st.session_state.user_role == "masyarakat":
    col_lapor, col_chat = st.columns([1.1, 1], gap="large")

    # ---------- FORMULIR INFORMASI KEBAKARAN (TANPA PILIH KEPARAHAN) ----------
    with col_lapor:
        st.markdown("""
        <div class="ignis-card" style="border-top: 4px solid #ff6b35;">
            <h3 style="margin: 0 0 4px 0; color: #ffffff; font-size: 18px;">Formulir Informasi Kebakaran Masyarakat</h3>
            <p style="color: #94a3b8; font-size: 12px; margin: 0 0 16px 0;">
                Kirim informasi titik api yang Anda lihat. AI akan menganalisis otomatis tingkat prioritas sehingga Anda tidak perlu memilih tingkat keparahan.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_lapor_masyarakat_ai", clear_on_submit=False):
            st.markdown("##### 1. Identitas Pelapor")
            nama_user = st.text_input("Nama Lengkap Pelapor *", placeholder="Contoh: Rendy Kaligis", value=st.session_state.username if st.session_state.username != "warga" else "")
            kontak_user = st.text_input("Nomor Telepon / WhatsApp Aktif", placeholder="Contoh: 081244556677")

            st.markdown("##### 2. Titik Lokasi Kebakaran")
            preset_choice = st.selectbox(
                "Pilih Titik Patokan Gunung Klabat (Opsional untuk Membantu Titik):",
                list(PRESET_PATOKAN_KLABAT.keys())
            )
            p_lat, p_lon, p_area, p_jarak, p_veg = PRESET_PATOKAN_KLABAT[preset_choice]

            default_gmaps = f"https://www.google.com/maps?q={p_lat:.5f},{p_lon:.5f}" if p_lat != 1.4650 else "https://www.google.com/maps?q=1.4658,124.9935"
            link_lokasi = st.text_input(
                "Link Lokasi Terbakar (Tautan Google Maps / Share Location) *",
                value=default_gmaps,
                placeholder="https://maps.app.goo.gl/... atau koordinat"
            )

            c_lat, c_lon = st.columns(2)
            with c_lat:
                lat_input = st.number_input("Latitude", value=float(p_lat), format="%.5f")
            with c_lon:
                lon_input = st.number_input("Longitude", value=float(p_lon), format="%.5f")

            st.markdown("##### 3. Bukti Foto & Deskripsi Kejadian")
            
            tab_file, tab_url = st.tabs(["Unggah File Foto", "Gunakan Tautan Foto"])
            uploaded_image_path = None
            
            with tab_file:
                uploaded_file = st.file_uploader("Pilih foto kebakaran dari galeri/kamera:", type=["jpg", "jpeg", "png", "webp"])
                if uploaded_file is not None:
                    filename = f"klb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    save_path = os.path.join(UPLOAD_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    uploaded_image_path = save_path
                    st.image(uploaded_file, caption="Pratinjau Foto Bukti", use_container_width=True)

            with tab_url:
                foto_url_input = st.text_input(
                    "Tautan Gambar Kebakaran (URL):",
                    value="https://images.unsplash.com/photo-1542385151-efd9000785a0?w=800&auto=format&fit=crop&q=60"
                )

            deskripsi_tempat = st.text_area(
                "Deskripsi Tempat & Kondisi Api *",
                placeholder="Ceritakan patokan tempat (misal: dekat Pos 3 atau dekat kebun cengkeh warga), kondisi asap, apakah ada pendaki yang turun, atau jarak ke pemukiman...",
                height=110,
                value="Kepulan asap membubung tinggi di semak lereng arah jalur pendakian. Angin bertiup cukup kencang ke arah atas lereng dan dikhawatirkan membahayakan pendaki."
            )

            # Estimasi jarak terdekat
            jarak_input = st.number_input("Perkiraan Jarak Titik Api ke Pemukiman Warga (km):", value=float(p_jarak), min_value=0.1, max_value=20.0, step=0.1)

            st.markdown("""
            <div style="background-color: rgba(56, 189, 248, 0.1); border-left: 4px solid #38bdf8; padding: 10px 14px; border-radius: 4px; font-size: 12px; color: #bae6fd; margin-bottom: 12px;">
                Prioritas penanganan akan dihitung secara otomatis oleh AI (Gemini 3.8 Flash) berdasarkan deskripsi, ancaman keselamatan warga, dan jalur pendaki Gunung Klabat.
            </div>
            """, unsafe_allow_html=True)

            btn_submit = st.form_submit_button("Kirim Laporan Kebakaran Sekarang", use_container_width=True)

        if btn_submit:
            if not nama_user.strip() or not deskripsi_tempat.strip() or not link_lokasi.strip():
                st.error("Mohon lengkapi Nama Pelapor, Link Lokasi, dan Deskripsi Tempat Kebakaran.")
            else:
                final_image = uploaded_image_path if uploaded_image_path else foto_url_input
                area_nama = p_area if p_lat != 1.4650 else "Kawasan Lereng Gunung Klabat"

                with st.spinner("AI sedang menganalisis tingkat prioritas risiko laporan Anda..."):
                    # Panggil AI Classifier otomatis (Gemini 3.8 Flash)
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
                    st.success(f"Laporan berhasil dikirim ke Posko Damkar & BPBD Minahasa Utara! (Kode: KLB-{datetime.now().year}-{new_id:03d})")
                    
                    st.markdown(f"""
                    <div style="background-color: #1e293b; border-left: 5px solid #ff6b35; padding: 14px; border-radius: 6px; margin-top: 10px;">
                        <div style="font-size: 13px; font-weight: bold; color: #ff6b35;">HASIL PENILAIAN PRIORITAS AI ({ai_result['source']}):</div>
                        <div style="font-size: 15px; font-weight: bold; color: #ffffff; margin: 4px 0;">
                            Prioritas: {ai_result['label_prioritas']} (Skor: {ai_result['skor_prioritas']}/100)
                        </div>
                        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.5;">
                            {ai_result['alasan_prioritas']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ---------- CHATBOT AI ANTI-PANIK (KONTRAS TINGGI & TULISAN JELAS) ----------
    with col_chat:
        st.markdown("""
        <div class="ignis-card" style="border-top: 4px solid #38bdf8;">
            <h3 style="margin: 0 0 4px 0; color: #ffffff; font-size: 18px;">Asisten Tanggap Darurat & Panduan Anti-Panik</h3>
            <p style="color: #94a3b8; font-size: 12px; margin: 0 0 16px 0;">
                Konsultasikan situasi Anda untuk mendapatkan instruksi penyelamatan diri dan nomor darurat resmi.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if "klabat_chat_messages" not in st.session_state:
            st.session_state.klabat_chat_messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Halo. Saya adalah Asisten Darurat IGNIS untuk kawasan Gunung Klabat.\n\n"
                        "Jika Anda melihat kebakaran atau berada di sekitar kepulan asap:\n"
                        "1. Tarik napas perlahan dan tetap tenang. Jangan panik.\n"
                        "2. Segera lindungi saluran pernapasan dengan kain basah.\n"
                        "3. Tanyakan langkah evakuasi atau nomor telepon posko yang dapat Anda hubungi sekarang."
                    )
                }
            ]

        # Tombol Pertanyaan Cepat
        st.markdown("<div style='font-size: 11px; color: #94a3b8; font-weight: bold; margin-bottom: 6px;'>PANDUAN DARURAT CEPAT:</div>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        quick_ask = None
        with q1:
            if st.button("Saya di Jalur Pendakian", use_container_width=True):
                quick_ask = "Saya sedang berada di jalur pendakian Gunung Klabat dan melihat asap kebakaran. Apa tindakan pertama yang harus saya ambil?"
        with q2:
            if st.button("Api Dekat Pemukiman", use_container_width=True):
                quick_ask = "Api membakar semak dekat pekarangan rumah warga lereng. Tindakan apa yang aman untuk keluarga?"
        with q3:
            if st.button("Nomor Posko Darurat", use_container_width=True):
                quick_ask = "Berikan nomor telepon darurat Damkar, BPBD Minahasa Utara, dan Pos Registrasi Klabat."

        # Kotak Tampilan Chat Bubble Kontras Tinggi
        chat_box = st.container(height=390)
        with chat_box:
            for m in st.session_state.klabat_chat_messages:
                if m["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">
                        <b>Anda:</b><br>{m['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-bubble-assistant">
                        <span style="background-color: #0284c7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">ASISTEN RESMI IGNIS</span>
                        <div style="margin-top: 8px;">
                            {m['content'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Input Chat
        user_chat_input = st.chat_input("Tulis pertanyaan atau kondisi darurat Anda...")
        if quick_ask:
            user_chat_input = quick_ask

        if user_chat_input:
            st.session_state.klabat_chat_messages.append({"role": "user", "content": user_chat_input})
            with chat_box:
                st.markdown(f"""
                <div class="chat-bubble-user">
                    <b>Anda:</b><br>{user_chat_input}
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Menyiapkan panduan tindakan aman..."):
                    resp = get_anti_panic_response(user_chat_input)
                    st.markdown(f"""
                    <div class="chat-bubble-assistant">
                        <span style="background-color: #0284c7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">ASISTEN RESMI IGNIS</span>
                        <div style="margin-top: 8px;">
                            {resp['answer'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.klabat_chat_messages.append({"role": "assistant", "content": resp["answer"]})
            st.rerun()

        # Kontak Darurat
        with st.expander("Kontak Darurat Resmi Posko Minahasa Utara", expanded=False):
            st.markdown("""
            - **Call Center Kedaruratan Minahasa Utara:** 112 (Bebas Pulsa)
            - **Posko Damkar Minahasa Utara (Airmadidi):** (0431) 891-113
            - **BPBD Minahasa Utara:** (0431) 892-112 / 0811-432-112
            - **Basarnas Manado (Evakuasi Hutan Klabat):** 115 / (0431) 812-111
            - **Polsek Airmadidi:** (0431) 891-110
            - **Pos Registrasi Pendakian Klabat (Airmadidi Atas):** 0812-4455-6677
            """)

# ==============================================================================
# PERAN 2: REGU PEMADAM & BPBD (USER 2)
# ==============================================================================
else:
    df_aktif = get_laporan_aktif()
    df_riwayat = get_riwayat_selesai()
    df_all = get_all_laporan_prioritas()

    total_aktif = len(df_aktif)
    total_selesai = len(df_riwayat)
    total_kritis = int((df_aktif["label_prioritas"] == "Kritis").sum())
    total_tinggi = int((df_aktif["label_prioritas"] == "Tinggi").sum())

    st.markdown("""
    <div class="ignis-card" style="border-top: 4px solid #ff6b35;">
        <h3 style="margin: 0 0 4px 0; color: #ffffff; font-size: 18px;">Pusat Komando & Disposisi Regu Pemadam Gunung Klabat</h3>
        <p style="color: #94a3b8; font-size: 12px; margin: 0 0 16px 0;">
            Pantau laporan kebakaran aktif yang diurutkan AI berdasarkan prioritas risiko, lakukan pemadaman, dan tandai saat api sudah berhasil diatasi.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics Eye-Catching
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="ignis-card" style="text-align: center; border-bottom: 3px solid #38bdf8; padding: 14px;">
            <div style="font-size: 11px; color: #94a3b8; font-weight: bold;">ANTREAN AKTIF</div>
            <div style="font-size: 28px; font-weight: bold; color: #38bdf8; margin-top: 4px;">{total_aktif}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="ignis-card" style="text-align: center; border-bottom: 3px solid #ef4444; padding: 14px;">
            <div style="font-size: 11px; color: #ef4444; font-weight: bold;">PRIORITAS KRITIS</div>
            <div style="font-size: 28px; font-weight: bold; color: #ef4444; margin-top: 4px;">{total_kritis}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="ignis-card" style="text-align: center; border-bottom: 3px solid #f97316; padding: 14px;">
            <div style="font-size: 11px; color: #f97316; font-weight: bold;">PRIORITAS TINGGI</div>
            <div style="font-size: 28px; font-weight: bold; color: #f97316; margin-top: 4px;">{total_tinggi}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="ignis-card" style="text-align: center; border-bottom: 3px solid #10b981; padding: 14px;">
            <div style="font-size: 11px; color: #10b981; font-weight: bold;">SUDAH DIATASI</div>
            <div style="font-size: 28px; font-weight: bold; color: #10b981; margin-top: 4px;">{total_selesai}</div>
        </div>
        """, unsafe_allow_html=True)

    tab_aktif, tab_histori, tab_peta, tab_fishbone = st.tabs([
        f"Antrean Penanganan Aktif ({total_aktif})",
        f"Riwayat Penanganan Selesai ({total_selesai})",
        "Peta Geospasial Gunung Klabat",
        "Analisis Akar Masalah (Fishbone)"
    ])

    # ==================== TAB 1: ANTREAN AKTIF (URUTAN AI) ====================
    with tab_aktif:
        st.markdown("#### Antrean Laporan Kebakaran Aktif di Lapangan")
        st.caption("AI otomatis mengurutkan laporan yang paling mendesak di posisi teratas. Setelah api padam, klik tombol 'Tandai Sudah Diatasi' untuk memindahkannya ke tab riwayat.")

        if df_aktif.empty:
            st.success("Seluruh titik kebakaran di kawasan Gunung Klabat telah berhasil diatasi! Tidak ada antrean aktif saat ini.")
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

                with st.container():
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <span style="font-size: 17px; font-weight: bold; color: #ffffff;">
                                    {r['kode_laporan']} - {r['lokasi_area']}
                                </span>
                                <span style="font-size: 12px; color: #94a3b8; margin-left: 12px;">
                                    Waktu Lapor: {r['tanggal_lapor']}
                                </span>
                            </div>
                            <div>
                                <span class="{badge_class}">PRIORITAS {prio_label.upper()} (SKOR: {r['skor_prioritas']})</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c_info, c_media, c_action = st.columns([1.4, 1, 1.3])

                    with c_info:
                        st.markdown(f"**Nama Pelapor:** {r['nama_user']} | Kontak: `{r.get('kontak_user') or 'Tanpa kontak'}`")
                        st.markdown(f"**Deskripsi Kejadian:** *\"{r['deskripsi_tempat']}\"*")
                        st.markdown(f"**Alasan Prioritas AI:** <span style='color: #38bdf8; font-weight: 500;'>{r['alasan_prioritas']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Vegetasi:** {r['tipe_vegetasi']} | **Jarak Pemukiman:** {r['jarak_pemukiman_km']} km")
                        st.markdown(f"**Status Saat Ini:** <span style='color: #f59e0b; font-weight: bold;'>{r['status_penanganan']}</span>", unsafe_allow_html=True)
                        
                        link_gmaps = r['link_lokasi']
                        st.markdown(f"📍 **Navigasi Armada:** [Buka Rute di Google Maps]({link_gmaps})")

                    with c_media:
                        st.markdown("**Bukti Foto Kebakaran:**")
                        gambar_src = r['gambar_kebakaran']
                        if gambar_src:
                            try:
                                if os.path.exists(gambar_src):
                                    img = Image.open(gambar_src)
                                    st.image(img, caption=r['kode_laporan'], use_container_width=True)
                                else:
                                    st.image(gambar_src, caption=r['kode_laporan'], use_container_width=True)
                            except Exception:
                                st.caption("Foto bukti tidak dapat ditampilkan.")
                        else:
                            st.caption("Tidak ada foto lampiran.")

                    with c_action:
                        st.markdown("**Tindakan Petugas Pemadam:**")
                        
                        # Input catatan penyelesaian
                        catatan_selesai = st.text_input(
                            "Catatan Hasil Pemadaman / Tindakan Tim:",
                            value=r.get('catatan_tim', ''),
                            placeholder="Misal: Api berhasil dipadamkan regu Damkar Airmadidi...",
                            key=f"note_active_{r['id']}"
                        )

                        # TOMBOL UTAMA: TANDAI SUDAH DIATASI
                        if st.button(f"Tandai Sudah Diatasi ({r['kode_laporan']})", key=f"btn_done_{r['id']}", use_container_width=True):
                            catatan_final = catatan_selesai.strip() if catatan_selesai.strip() else "Kebakaran telah berhasil dipadamkan oleh regu lapangan."
                            tandai_sudah_diatasi(r['id'], catatan_final)
                            st.success(f"Laporan {r['kode_laporan']} telah ditandai SUDAH DIATASI dan dipindahkan ke Riwayat!")
                            st.rerun()

                        # Update Status Bertahap Lainnya (Opsional)
                        with st.expander("Ubah Status Operasional Lainnya", expanded=False):
                            status_options = ["Menunggu Penanganan", "Tim Menuju Lokasi", "Sedang Dipadamkan"]
                            cur_idx = status_options.index(r['status_penanganan']) if r['status_penanganan'] in status_options else 0
                            new_st = st.selectbox(
                                "Status Operasional:",
                                status_options,
                                index=cur_idx,
                                key=f"sel_st_{r['id']}"
                            )
                            if st.button(f"Perbarui Status Jadi '{new_st}'", key=f"btn_update_{r['id']}"):
                                update_status_pemadaman(r['id'], new_st, catatan_selesai)
                                st.success("Status operasional diperbarui!")
                                st.rerun()

                    st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 15px 0 20px 0;'>", unsafe_allow_html=True)

    # ==================== TAB 2: RIWAYAT PENANGANAN (SUDAH DIATASI) ====================
    with tab_histori:
        st.markdown("#### Riwayat Arsip Kebakaran yang Telah Berhasil Diatasi")
        st.caption("Daftar seluruh insiden kebakaran di kawasan Gunung Klabat yang telah selesai dipadamkan dan ditangani oleh regu pemadam.")

        if df_riwayat.empty:
            st.info("Belum ada riwayat penanganan selesai. Laporan yang ditandai 'Sudah Diatasi' pada Tab 1 akan otomatis masuk ke sini.")
        else:
            for idx, r in df_riwayat.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #0f172a; border-left: 6px solid #10b981; border-radius: 8px; padding: 18px; margin-bottom: 16px; border: 1px solid #334155;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div>
                                <span style="font-size: 17px; font-weight: bold; color: #ffffff;">
                                    {r['kode_laporan']} - {r['lokasi_area']}
                                </span>
                                <span style="font-size: 12px; color: #10b981; margin-left: 12px; font-weight: bold;">
                                    SELESAI / PADAM
                                </span>
                            </div>
                            <div>
                                <span style="background-color: #10b981; color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold;">
                                    SUDAH DIATASI
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c_h_info, c_h_media, c_h_time = st.columns([1.5, 1, 1.2])

                    with c_h_info:
                        st.markdown(f"**Nama Pelapor:** {r['nama_user']} | Kontak: `{r.get('kontak_user') or 'Tanpa kontak'}`")
                        st.markdown(f"**Deskripsi Kejadian:** *\"{r['deskripsi_tempat']}\"*")
                        st.markdown(f"**Vegetasi:** {r['tipe_vegetasi']} | Jarak Pemukiman: {r['jarak_pemukiman_km']} km")
                        st.markdown(f"**Catatan Petugas Pemadam:** <span style='color: #10b981; font-weight: bold;'>\"{r.get('catatan_tim') or 'Penanganan selesai dan kondisi aman.'}\"</span>", unsafe_allow_html=True)
                        
                        link_gmaps = r['link_lokasi']
                        st.markdown(f"📍 [Lihat Koordinat di Google Maps]({link_gmaps})")

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
                        <div style="background-color: #1e293b; padding: 12px; border-radius: 6px; font-size: 12px; border: 1px solid #334155;">
                            <b>Waktu Lapor Masuk:</b><br>{r['tanggal_lapor']}<br><br>
                            <b>Waktu Berhasil Diatasi:</b><br><span style="color: #10b981; font-weight: bold;">{r.get('waktu_selesai') or 'Telah diselesaikan'}</span><br><br>
                            <b>Skor Prioritas Awal:</b> {r['skor_prioritas']} ({r['label_prioritas']})
                        </div>
                        """, unsafe_allow_html=True)

                        # Opsi buka kembali jika api muncul lagi
                        if st.button(f"Buka Kembali Kasus (Rekurensi Api)", key=f"btn_reopen_{r['id']}"):
                            update_status_pemadaman(r['id'], "Sedang Dipadamkan", "Kasus dibuka kembali karena titik api menyala kembali.")
                            st.warning(f"Kasus {r['kode_laporan']} telah dibuka kembali ke Antrean Aktif.")
                            st.rerun()

                    st.markdown("<hr style='border: none; border-top: 1px dashed #334155; margin: 15px 0 20px 0;'>", unsafe_allow_html=True)

    # ==================== TAB 3: PETA GEOSPASIAL GUNUNG KLABAT ====================
    with tab_peta:
        st.markdown("#### Peta Titik Sebaran Kebakaran Gunung Klabat")
        st.caption("Pusat pantauan: Puncak Gunung Klabat (1.995 mdpl) dan seluruh jalur lereng Minahasa Utara.")

        klabat_map = render_klabat_folium_map(df_all)
        st_folium(klabat_map, width="100%", height=560, returned_objects=[])

        st.markdown("""
        <div style="background-color: #1e293b; padding: 12px 16px; border-radius: 8px; font-size: 12px; margin-top: 12px; border: 1px solid #334155;">
            <b>Legenda Status Titik di Peta:</b><br>
            <span style="color: #ef4444; font-weight: bold;">● Merah:</span> Prioritas Kritis Aktif (Dekat pemukiman Airmadidi / Kaki Dian / Suwaan)<br>
            <span style="color: #f97316; font-weight: bold;">● Oranye:</span> Prioritas Tinggi Aktif (Jalur pendakian aktif Pos 1-6 atau kebun cengkeh warga)<br>
            <span style="color: #f59e0b; font-weight: bold;">● Kuning:</span> Prioritas Sedang Aktif (Savana puncak atau kawasan lereng terisolasi)<br>
            <span style="color: #10b981; font-weight: bold;">● Hijau Zamrud:</span> <b>Sudah Berhasil Diatasi / Api Padam</b>
        </div>
        """, unsafe_allow_html=True)

    # ==================== TAB 4: FISHBONE (KHUSUS PETUGAS) ====================
    with tab_fishbone:
        render_tab_fishbone(df_all) 