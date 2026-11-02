"""
Script generator untuk membuat file PowerPoint (PPTX) resmi IGNIS Klabat.
Mencakup: Masalah, Solusi, Root Cause Analysis (RCA 5 Whys), Fishbone Diagram, dan Implementasi Python.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path):
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palet Warna Clean Light & Professional
    COLOR_BG = RGBColor(248, 250, 252)        # #F8FAFC Soft Slate
    COLOR_CARD_BG = RGBColor(255, 255, 255)   # #FFFFFF Pure White
    COLOR_BORDER = RGBColor(226, 232, 240)    # #E2E8F0 Subtle Border
    COLOR_PRIMARY = RGBColor(234, 88, 12)     # #EA580C Flame Orange
    COLOR_SECONDARY = RGBColor(2, 132, 199)   # #0284C7 Sky Blue
    COLOR_EMERALD = RGBColor(16, 185, 129)    # #10B981 Green Safe
    COLOR_RED = RGBColor(239, 68, 68)         # #EF4444 Critical
    COLOR_DARK = RGBColor(15, 23, 42)         # #0F172A Dark Slate Text
    COLOR_MUTED = RGBColor(100, 116, 139)     # #64748B Muted Gray Text
    COLOR_LIGHT_BLUE = RGBColor(240, 249, 255)# Light Blue Tint
    COLOR_LIGHT_ORANGE = RGBColor(255, 247, 237) # Light Orange Tint

    def set_slide_background(slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = COLOR_BG
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, title_text, category_text="IGNIS KLABAT • SISTEM MITIGASI BENCANA"):
        # Category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_PRIMARY

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_DARK

        # Thin divider line
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_BORDER
        line.line.fill.background()

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: COVER
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Big Card in center
    add_card(slide1, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.5), COLOR_CARD_BG, COLOR_BORDER)

    # Flame icon box
    flame_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.6), Inches(0.8), Inches(0.8))
    flame_box.fill.solid()
    flame_box.fill.fore_color.rgb = COLOR_PRIMARY
    flame_box.line.fill.background()
    tf_f = flame_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "🔥"
    p_f.font.size = Pt(26)
    p_f.alignment = PP_ALIGN.CENTER

    # Badge Pill
    badge_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.8), Inches(1.75), Inches(5.8), Inches(0.45))
    badge_box.fill.solid()
    badge_box.fill.fore_color.rgb = COLOR_LIGHT_ORANGE
    badge_box.line.color.rgb = RGBColor(254, 215, 170)
    tf_b = badge_box.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "SISTEM PENDUKUNG KEPUTUSAN & MITIGASI KARHUTLA BERBASIS AI"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_PRIMARY
    p_b.alignment = PP_ALIGN.CENTER

    # Main Titles
    title_box = slide1.shapes.add_textbox(Inches(1.8), Inches(2.5), Inches(9.8), Inches(2.2))
    tf = title_box.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = "IGNIS KLABAT"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_DARK

    p2 = tf.add_paragraph()
    p2.text = "Investigasi Multi-Faktor Kebakaran Hutan Gunung Klabat (1.995 mdpl) Menggunakan Root Cause Analysis (RCA) & Ishikawa Fishbone Diagram"
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLOR_MUTED
    p2.space_before = Pt(8)

    # Footer Card Info
    footer_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(5.0), Inches(9.7), Inches(1.1))
    footer_box.fill.solid()
    footer_box.fill.fore_color.rgb = COLOR_LIGHT_BLUE
    footer_box.line.color.rgb = RGBColor(186, 230, 253)
    tf_ft = footer_box.text_frame
    tf_ft.word_wrap = True

    p_ft1 = tf_ft.paragraphs[0]
    p_ft1.text = "📍 Ruang Lingkup: Kawasan Gunung Klabat, Minahasa Utara, Sulawesi Utara"
    p_ft1.font.size = Pt(12)
    p_ft1.font.bold = True
    p_ft1.font.color.rgb = COLOR_SECONDARY

    p_ft2 = tf_ft.add_paragraph()
    p_ft2.text = "Fokus Bahasan: Masalah Lapangan, Solusi Sistem, Metode 5 Whys, dan Validasi Empiris Fishbone Python"
    p_ft2.font.size = Pt(11)
    p_ft2.font.color.rgb = COLOR_DARK
    p_ft2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: MASALAH YANG ADA
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Masalah yang Ada: Tantangan Karhutla di Gunung Klabat")

    # 3 Cards
    cards_data = [
        ("1. Karakteristik Kawasan Gunung", COLOR_PRIMARY, [
            "Gunung Klabat adalah puncak tertinggi di Sulawesi Utara (1.995 mdpl).",
            "Bahan Bakar Kering: Semak belukar dan ilalang di lereng sangat cepat kering saat musim kemarau.",
            "Topografi Ekstrem: Lereng curam, jurang terjal, dan jalan setapak menyulitkan pergerakan mobil tangki pemadam.",
            "Perbatasan Rawan: Berbatasan langsung dengan kebun produktif cengkeh, pala, dan perumahan warga Airmadidi."
        ]),
        ("2. Kendala Pelaporan Masyarakat", COLOR_SECONDARY, [
            "Kepanikan Pendaki: Saat melihat asap di jalur pendakian, pendaki rentan salah arah dan terjebak asap tebal.",
            "Beban Teknis: Pelapor awam tidak mengerti cara mengukur keparahan (Kritis / Sedang / Rendah) secara objektif.",
            "Keterlambatan Informasi: Laporan sering lambat sampai ke posko pemadam atau tanpa koordinat akurat.",
            "Minim Panduan Darurat: Masyarakat lereng tidak memiliki rujukan langkah evakuasi pertama yang aman."
        ]),
        ("3. Kendala Regu Damkar & BPBD", COLOR_RED, [
            "Dilema Prioritas: Tanpa sistem cerdas, petugas kesulitan menentukan titik api mana yang harus didahulukan.",
            "Keterbatasan Sumber Daya: Personel dan armada semprot air terbatas untuk mencakup seluruh lingkar lereng gunung.",
            "Evaluasi Masih Sporadis: Karhutla kerap hanya dipadamkan tanpa ada investigasi sistemik akar penyebabnya.",
            "Ketiadaan Sistem Arsip: Sulit melihat rekurensi titik api dan pola pemicu di tahun-tahun berikutnya."
        ])
    ]

    card_w = Inches(3.7)
    card_h = Inches(5.4)
    for i, (title, color, points) in enumerate(cards_data):
        cx = Inches(0.8 + i * 4.0)
        cy = Inches(1.6)
        add_card(slide2, cx, cy, card_w, card_h)

        # Header bar in card
        hbar = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.2), cy + Inches(0.2), card_w - Inches(0.4), Inches(0.55))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = color
        hbar.line.fill.background()
        tf_h = hbar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = title
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(255, 255, 255)
        p_h.alignment = PP_ALIGN.CENTER

        # Body text
        tb = slide2.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.85), card_w - Inches(0.4), card_h - Inches(1.0))
        tf_b = tb.text_frame
        tf_b.word_wrap = True
        for j, pt in enumerate(points):
            p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: SOLUSI YANG DIBUAT DENGAN IGNIS KLABAT
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "Solusi yang Dibuat: Arsitektur Sistem IGNIS Klabat")

    # Dual Role Cards (Left: Warga, Right: Damkar)
    col_w = Inches(5.6)
    col_h = Inches(5.4)

    # Portal Warga Card
    add_card(slide3, Inches(0.8), Inches(1.6), col_w, col_h)
    hbar_w = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.8), col_w - Inches(0.4), Inches(0.6))
    hbar_w.fill.solid()
    hbar_w.fill.fore_color.rgb = COLOR_SECONDARY
    hbar_w.line.fill.background()
    p_hw = hbar_w.text_frame.paragraphs[0]
    p_hw.text = "👤 PORTAL MASYARAKAT & PENDAKI"
    p_hw.font.size = Pt(14)
    p_hw.font.bold = True
    p_hw.font.color.rgb = RGBColor(255, 255, 255)
    p_hw.alignment = PP_ALIGN.CENTER

    tb_w = slide3.shapes.add_textbox(Inches(1.0), Inches(2.5), col_w - Inches(0.4), col_h - Inches(1.1))
    tf_w = tb_w.text_frame
    tf_w.word_wrap = True
    warga_solutions = [
        ("Otomasi Prioritas AI (Gemini 3.8 Flash):", "Masyarakat TIDAK PERLU memilih keparahan. AI otomatis menganalisis teks kejadian, jarak ke pemukiman, dan vegetasi."),
        ("Preset Titik Patokan Klabat:", "Memudahkan pelapor memilih patokan (Kaki Dian, Pos 1-6, Puncak) lengkap dengan auto-fill koordinat dan link Google Maps."),
        ("Asisten AI Anti-Panik 24 Jam:", "Memberikan instruksi penyelamatan tenang berbasis SOP (kain basah, larangan mendaki ke atas saat api dari bawah)."),
        ("Direktori Darurat Terpadu:", "Satu klik terhubung ke Call Center 112, Damkar Airmadidi, BPBD Minut, Basarnas, Polsek, dan Pos Klabat.")
    ]
    for j, (head, desc) in enumerate(warga_solutions):
        p = tf_w.paragraphs[0] if j == 0 else tf_w.add_paragraph()
        p.text = f"✓ {head} {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # Pusat Komando Damkar Card
    add_card(slide3, Inches(6.9), Inches(1.6), col_w, col_h)
    hbar_d = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.8), col_w - Inches(0.4), Inches(0.6))
    hbar_d.fill.solid()
    hbar_d.fill.fore_color.rgb = COLOR_PRIMARY
    hbar_d.line.fill.background()
    p_hd = hbar_d.text_frame.paragraphs[0]
    p_hd.text = "🚒 PUSAT KOMANDO DAMKAR & BPBD"
    p_hd.font.size = Pt(14)
    p_hd.font.bold = True
    p_hd.font.color.rgb = RGBColor(255, 255, 255)
    p_hd.alignment = PP_ALIGN.CENTER

    tb_d = slide3.shapes.add_textbox(Inches(7.1), Inches(2.5), col_w - Inches(0.4), col_h - Inches(1.1))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    damkar_solutions = [
        ("Antrean Terurut Prioritas AI:", "Laporan yang paling mengancam pemukiman (Kritis) otomatis berada di urutan teratas untuk respon armada."),
        ("Navigasi Armada Cepat:", "Dilengkapi tautan navigasi langsung ke rute Google Maps dan koordinat presisi."),
        ("Disposisi & Riwayat Padam:", "Status bertahap: 'Tim Menuju Lokasi' ➔ 'Sedang Dipadamkan' ➔ 'Tandai Sudah Diatasi' lengkap dengan durasi tuntas."),
        ("Peta Geospasial & Analisis Akar Masalah:", "Peta sebaran Folium terintegrasi dengan Diagram Fishbone RCA untuk perencanaan jangka panjang.")
    ]
    for j, (head, desc) in enumerate(damkar_solutions):
        p = tf_d.paragraphs[0] if j == 0 else tf_d.add_paragraph()
        p.text = f"✓ {head} {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 4: METODE ROOT CAUSE ANALYSIS (RCA) - TEORI & METODE
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Metodologi Investigasi: Root Cause Analysis (RCA)")

    # Left Box: Definisi & Urgensi
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.4))
    tb_rca_def = slide4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(4.1), Inches(5.0))
    tf_rca = tb_rca_def.text_frame
    tf_rca.word_wrap = True

    p = tf_rca.paragraphs[0]
    p.text = "Apa itu Root Cause Analysis (RCA)?"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    points_rca = [
        "Metode investigasi terstruktur untuk menemukan kelemahan paling mendasar yang menjadi pemicu kebakaran.",
        "Bukan Sekadar Mengatasi Gejala: Memadamkan api hanya menyelesaikan gejala (symptom). RCA mencari tahu penyebab sistemik agar tidak terulang.",
        "Metode The 5 Whys: Melakukan penelusuran berjenjang dengan menanyakan 'Mengapa?' minimal 5 kali secara kausalitas logis.",
        "Landasan Kebijakan: Menghasilkan rekomendasi jangka panjang (SOP pos pendakian, regulasi sekat bakar warga lereng, dan tandon air mitigasi)."
    ]
    for pt in points_rca:
        p = tf_rca.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11.5)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(8)

    # Right Box: Rantai 5 Whys Hierarchy
    add_card(slide4, Inches(5.6), Inches(1.6), Inches(6.9), Inches(5.4))

    whys_steps = [
        ("Level 1 (Gejala Lapangan)", "Mengapa api muncul dan merambat di semak lereng?", "Ditemukan bara api unggun atau puntung rokok yang ditinggalkan pendaki.", COLOR_MUTED),
        ("Level 2 (Kondisi Lingkungan)", "Mengapa bara kecil dapat cepat membesar?", "Vegetasi ilalang sangat kering saat kemarau dan angin lereng bertiup kencang.", COLOR_SECONDARY),
        ("Level 3 (Perilaku Manusia)", "Mengapa pendaki meninggalkan bara tanpa dipadamkan?", "Pendaki kehabisan air minum dan terburu-buru turun atau mengejar puncak.", COLOR_SECONDARY),
        ("Level 4 (Prosedural Posko)", "Mengapa tidak ada pemeriksaan api di pos pendakian?", "SOP pemeriksaan barang bawaan dan edukasi di pos registrasi masih minim.", COLOR_PRIMARY),
        ("Level 5 (Akar Masalah Sistemik)", "AKAR MASALAH (ROOT CAUSE):", "Belum adanya tata kelola registrasi terpadu digital, ketiadaan patroli di titik rawan, dan minimnya tandon air darurat di jalur.", COLOR_PRIMARY)
    ]

    for k, (level, q, a, col) in enumerate(whys_steps):
        wy = Inches(1.8 + k * 1.0)
        wbox = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.8), wy, Inches(6.5), Inches(0.85))
        wbox.fill.solid()
        wbox.fill.fore_color.rgb = COLOR_BG if k < 4 else COLOR_LIGHT_ORANGE
        wbox.line.color.rgb = col
        wbox.line.width = Pt(1.5)

        tf_w = wbox.text_frame
        tf_w.word_wrap = True
        p_l = tf_w.paragraphs[0]
        p_l.text = f"{level}: {q}"
        p_l.font.size = Pt(10.5)
        p_l.font.bold = True
        p_l.font.color.rgb = col

        p_a = tf_w.add_paragraph()
        p_a.text = f"➔ {a}"
        p_a.font.size = Pt(11)
        p_a.font.color.rgb = COLOR_DARK
        p_a.space_before = Pt(2)

    # =========================================================================
    # SLIDE 5: ISHIKAWA FISHBONE DIAGRAM - 5 KATEGORI PENYEBAB
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Media Visual: Fishbone Diagram (Ishikawa)")

    # Intro Card Top
    top_card = add_card(slide5, Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.0))
    tf_top = top_card.text_frame
    tf_top.word_wrap = True
    p_t1 = tf_top.paragraphs[0]
    p_t1.text = "🎯 Fungsi Fishbone: Mengelompokkan multi-faktor potensi penyebab kebakaran hutan ke dalam 5 kategori terstruktur."
    p_t1.font.size = Pt(12)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_PRIMARY

    p_t2 = tf_top.add_paragraph()
    p_t2.text = "Kepala Ikan (Effect): Kebakaran Hutan & Lahan Kawasan Gunung Klabat. Duri-Duri (Causes): 5 Cabang Utama."
    p_t2.font.size = Pt(11)
    p_t2.font.color.rgb = COLOR_DARK
    p_t2.space_before = Pt(3)

    # 5 Branch Cards
    branches = [
        ("1. MANUSIA (People)", COLOR_PRIMARY, [
            "Puntung rokok pendaki",
            "Bara api unggun perapian",
            "Pembakaran sampah serasah kebun",
            "Pengawasan pos registrasi lemah"
        ]),
        ("2. LINGKUNGAN (Environment)", COLOR_SECONDARY, [
            "Semak & ilalang mudah terbakar",
            "Kebun cengkeh, pala, kelapa",
            "Serasah kering mudah tersulut",
            "Medan lereng curam & jurang"
        ]),
        ("3. CUACA (Climate)", COLOR_MUTED, [
            "Angin lereng bertiup kencang",
            "Musim kemarau ekstrem",
            "Hari tanpa hujan berturut-turut",
            "Suhu tinggi & kelembaban rendah"
        ]),
        ("4. INFRASTRUKTUR", COLOR_RED, [
            "Titik api di jalur setapak sempit",
            "Dekat pemukiman warga (<= 1 km)",
            "Akses evakuasi pendaki terbatas",
            "Sumber air pemadam minim"
        ]),
        ("5. PENANGANAN (Process)", COLOR_EMERALD, [
            "Durasi tempuh laporan ke lokasi",
            "Antrean laporan menumpuk",
            "Keterbatasan selang pemadam",
            "Personel darat medan terjal minim"
        ])
    ]

    bw = Inches(2.25)
    bh = Inches(4.1)
    for idx, (b_name, b_col, b_items) in enumerate(branches):
        bx = Inches(0.8 + idx * 2.37)
        by = Inches(2.8)
        add_card(slide5, bx, by, bw, bh)

        # Header Pill
        hpill = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx + Inches(0.1), by + Inches(0.12), bw - Inches(0.2), Inches(0.55))
        hpill.fill.solid()
        hpill.fill.fore_color.rgb = b_col
        hpill.line.fill.background()
        tf_hp = hpill.text_frame
        tf_hp.word_wrap = True
        p_hp = tf_hp.paragraphs[0]
        p_hp.text = b_name
        p_hp.font.size = Pt(11)
        p_hp.font.bold = True
        p_hp.font.color.rgb = RGBColor(255, 255, 255)
        p_hp.alignment = PP_ALIGN.CENTER

        # Items
        tb_it = slide5.shapes.add_textbox(bx + Inches(0.1), by + Inches(0.75), bw - Inches(0.2), bh - Inches(0.9))
        tf_it = tb_it.text_frame
        tf_it.word_wrap = True
        for m, item in enumerate(b_items):
            p = tf_it.paragraphs[0] if m == 0 else tf_it.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 6: IMPLEMENTASI PYTHON - DYNAMIC EVIDENCE CLASSIFIER (NILAI PLUS)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Implementasi Teknis Python: Dynamic Evidence Classifier")

    col6_w = Inches(5.6)
    col6_h = Inches(5.4)

    # Left: Logic Code Structure
    add_card(slide6, Inches(0.8), Inches(1.6), col6_w, col6_h)
    tb_c1 = slide6.shapes.add_textbox(Inches(1.0), Inches(1.8), col6_w - Inches(0.4), col6_h - Inches(0.4))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True

    p = tf_c1.paragraphs[0]
    p.text = "💻 Bukan Diagram Statis / Hardcode"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    p_tech = [
        ("Evaluasi Otomatis dari SQLite:", "Setiap faktor dihitung statusnya secara langsung oleh modul Python 'fishbone_klabat.py' dari data riwayat laporan."),
        ("Regex Keyword Pattern Matching:", "Menggunakan ekspresi reguler batas kata (\\b) untuk mencocokkan kata kunci seperti 'rokok', 'kebun', 'curam', tanpa false-positive."),
        ("Ambang Batas Statistik (Threshold):", "Faktor dianggap sah 'Didukung Data' jika muncul minimal pada 2 laporan dan mencakup minimal 10% data agregat."),
        ("Engine Plotly Interaktif:", "Menghasilkan grafik interaktif dengan hover tooltip detail persentase bukti dan status validitas faktor.")
    ]
    for head, body in p_tech:
        p = tf_c1.add_paragraph()
        p.text = f"• {head} {body}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(8)

    # Right: Validitas Empiris (Didukung Data vs Dugaan)
    add_card(slide6, Inches(6.9), Inches(1.6), col6_w, col6_h)
    tb_c2 = slide6.shapes.add_textbox(Inches(7.1), Inches(1.8), col6_w - Inches(0.4), col6_h - Inches(0.4))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True

    p = tf_c2.paragraphs[0]
    p.text = "🔬 Pembedaan Status Ilmiah"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_SECONDARY

    # Box 1: Didukung Data
    b_data = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(2.4), col6_w - Inches(0.4), Inches(1.8))
    b_data.fill.solid()
    b_data.fill.fore_color.rgb = RGBColor(209, 250, 229)
    b_data.line.color.rgb = COLOR_EMERALD
    b_data.line.width = Pt(1.5)
    tf_bd = b_data.text_frame
    tf_bd.word_wrap = True
    p_bd1 = tf_bd.paragraphs[0]
    p_bd1.text = "🟢 STATUS: DIDUKUNG DATA (GARIS SOLID HIJAU)"
    p_bd1.font.size = Pt(11.5)
    p_bd1.font.bold = True
    p_bd1.font.color.rgb = RGBColor(4, 120, 87)

    p_bd2 = tf_bd.add_paragraph()
    p_bd2.text = "Faktor memiliki bukti terukur di basis data laporan masyarakat (misal: 'semak kering', 'kebun cengkeh', jarak <= 1 km dari pemukiman)."
    p_bd2.font.size = Pt(11)
    p_bd2.font.color.rgb = COLOR_DARK
    p_bd2.space_before = Pt(4)

    # Box 2: Dugaan
    b_dugaan = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(4.5), col6_w - Inches(0.4), Inches(2.1))
    b_dugaan.fill.solid()
    b_dugaan.fill.fore_color.rgb = RGBColor(254, 243, 199)
    b_dugaan.line.color.rgb = RGBColor(245, 158, 11)
    b_dugaan.line.width = Pt(1.5)
    tf_bg = b_dugaan.text_frame
    tf_bg.word_wrap = True
    p_bg1 = tf_bg.paragraphs[0]
    p_bg1.text = "🟠 STATUS: DUGAAN / HIPOTESIS (GARIS PUTUS-PUTUS ORANYE)"
    p_bg1.font.size = Pt(11.5)
    p_bg1.font.bold = True
    p_bg1.font.color.rgb = RGBColor(180, 83, 9)

    p_bg2 = tf_bg.add_paragraph()
    p_bg2.text = "Faktor yang secara ilmiah logis namun belum ada sensor pengukurnya di sistem (misal data BMKG untuk angin/kelembaban atau inventaris logistik pemadam). Ini menunjukkan kejujuran data akademik."
    p_bg2.font.size = Pt(11)
    p_bg2.font.color.rgb = COLOR_DARK
    p_bg2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 7: INTEGRASI AI (GEMINI 3.8 FLASH) & CHATBOT
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Fitur Cerdas: Integrasi Gemini AI & Chatbot Darurat")

    c7_w = Inches(5.6)
    c7_h = Inches(5.4)

    # Left: AI Classifier
    add_card(slide7, Inches(0.8), Inches(1.6), c7_w, c7_h)
    tb_ai1 = slide7.shapes.add_textbox(Inches(1.0), Inches(1.8), c7_w - Inches(0.4), c7_h - Inches(0.4))
    tf_ai1 = tb_ai1.text_frame
    tf_ai1.word_wrap = True
    p = tf_ai1.paragraphs[0]
    p.text = "🤖 AI Priority Classifier (Gemini 3.8 Flash)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    ai_pts = [
        ("Masyarakat Bebas dari Beban Teknis:", "Warga awam tidak dipaksa memilih keparahan. AI membaca narasi kejadian dan kondisi sekitar."),
        ("Formula Penilaian Cerdas:", "Memadukan kedekatan dengan rumah warga (< 500m = Kritis), risiko pemutusan jalur evakuasi pendaki, dan tipe vegetasi."),
        ("Explainable AI (XAI):", "Memberikan alasan taktis padat kepada petugas damkar mengapa laporan tersebut harus diprioritaskan."),
        ("Fallback Rule-Based System:", "Jika koneksi internet offline, sistem tetap 100% bekerja menggunakan algoritma pakar lokal.")
    ]
    for h, b in ai_pts:
        p = tf_ai1.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(8)

    # Right: Anti-Panic Chatbot
    add_card(slide7, Inches(6.9), Inches(1.6), c7_w, c7_h)
    tb_ai2 = slide7.shapes.add_textbox(Inches(7.1), Inches(1.8), c7_w - Inches(0.4), c7_h - Inches(0.4))
    tf_ai2 = tb_ai2.text_frame
    tf_ai2.word_wrap = True
    p = tf_ai2.paragraphs[0]
    p.text = "💬 Asisten Tanggap Darurat & Anti-Panik"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_SECONDARY

    chat_pts = [
        ("Psikologis Tenang & Tegas:", "Menghindari kepanikan pelapor dengan respon terarah dan instruktif."),
        ("Aturan Mutlak Keselamatan Klabat:", "Larangan keras mendaki ke puncak bila api berasal dari lereng bawah, karena lidah api dan gas beracun naik sangat cepat."),
        ("Panduan Fisik Darurat:", "Instruksi membasahi kain atau masker dengan air minum untuk melindungi paru-paru dari infeksi asap."),
        ("Integrasi Hotline Cepat:", "Menampilkan tombol panggilan darurat Call Center 112, Posko Damkar, dan Basarnas Manado.")
    ]
    for h, b in chat_pts:
        p = tf_ai2.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 8: KEKURANGAN & BATASAN SISTEM SAAT INI (LIMITATIONS)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "Kekurangan & Batasan Sistem Saat Ini (System Limitations)")

    # 3 Limitation Cards
    limit_cards = [
        ("1. Keterbatasan Algoritma NLP & Teks", COLOR_RED, [
            "Pencocokan Kata Kunci (Regex): Belum menangani negasi kompleks (contoh: kalimat 'bukan akibat rokok' tetap mencocokkan kata 'rokok').",
            "Laporan Belum Terverifikasi Fisik: Status 'Didukung Data' pada Fishbone berarti 'muncul di laporan masyarakat', bukan vonis mutlak penyelidikan forensik.",
            "Ketergantungan Prompt LLM: Kualitas respons AI Gemini sangat dipengaruhi kelengkapan narasi yang ditulis oleh pelapor awam."
        ]),
        ("2. Keterbatasan Integrasi Sensor Fisik", COLOR_PRIMARY, [
            "Belum Terhubung API BMKG: Data cuaca (kecepatan angin lereng, suhu, dan kelembapan) masih berstatus 'Dugaan' karena belum ada integrasi stasiun cuaca.",
            "Absennya Sensor IoT Lapangan: Belum ada kamera termal atau sensor pendeteksi asap fisik mandiri di pos-pos pendakian rawan.",
            "Peta Sumber Air Statis: Belum ada sensor pemantau debit tandon/sungai untuk mengetahui ketersediaan air pemadam saat musim kemarau ekstrem."
        ]),
        ("3. Infrastruktur Jaringan & Verifikasi", COLOR_SECONDARY, [
            "Blank Spot Sinyal Gunung: Jalur pendakian atas (Pos 4 s/d Puncak 1.995 mdpl) memiliki titik lemah sinyal internet untuk pelaporan web.",
            "Potensi Laporan Palsu (Hoax): Sistem belum memiliki filter verifikasi identitas berbasis NIK/KTP untuk mencegah laporan iseng atau salah identifikasi asap.",
            "Ketergantungan Koneksi LLM: Pemrosesan AI Gemini membutuhkan koneksi internet, meskipun sistem fallback lokal sudah tersedia."
        ])
    ]

    for idx, (title, col, items) in enumerate(limit_cards):
        cx = Inches(0.8 + idx * 4.0)
        cy = Inches(1.6)
        add_card(slide8, cx, cy, card_w, Inches(5.4))

        # Header pill
        hpill = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.2), cy + Inches(0.2), card_w - Inches(0.4), Inches(0.55))
        hpill.fill.solid()
        hpill.fill.fore_color.rgb = col
        hpill.line.fill.background()
        tf_h = hpill.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = title
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(255, 255, 255)
        p_h.alignment = PP_ALIGN.CENTER

        # Body items
        tb_b = slide8.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.85), card_w - Inches(0.4), Inches(4.3))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        for m, it in enumerate(items):
            p = tf_b.paragraphs[0] if m == 0 else tf_b.add_paragraph()
            p.text = "• " + it
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 9: KESIMPULAN & DAMPAK NYATA SISTEM
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9)
    add_header(slide9, "Dampak Nyata Sistem & Kesimpulan Akhir")

    # 3 Summary Cards
    s_cards = [
        ("Dampak Bagi Warga & Pendaki", COLOR_SECONDARY, [
            "Kemudahan melapor dalam hitungan detik tanpa kebingungan teknis.",
            "Kepastian bahwa laporan langsung masuk ke radar posko damkar.",
            "Asisten anti-panik 24 jam mencegah jatuhnya korban jiwa di jalur pendakian.",
            "Akses cepat ke seluruh nomor telepon darurat Minahasa Utara."
        ]),
        ("Dampak Bagi Damkar & BPBD", COLOR_PRIMARY, [
            "Optimalisasi respons armada pemadam menuju titik paling kritis lebih dulu.",
            "Efisiensi logistik selang dan personel pada medan terjal lereng Klabat.",
            "Pencatatan riwayat tuntas untuk evaluasi durasi penanganan.",
            "Peta geospasial real-time yang memisahkan titik aktif vs sudah padam."
        ]),
        ("Keunggulan Ilmiah RCA & Fishbone", COLOR_EMERALD, [
            "Mengubah paradigma dari pemadaman reaktif menjadi mitigasi preventif.",
            "Identifikasi akar masalah struktural (SOP registrasi, tandon air, patroli).",
            "Pemisahan transparan bukti data vs dugaan lapangan pada Python.",
            "Dasar pengambilan kebijakan anggaran dan regulasi oleh Pemkab Minut."
        ])
    ]

    for idx, (title, col, items) in enumerate(s_cards):
        cx = Inches(0.8 + idx * 4.0)
        cy = Inches(1.6)
        add_card(slide9, cx, cy, card_w, Inches(5.4))

        # Header pill
        hpill = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.2), cy + Inches(0.2), card_w - Inches(0.4), Inches(0.55))
        hpill.fill.solid()
        hpill.fill.fore_color.rgb = col
        hpill.line.fill.background()
        tf_h = hpill.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = title
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(255, 255, 255)
        p_h.alignment = PP_ALIGN.CENTER

        # Body items
        tb_b = slide9.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.85), card_w - Inches(0.4), Inches(4.2))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        for m, it in enumerate(items):
            p = tf_b.paragraphs[0] if m == 0 else tf_b.add_paragraph()
            p.text = "✓ " + it
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_DARK
            p.space_after = Pt(10)

    # Simpan File
    prs.save(output_path)
    print(f"Presentation saved successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = r"d:\Download C\tugas AI\ignis_system"
    out_file = os.path.join(out_dir, "IGNIS_Klabat_Presentasi_RCA_Fishbone.pptx")
    create_presentation(out_file)
