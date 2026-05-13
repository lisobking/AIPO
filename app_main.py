import os
import sys
import logging
import sqlite3
import shutil
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

# 경로 설정
PROJECT_ROOT = Path(__file__).parent.resolve()
INPUT_DIR = PROJECT_ROOT / "workspace" / "01_input_quotes"
OUTPUT_DIR = PROJECT_ROOT / "workspace" / "02_output_pos"
TEMPLATE_FILE = PROJECT_ROOT / "template" / "Standard_PO_Template.xlsx"
LOG_DIR = PROJECT_ROOT / "logs"
DB_PATH = PROJECT_ROOT / "settings.db"

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(LOG_DIR / "system_security.log", encoding='utf-8'),
                              logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("ParkDirector")

class AutoPOManager:
    def __init__(self):
        logger.info("👔 박부장: 스마트 파서 모듈 가동.")
        self.ensure_directories()
        
    def ensure_directories(self):
        for path in [INPUT_DIR, OUTPUT_DIR, LOG_DIR]:
            path.mkdir(parents=True, exist_ok=True)

    def find_header_row(self, file_path, keywords=['품목', 'ITEM']):
        """엑셀에서 키워드를 찾아 헤더 행 번호를 반환 (0-indexed)"""
        df_raw = pd.read_excel(file_path, header=None)
        for i, row in df_raw.iterrows():
            for val in row:
                if any(k in str(val) for k in keywords):
                    logger.info(f"🔍 헤더 감지: {i}행에서 '{val}' 발견")
                    return i
        return 0

    def process_file(self, file_path):
        try:
            # 1. 스마트 헤더 감지
            header_idx = self.find_header_row(file_path)
            input_df = pd.read_excel(file_path, header=header_idx)
            
            # 2. 템플릿 로드
            output_path = OUTPUT_DIR / f"PO_{file_path.stem}.xlsx"
            shutil.copy(TEMPLATE_FILE, output_path)
            
            # 3. 데이터 매핑 (샘플 컬럼명 대응)
            processed_data = []
            target_col = next((c for c in input_df.columns if '품목' in str(c) or 'ITEM' in str(c)), input_df.columns[0])
            
            for idx, row in input_df.iterrows():
                item_name = row[target_col]
                if pd.isna(item_name) or str(item_name).strip() == "" or "ITEM" in str(item_name): continue
                
                # 매핑 및 계산 (생략된 로직은 DB 연동)
                processed_data.append([idx + 1, "CODE-X", item_name, 1, 0, 0]) # 예시 데이터

            # 4. 동적 인젝션 (Openpyxl)
            wb = load_workbook(output_path)
            ws = wb.active
            
            start_row = 16
            # 데이터가 많을 경우 행 삽입 로직 (박부장 지시사항)
            if len(processed_data) > 10:
                ws.insert_rows(start_row + 1, amount=len(processed_data)-10)
            
            for r_idx, row_data in enumerate(processed_data):
                for c_idx, value in enumerate(row_data):
                    ws.cell(row=start_row + r_idx, column=c_idx + 2, value=value)
            
            wb.save(output_path)
            logger.info(f"✅ 스마트 변환 완료: {output_path.name}")
            
        except Exception as e:
            logger.error(f"❌ 오류 발생: {str(e)}")

    def process_all(self):
        files = list(INPUT_DIR.glob("*.xlsx"))
        for f in files: self.process_file(f)

if __name__ == "__main__":
    AutoPOManager().process_all()
