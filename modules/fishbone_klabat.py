"""
Fishbone Diagram (Ishikawa) khusus Kebakaran Hutan & Lahan Gunung Klabat.

PRINSIP UTAMA
-------------
Status setiap faktor TIDAK ditulis manual, melainkan dihitung dari isi database:
  - "Didukung data" : ada bukti terukur di tabel laporan (jumlah/persentase/median).
  - "Dugaan"        : belum ada data pendukung; perlu investigasi lapangan.

Faktor yang tidak punya data di sistem (misalnya cuaca, ketersediaan air) SELALU
berstatus "Dugaan" sampai ada sumber datanya (contoh: data BMKG).

BATASAN YANG HARUS DISEBUT SAAT PRESENTASI
------------------------------------------
1. Pencocokan teks memakai kata kunci dan belum menangani negasi
   (kalimat "bukan akibat puntung rokok" tetap terhitung).
2. Laporan masyarakat belum diverifikasi lapangan, sehingga "Didukung data"
   berarti "muncul di data laporan", bukan "terbukti penyebabnya".
3. Jika seluruh data bersifat simulasi, hasilnya hanya demonstrasi metode.
"""

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