"""
Database Manager untuk Sistem IGNIS - Gunung Klabat, Minahasa Utara.
Menyimpan laporan kebakaran, foto bukti, koordinat, status regu pemadam, dan riwayat penanganan.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ignis_klabat.db")

def get_connection():
    """Membuat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Menginisialisasi tabel database laporan kebakaran Gunung Klabat."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS laporan_klabat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_laporan TEXT UNIQUE NOT NULL,
        tanggal_lapor TEXT NOT NULL,
        nama_user TEXT NOT NULL,
        kontak_user TEXT,
        link_lokasi TEXT NOT NULL,
        gambar_kebakaran TEXT,
        deskripsi_tempat TEXT NOT NULL,
        lokasi_area TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        keparahan TEXT NOT NULL,
        tipe_vegetasi TEXT NOT NULL,
        jarak_pemukiman_km REAL NOT NULL,
        skor_prioritas REAL DEFAULT 0.0,
        label_prioritas TEXT DEFAULT 'Sedang',
        alasan_prioritas TEXT NOT NULL,
        status_penanganan TEXT DEFAULT 'Menunggu Penanganan',
        catatan_tim TEXT DEFAULT '',
        waktu_selesai TEXT,
        is_simulated INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    # Tambah kolom waktu_selesai jika belum ada
    cursor.execute("PRAGMA table_info(laporan_klabat)")
    columns = [col[1] for col in cursor.fetchall()]
    if "waktu_selesai" not in columns:
        try:
            cursor.execute("ALTER TABLE laporan_klabat ADD COLUMN waktu_selesai TEXT")
        except Exception:
            pass

    conn.commit()
    conn.close()

def insert_laporan(data: Dict[str, Any]) -> int:
    """Menyimpan satu laporan baru ke SQLite."""
    conn = get_connection()
    cursor = conn.cursor()

    if "kode_laporan" not in data or not data["kode_laporan"]:
        count = cursor.execute("SELECT COUNT(*) FROM laporan_klabat").fetchone()[0]
        data["kode_laporan"] = f"KLB-{datetime.now().year}-{count + 1:03d}"

    if "created_at" not in data:
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    INSERT INTO laporan_klabat (
        kode_laporan, tanggal_lapor, nama_user, kontak_user,
        link_lokasi, gambar_kebakaran, deskripsi_tempat, lokasi_area,
        latitude, longitude, keparahan, tipe_vegetasi, jarak_pemukiman_km,
        skor_prioritas, label_prioritas, alasan_prioritas, status_penanganan,
        catatan_tim, waktu_selesai, is_simulated, created_at
    ) VALUES (
        :kode_laporan, :tanggal_lapor, :nama_user, :kontak_user,
        :link_lokasi, :gambar_kebakaran, :deskripsi_tempat, :lokasi_area,
        :latitude, :longitude, :keparahan, :tipe_vegetasi, :jarak_pemukiman_km,
        :skor_prioritas, :label_prioritas, :alasan_prioritas, :status_penanganan,
        :catatan_tim, :waktu_selesai, :is_simulated, :created_at
    )
    """
    if "waktu_selesai" not in data:
        data["waktu_selesai"] = None

    cursor.execute(query, data)
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_laporan_prioritas() -> pd.DataFrame:
    """Mengambil semua laporan terurut prioritas."""
    conn = get_connection()
    query = """
    SELECT * FROM laporan_klabat 
    ORDER BY 
        CASE status_penanganan
            WHEN 'Menunggu Penanganan' THEN 1
            WHEN 'Tim Menuju Lokasi' THEN 2
            WHEN 'Sedang Dipadamkan' THEN 3
            WHEN 'Sudah Diatasi' THEN 4
            WHEN 'Selesai / Padam' THEN 5
            ELSE 6
        END,
        skor_prioritas DESC,
        id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_laporan_aktif() -> pd.DataFrame:
    """Mengambil laporan yang BELUM diatasi (masih aktif di lapangan)."""
    conn = get_connection()
    query = """
    SELECT * FROM laporan_klabat 
    WHERE status_penanganan NOT IN ('Sudah Diatasi', 'Selesai / Padam')
    ORDER BY skor_prioritas DESC, id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_riwayat_selesai() -> pd.DataFrame:
    """Mengambil laporan yang SUDAH BERHASIL DIATASI oleh petugas."""
    conn = get_connection()
    query = """
    SELECT * FROM laporan_klabat 
    WHERE status_penanganan IN ('Sudah Diatasi', 'Selesai / Padam')
    ORDER BY waktu_selesai DESC, id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_status_pemadaman(laporan_id: int, status_baru: str, catatan_tim: str = ""):
    """Memperbarui status penanganan oleh regu pemadam."""
    conn = get_connection()
    cursor = conn.cursor()
    waktu_selesai = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status_baru in ["Sudah Diatasi", "Selesai / Padam"] else None
    
    if waktu_selesai:
        cursor.execute("""
        UPDATE laporan_klabat
        SET status_penanganan = ?, catatan_tim = ?, waktu_selesai = ?
        WHERE id = ?
        """, (status_baru, catatan_tim, waktu_selesai, laporan_id))
    else:
        cursor.execute("""
        UPDATE laporan_klabat
        SET status_penanganan = ?, catatan_tim = ?
        WHERE id = ?
        """, (status_baru, catatan_tim, laporan_id))
        
    conn.commit()
    conn.close()

def tandai_sudah_diatasi(laporan_id: int, catatan: str = ""):
    """Tombol cepat menandai laporan kebakaran telah padam/berhasil diatasi."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE laporan_klabat
    SET status_penanganan = 'Sudah Diatasi',
        catatan_tim = ?,
        waktu_selesai = ?
    WHERE id = ?
    """, (catatan, now_str, laporan_id))
    conn.commit()
    conn.close()

def get_laporan_detail(laporan_id: int) -> Optional[Dict[str, Any]]:
    """Mengambil satu data laporan lengkap."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM laporan_klabat WHERE id = ?", (laporan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
