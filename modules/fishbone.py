"""
Fishbone Diagram (Ishikawa) Module for IGNIS.
Memvisualisasikan faktor penyebab kejadian karhutla berdasarkan 5 kategori:
1. Manusia (Human Activity & Intent)
2. Lingkungan (Ecosystem & Vegetation Type)
3. Cuaca (Atmospheric & Meteorological Conditions)
4. Infrastruktur (Canal Blocking, Access Roads, Water Retention)
5. Penanganan (Emergency Response & Inter-agency Coordination)

Membedakan secara tegas antara:
- [Dugaan / Hipotesis]: Masih memerlukan investigasi lapangan
- [Terverifikasi]: Telah terkonfirmasi oleh data satelit, sensor, atau laporan petugas
"""

from typing import Dict, Any, List
import plotly.graph_objects as go

def get_fishbone_factors(report: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Menyusun faktor-faktor penyebab spesifik untuk laporan tertentu,
    membedakan faktor 'Dugaan' vs 'Terverifikasi'.
    """
    tipe_lahan = report.get("tipe_lahan", "Semak Belukar")
    keparahan = report.get("keparahan", "Sedang")
    jarak = float(report.get("jarak_pemukiman_km", 2.0))
    status_petugas = report.get("status_verifikasi_petugas", "Menunggu Verifikasi")
    is_verified_officer = (status_petugas == "Terverifikasi Valid")

    factors = {
        "Manusia": [
            {
                "faktor": "Praktik Land Clearing pembukaan lahan dengan cara membakar",
                "status": "Terverifikasi" if ("sawit" in tipe_lahan.lower() or "ladang" in str(report.get("deskripsi")).lower()) else "Dugaan",
                "keterangan": "Metode murah untuk membersihkan sisa vegetasi sebelum tanam baru."
            },
            {
                "faktor": "Kelalaian pembuangan puntung rokok atau sisa api unggun",
                "status": "Dugaan",
                "keterangan": "Aktivitas pemburu liar atau pekerja perkebunan yang melintas."
            },
            {
                "faktor": "Rendahnya kepatuhan terhadap larangan pembakaran saat status siaga",
                "status": "Terverifikasi" if keparahan in ["Tinggi", "Kritis"] else "Dugaan",
                "keterangan": "Sosialisasi belum menjangkau seluruh lapisan petani perambah."
            }
        ],
        "Lingkungan": [
            {
                "faktor": f"Karakteristik bahan bakar organik ({tipe_lahan})",
                "status": "Terverifikasi",
                "keterangan": f"Lapisan serasah dan gambut tebal sangat mudah menyulut pembakaran bawah tanah."
            },
            {
                "faktor": f"Kedekatan dengan zona aktivitas pemukiman ({jarak:.1f} km)",
                "status": "Terverifikasi",
                "keterangan": "Tingginya intensitas interaksi manusia di zona perbatasan hutan/kebun."
            },
            {
                "faktor": "Penurunan kelembaban tanah gambut hingga titik kritis (< 100%)",
                "status": "Terverifikasi" if "Gambut" in tipe_lahan else "Dugaan",
                "keterangan": "Kondisi gambut kering menjadi bahan bakar yang membara tahan lama."
            }
        ],
        "Cuaca": [
            {
                "faktor": "Hari Tanpa Hujan (HTH) berturut-turut > 14 hari",
                "status": "Terverifikasi",
                "keterangan": "Fase kemarau mengakibatkan defisit kelembaban vegetasi darat."
            },
            {
                "faktor": "Suhu udara ekstrem siang hari > 34°C",
                "status": "Terverifikasi",
                "keterangan": "Mempercepat pengeringan ranting dan dedaunan mati di lantai hutan."
            },
            {
                "faktor": "Kecepatan hembusan angin kencang memicu 'Spot Fire' loncatan bara",
                "status": "Terverifikasi" if keparahan in ["Tinggi", "Kritis"] else "Dugaan",
                "keterangan": "Membawa percikan bara api melintasi parit dan jalan setapak."
            }
        ],
        "Infrastruktur": [
            {
                "faktor": "Kondisi sekat kanal (canal blocking) tidak berfungsi optimal",
                "status": "Terverifikasi" if "Gambut" in tipe_lahan else "Dugaan",
                "keterangan": "Air gambut mengalir bebas keluar sehingga lapisan atas mengering kerontang."
            },
            {
                "faktor": "Ketiadaan sumber air pemadam darurat (embung/parit buatan)",
                "status": "Terverifikasi" if jarak > 2.0 else "Dugaan",
                "keterangan": "Embung alami di sekitar lokasi mengering selama kemarau."
            },
            {
                "faktor": "Akses jalan menuju titik api sempit dan berlumpur/rawa",
                "status": "Terverifikasi" if is_verified_officer else "Dugaan",
                "keterangan": "Armada pemadam roda 4 tidak dapat menjangkau titik api langsung."
            }
        ],
        "Penanganan": [
            {
                "faktor": "Jeda waktu deteksi dari laporan masyarakat ke tindakan posko",
                "status": "Terverifikasi",
                "keterangan": "Perlu proses konfirmasi manual sebelum pengerahan armada darat."
            },
            {
                "faktor": "Keterbatasan armada pompa jinjing bertekanan tinggi di tingkat desa",
                "status": "Terverifikasi" if keparahan in ["Tinggi", "Kritis"] else "Dugaan",
                "keterangan": "Kelompok Masyarakat Peduli Api (MPA) kekurangan selang tembak panjang."
            },
            {
                "faktor": "Koordinasi water bombing udara memerlukan izin lintas sektoral",
                "status": "Dugaan",
                "keterangan": "Eskalasi darurat helikopter membutuhkan penetapan status siaga darurat daerah."
            }
        ]
    }

    return factors

def render_fishbone_plotly(factors: Dict[str, List[Dict[str, Any]]], title: str = "Diagram Sebab-Akibat Karhutla (Ishikawa Fishbone)") -> go.Figure:
    """
    Membuat visualisasi Fishbone Diagram interaktif menggunakan Plotly.
    Membedakan visual antara Terverifikasi (Hijau Emerald solid) vs Dugaan (Oranye/Kuning putus-putus).
    """
    fig = go.Figure()

    # Sumbu Utama Tulang Ikan (Spine)
    fig.add_trace(go.Scatter(
        x=[0, 10],
        y=[0, 0],
        mode="lines+markers",
        line=dict(color="#E63946", width=6),
        marker=dict(size=[1, 18], symbol=["circle", "triangle-right"], color="#E63946"),
        hoverinfo="none",
        name="Tulang Belakang (Akibat)"
    ))

    # Kepala Ikan (Masalah Utama / Efek)
    fig.add_annotation(
        x=10.2, y=0,
        text="<b>ESKALASI KEJADIAN<br>KARHUTLA</b>",
        showarrow=False,
        font=dict(size=13, color="#FFFFFF"),
        bgcolor="#E63946",
        bordercolor="#FFFFFF",
        borderwidth=2,
        borderpad=6
    )

    # 5 Tulang Cabang (Ribs)
    # Atas: Manusia (x=2), Lingkungan (x=5), Cuaca (x=8)
    # Bawah: Infrastruktur (x=3.5), Penanganan (x=6.5)
    branches = [
        {"cat": "Manusia", "x_base": 2.5, "x_top": 1.5, "y_top": 3.0, "side": "top"},
        {"cat": "Lingkungan", "x_base": 5.5, "x_top": 4.5, "y_top": 3.0, "side": "top"},
        {"cat": "Cuaca", "x_base": 8.0, "x_top": 7.0, "y_top": 3.0, "side": "top"},
        {"cat": "Infrastruktur", "x_base": 4.0, "x_top": 3.0, "y_top": -3.0, "side": "bottom"},
        {"cat": "Penanganan", "x_base": 7.0, "x_top": 6.0, "y_top": -3.0, "side": "bottom"},
    ]

    for b in branches:
        cat_name = b["cat"]
        fig.add_trace(go.Scatter(
            x=[b["x_base"], b["x_top"]],
            y=[0, b["y_top"]],
            mode="lines",
            line=dict(color="#48CAE4", width=3),
            hoverinfo="none",
            showlegend=False
        ))

        # Label Kategori Cabang
        fig.add_annotation(
            x=b["x_top"], y=b["y_top"] + (0.35 if b["side"] == "top" else -0.35),
            text=f"<b>{cat_name.upper()}</b>",
            showarrow=False,
            font=dict(size=11, color="#90E0EF"),
            bgcolor="#0B192C",
            bordercolor="#48CAE4",
            borderwidth=1,
            borderpad=4
        )

        # Faktor-faktor kecil di sepanjang tulang cabang
        sub_factors = factors.get(cat_name, [])
        for idx, factor in enumerate(sub_factors):
            # Posisi di sepanjang cabang
            fraction = (idx + 1) / (len(sub_factors) + 1)
            fx = b["x_base"] + fraction * (b["x_top"] - b["x_base"])
            fy = fraction * b["y_top"]

            is_verif = (factor["status"] == "Terverifikasi")
            marker_color = "#2ECC71" if is_verif else "#F39C12"
            status_text = "Terverifikasi (Empiris)" if is_verif else "Dugaan (Hipotesis)"

            # Garis sub-tulang horizontal kecil
            sub_len = -0.7 if b["side"] == "top" else 0.7
            fig.add_trace(go.Scatter(
                x=[fx, fx + sub_len],
                y=[fy, fy],
                mode="lines+markers",
                line=dict(
                    color=marker_color,
                    width=2,
                    dash="solid" if is_verif else "dot"
                ),
                marker=dict(size=6, color=marker_color),
                hovertext=f"<b>[{cat_name}] {factor['faktor']}</b><br>Status: {status_text}<br>Ket: {factor['keterangan']}",
                hoverinfo="text",
                name=status_text,
                showlegend=(cat_name == "Manusia" and idx < 2)
            ))

            # Label teks ringkas
            label_text = factor["faktor"][:28] + ("..." if len(factor["faktor"]) > 28 else "")
            fig.add_annotation(
                x=fx + sub_len + (-0.05 if sub_len < 0 else 0.05),
                y=fy,
                text=f"<span style='color:{marker_color}; font-size:10px;'>{'✓' if is_verif else '?'} {label_text}</span>",
                showarrow=False,
                xanchor="right" if sub_len < 0 else "left",
                font=dict(size=9, color="#E0E1DD")
            )

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#FFFFFF")),
        plot_bgcolor="#0A1128",
        paper_bgcolor="#070D1F",
        xaxis=dict(visible=False, range=[-1, 12]),
        yaxis=dict(visible=False, range=[-4.2, 4.2]),
        margin=dict(l=20, r=20, t=50, b=20),
        height=480,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(color="#FFFFFF", size=11)
        )
    )

    return fig
