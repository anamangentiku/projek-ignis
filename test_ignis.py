"""
Unit & Integration Test Suite for IGNIS System.
Menguji:
1. Inisialisasi DB SQLite & Data Retrieval
2. Pipeline Preprocessing & Geocoordinate Validation
3. Verifier (Haversine Spatial-Temporal & Consistency Audit)
4. AI Risk Scoring (Explainable AI 0-100 Calculation & Breakdown)
5. 5 Whys Root Cause Analysis & Fishbone Factors
6. Fallback Rule-Based Engine & Mitigation Recommendation
7. AI Evaluation Benchmark Runner (3 Kegagalan AI)
8. Folium Map Generation
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_all_laporan, get_db_stats, get_laporan_by_id
from modules.preprocessing import clean_text, validate_coordinates, preprocess_dataframe, evaluate_dataset_quality
from modules.verifier import haversine_distance, check_spatial_temporal_duplicates, audit_report_consistency, run_system_verification
from modules.scoring import calculate_risk_score
from modules.rca import generate_5whys_analysis
from modules.fishbone import get_fishbone_factors, render_fishbone_plotly
from modules.llm_service import answer_chat_query, generate_mitigation_recommendation
from modules.ai_evaluation import get_all_evaluation_cases, run_evaluation_benchmark
from modules.geo_map import create_ignis_map

def run_tests():
    print("=== MEMULAI TEST SUITE IGNIS ===")
    
    # 1. Test Database
    stats = get_db_stats()
    print(f"1. Database Stats: Total={stats['total']}, Simulated={stats['simulated']}, Real={stats['real']}")
    assert stats['total'] >= 100, "Dataset harus memiliki >= 100 baris!"
    
    df = get_all_laporan()
    assert len(df) == stats['total'], "Dataframe length must match total"
    first_report = df.iloc[0].to_dict()
    print("   [PASS] Database retrieval OK")

    # 2. Test Preprocessing & Coordinate Validation
    valid_coord, _ = validate_coordinates(1.4800, 102.1300)
    assert valid_coord is True, "Koordinat Riau harus valid"
    invalid_coord, _ = validate_coordinates(45.000, -75.000)
    assert invalid_coord is False, "Koordinat Kanada harus ditolak"
    cleaned = clean_text("<b>Halo</b>   dunia  <script>alert(1)</script>")
    assert cleaned == "Halo dunia", "Teks harus dibersihkan dari HTML dan spasi ganda"
    quality = evaluate_dataset_quality(df)
    print(f"2. Preprocessing & Quality: Completeness={quality['completeness_score']}%, ValidCoords={quality['coord_validity_ratio']}%")
    print("   [PASS] Preprocessing OK")

    # 3. Test Haversine & Duplication Verifier
    dist = haversine_distance(1.4800, 102.1300, 1.4850, 102.1350)
    assert 0.5 <= dist <= 1.5, f"Jarak estimasi haversine harus ~0.9 km, didapat: {dist}"
    verif = run_system_verification(first_report, df.to_dict(orient="records"))
    assert "system_status" in verif, "Hasil verifikasi sistem harus memuat system_status"
    print(f"3. Verifier: Distance test={dist} km, Sample Status={verif['system_status']}")
    print("   [PASS] Verifier OK")

    # 4. Test AI Risk Scoring (Explainable AI)
    score_res = calculate_risk_score(first_report)
    assert 0 <= score_res["total_skor"] <= 100, "Skor harus dalam range 0-100"
    assert "breakdown" in score_res and len(score_res["breakdown"]) >= 5, "Breakdown harus memuat minimal 5 komponen"
    assert score_res["label"] in ["Kritis", "Tinggi", "Sedang", "Rendah"], "Label prioritas harus valid"
    print(f"4. AI Risk Scoring: Score={score_res['total_skor']}, Label={score_res['label']}")
    print("   [PASS] Explainable AI Scoring OK")

    # 5. Test 5 Whys & Fishbone
    rca = generate_5whys_analysis(first_report)
    assert "why1" in rca and "why5" in rca, "RCA harus memuat rantai why1-why5"
    factors = get_fishbone_factors(first_report)
    assert len(factors) == 5, "Fishbone harus memuat 5 kategori"
    fish_fig = render_fishbone_plotly(factors)
    assert fish_fig is not None, "Plotly figure must be generated"
    print(f"5. RCA & Fishbone: Scenario={rca['scenario_key']}, 5 categories rendered")
    print("   [PASS] RCA & Fishbone OK")

    # 6. Test LLM Chat & Mitigation Recommendation (Fallback / Gemini)
    chat_ans = answer_chat_query("Berapa laporan prioritas Kritis?", df)
    assert len(chat_ans["answer"]) > 10, "Jawaban chatbot harus informatif"
    mitigasi = generate_mitigation_recommendation(first_report, score_info=score_res)
    assert "tindakan_segera" in mitigasi and len(mitigasi["tindakan_segera"]) > 0, "Mitigasi harus memuat tindakan segera"
    print(f"6. LLM/Fallback Engine: Chat Source='{chat_ans['source']}', Mitigasi Source='{mitigasi['sumber_rekomendasi']}'")
    print("   [PASS] LLM & Mitigation OK")

    # 7. Test AI Evaluation Benchmark
    cases = get_all_evaluation_cases()
    assert len(cases) >= 3, "Harus menguji minimal 3 mode kegagalan AI"
    for c in cases:
        assert c["status_evaluasi"] == "TERVERIFIKASI & TERATASI (PASSED)"
    print(f"7. AI Evaluation: {len(cases)} Failure Cases Tested and Passed")
    print("   [PASS] AI Evaluation Benchmark OK")

    # 8. Test Folium Map Generation
    fmap = create_ignis_map(df.head(20))
    assert fmap is not None, "Folium map must not be None"
    print("8. Folium Interactive Map: Generated successfully")
    print("   [PASS] Folium Map OK")

    print("\n==========================================")
    print("[SUCCESS] SEMUA PENGUJIAN INTEGRASI IGNIS BERHASIL (PASSED)!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
