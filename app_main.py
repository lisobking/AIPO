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
        for path in [INPUT_DIR, OUTPUT_DIR, LOG_DIR]:
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

if __name__ == '__main__':
    logger.info("🚀 서버 시작: http://localhost:5001")
    app.run(port=5001, debug=True)
