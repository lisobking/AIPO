import os
import sys
import logging
import sqlite3
import shutil
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from flask import Flask, request, jsonify, send_file

PROJECT_ROOT = Path(__file__).parent.resolve()
INPUT_DIR = PROJECT_ROOT / "workspace" / "01_input_quotes"
OUTPUT_DIR = PROJECT_ROOT / "workspace" / "02_output_pos"
TEMPLATE_FILE = PROJECT_ROOT / "template" / "Standard_PO_Template.xlsx"

# 견적서 초안 생성 파이프라인 경로
EFFORT_INPUT_DIR = PROJECT_ROOT / "workspace" / "03_input_effort"
QUOTE_OUTPUT_DIR = PROJECT_ROOT / "workspace" / "04_output_quotes"
LOG_DIR = PROJECT_ROOT / "logs"
WEB_DIR = PROJECT_ROOT / "web"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler(LOG_DIR / "system_security.log", encoding='utf-8'),
                              logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("ParkDirector")

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path='/static')

class AutoPOManager:
    def __init__(self):
        self.ensure_directories()
        
    def ensure_directories(self):
        for path in [INPUT_DIR, OUTPUT_DIR, LOG_DIR, EFFORT_INPUT_DIR, QUOTE_OUTPUT_DIR]:
            path.mkdir(parents=True, exist_ok=True)

    def find_header_row(self, df):
        for i, row in df.iterrows():
            if any('품목' in str(val) or 'ITEM' in str(val) for val in row):
                return i
        return 0

    def process_file(self, file_path):
        output_path = OUTPUT_DIR / f"PO_{file_path.stem}.xlsx"
        try:
            df_raw = pd.read_excel(file_path, header=None)
            header_idx = self.find_header_row(df_raw)
            input_df = pd.read_excel(file_path, header=header_idx)
            
            shutil.copy(TEMPLATE_FILE, output_path)
            wb = load_workbook(output_path)
            ws = wb.active
            
            target_col = next((c for c in input_df.columns if '품목' in str(c) or 'ITEM' in str(c)), input_df.columns[0])
            price_col = next((c for c in input_df.columns if '단가' in str(c) or 'PRICE' in str(c)), None)
            
            start_row = 16 
            
            r_idx = 0
            for _, row in input_df.iterrows():
                item_name = row[target_col]
                if pd.isna(item_name) or str(item_name).strip() == "" or "ITEM" in str(item_name): continue
                price = row[price_col] if price_col else 0
                
                # 박부장: 동적 행 삽입
                if r_idx >= 10:
                    ws.insert_rows(start_row + r_idx)
                
                ws.cell(row=start_row + r_idx, column=2, value=r_idx + 1)
                ws.cell(row=start_row + r_idx, column=3, value=f"AUTO-CD-{r_idx}")
                ws.cell(row=start_row + r_idx, column=4, value=item_name)
                ws.cell(row=start_row + r_idx, column=5, value=1)
                ws.cell(row=start_row + r_idx, column=6, value=price)
                ws.cell(row=start_row + r_idx, column=7, value=price)
                r_idx += 1
                
            wb.save(output_path)
            return str(output_path)
        except Exception as e:
            logger.error(f"File Parse Error: {e}")
            raise

    def find_effort_header(self, df):
        """공수산정서 헤더 행 탐지: '순번', '항목', '공수' 키워드 기반"""
        for i, row in df.iterrows():
            row_str = ' '.join([str(v) for v in row if str(v) != 'nan'])
            if ('순번' in row_str or '번호' in row_str) and ('항목' in row_str or '내역' in row_str):
                return i
        return 0

    def find_effort_col(self, columns):
        """공수(M/D) 컬럼 자동 탐지"""
        for c in columns:
            cs = str(c)
            if '공수' in cs or 'M/D' in cs or 'MD' in cs or 'man' in cs.lower():
                return c
        return None

    def find_item_col(self, columns):
        """항목명 컬럼 자동 탐지"""
        for c in columns:
            cs = str(c)
            if '항목' in cs or '내역' in cs or '설명' in cs:
                return c
        return columns[1] if len(columns) > 1 else columns[0]

    def process_effort_to_quote(self, file_path, unit_price, template_path=None):
        """공수산정내역서 → 견적서 초안 변환"""
        output_path = QUOTE_OUTPUT_DIR / f"견적초안_{file_path.stem}.xlsx"
        try:
            df_raw = pd.read_excel(file_path, header=None)
            header_idx = self.find_effort_header(df_raw)
            effort_df = pd.read_excel(file_path, header=header_idx)

            item_col = self.find_item_col(effort_df.columns)
            effort_col = self.find_effort_col(effort_df.columns)

            items = []
            for _, row in effort_df.iterrows():
                item_name = row[item_col] if item_col else None
                md_val = row[effort_col] if effort_col else None

                if pd.isna(item_name) or str(item_name).strip() == '':
                    continue
                if pd.isna(md_val):
                    continue
                try:
                    md_float = float(md_val)
                except (ValueError, TypeError):
                    continue
                if md_float <= 0:
                    continue

                items.append({
                    'name': str(item_name).strip(),
                    'md': md_float,
                    'amount': md_float * unit_price
                })

            if template_path and Path(template_path).exists():
                shutil.copy(template_path, output_path)
                wb = load_workbook(output_path)
            else:
                from openpyxl import Workbook
                wb = Workbook()

            ws = wb.active

            # 견적서 헤더
            ws['A1'] = '견적서 초안 (Auto-Generated)'
            ws['A3'] = '순번'
            ws['B3'] = '항목'
            ws['C3'] = '공수(M/D)'
            ws['D3'] = f'단가(₩{unit_price:,.0f})'
            ws['E3'] = '금액'

            total = 0
            for idx, item in enumerate(items):
                r = 4 + idx
                ws.cell(row=r, column=1, value=idx + 1)
                ws.cell(row=r, column=2, value=item['name'])
                ws.cell(row=r, column=3, value=item['md'])
                ws.cell(row=r, column=4, value=unit_price)
                ws.cell(row=r, column=5, value=item['amount'])
                total += item['amount']

            summary_row = 4 + len(items) + 1
            ws.cell(row=summary_row, column=2, value='합계 (V.A.T 별도)')
            ws.cell(row=summary_row, column=3, value=sum(i['md'] for i in items))
            ws.cell(row=summary_row, column=5, value=total)

            wb.save(output_path)
            logger.info(f"견적 초안 생성 완료: {output_path} ({len(items)}건, 합계: ₩{total:,.0f})")
            return str(output_path)
        except Exception as e:
            logger.error(f"Effort→Quote Error: {e}")
            raise

manager = AutoPOManager()

@app.route('/')
def index():
    return send_file(WEB_DIR / 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    file_path = INPUT_DIR / file.filename
    file.save(file_path)
    
    try:
        out_path = manager.process_file(file_path)
        return send_file(out_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Upload process failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload_quote', methods=['POST'])
def upload_quote():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    unit_price = request.form.get('unit_price', 1350000)
    try:
        unit_price = float(unit_price)
    except (ValueError, TypeError):
        unit_price = 1350000

    file_path = EFFORT_INPUT_DIR / file.filename
    file.save(file_path)

    try:
        out_path = manager.process_effort_to_quote(file_path, unit_price)
        return send_file(out_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Quote generation failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 서버 시작: http://localhost:5001")
    app.run(port=5001, debug=True)
