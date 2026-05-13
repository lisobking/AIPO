import pandas as pd
from pathlib import Path
import logging

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.resolve()
INPUT_DIR = PROJECT_ROOT / "workspace" / "01_input_quotes"
OUTPUT_DIR = PROJECT_ROOT / "workspace" / "02_output_pos"
LOG_FILE = PROJECT_ROOT / "logs" / "qc_report.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def verify_data():
    """QC 에이전트: 입출력 데이터 합계 무결성 검증"""
    print("🔍 QC 에이전트: 무결성 검사 가동...")
    
    input_files = list(INPUT_DIR.glob("*.xlsx"))
    
    for in_file in input_files:
        out_file = OUTPUT_DIR / f"PO_{in_file.name}"
        
        if not out_file.exists():
            print(f"❌ [QC] 발주서가 생성되지 않음: {in_file.name}")
            continue
            
        # 데이터 로드
        in_df = pd.read_excel(in_file)
        out_df = pd.read_excel(out_file, skiprows=2) # 템플릿 헤더 고려
        
        # 합계 비교 (예시 logic: 견적서 수량과 발주서 수량 합계 비교)
        in_sum = in_df['수량'].sum()
        out_sum = out_df['수량'].sum()
        
        if in_sum == out_sum:
            status = "✅ PASS"
            print(f"{status}: {in_file.name} -> {out_file.name} (수량 {in_sum}개 일치)")
        else:
            status = "🚨 FAIL"
            print(f"{status}: {in_file.name} 데이터 불일치! (원본 {in_sum} vs 생성 {out_sum})")
            
        logging.info(f"Verification for {in_file.name}: {status}")

if __name__ == "__main__":
    verify_data()
