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
                from openpyxl.styles import Font, Alignment, Border, Side, PatternFill, numbers
                wb = Workbook()

            ws = wb.active
            ws.title = '견적서'

            # 스타일 정의
            from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
            header_font = Font(name='맑은 고딕', size=16, bold=True)
            col_font = Font(name='맑은 고딕', size=10, bold=True, color='FFFFFF')
            data_font = Font(name='맑은 고딕', size=10)
            summary_font = Font(name='맑은 고딕', size=11, bold=True)
            center = Alignment(horizontal='center', vertical='center', wrap_text=True)
            left = Alignment(horizontal='left', vertical='center', wrap_text=True)
            right = Alignment(horizontal='right', vertical='center')
            thin_border = Border(
                left=Side(style='thin', color='CCCCCC'),
                right=Side(style='thin', color='CCCCCC'),
                top=Side(style='thin', color='CCCCCC'),
                bottom=Side(style='thin', color='CCCCCC')
            )
            thick_border = Border(
                left=Side(style='thin', color='333333'),
                right=Side(style='thin', color='333333'),
                top=Side(style='medium', color='333333'),
                bottom=Side(style='medium', color='333333')
            )
            header_fill = PatternFill(start_color='2C3E50', end_color='2C3E50', fill_type='solid')
            alt_fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')
            summary_fill = PatternFill(start_color='EBF5FB', end_color='EBF5FB', fill_type='solid')

            # 컬럼 너비
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 35
            ws.column_dimensions['C'].width = 14
            ws.column_dimensions['D'].width = 18
            ws.column_dimensions['E'].width = 22

            # 타이틀
            ws.merge_cells('A1:E1')
            title_cell = ws['A1']
            title_cell.value = '기 술 지 원  견 적 서  (초안)'
            title_cell.font = header_font
            title_cell.alignment = Alignment(horizontal='center', vertical='center')

            ws.merge_cells('A2:E2')
            ws['A2'].value = f'M/D 단가: ₩{unit_price:,.0f} 기준 | Auto-Generated by AutoPO'
            ws['A2'].font = Font(name='맑은 고딕', size=9, color='888888')
            ws['A2'].alignment = Alignment(horizontal='center')

            # 헤더 행
            headers = ['순번', '항 목', '공수(M/D)', '단가(원)', '금액(원)']
            for col_idx, h in enumerate(headers, 1):
                cell = ws.cell(row=3, column=col_idx, value=h)
                cell.font = col_font
                cell.fill = header_fill
                cell.alignment = center
                cell.border = thin_border

            # 데이터 행
            total = 0
            for idx, item in enumerate(items):
                r = 4 + idx
                row_fill = alt_fill if idx % 2 == 1 else PatternFill()

                ws.cell(row=r, column=1, value=idx + 1).font = data_font
                ws.cell(row=r, column=1).alignment = center
                ws.cell(row=r, column=2, value=item['name']).font = data_font
                ws.cell(row=r, column=2).alignment = left
                ws.cell(row=r, column=3, value=item['md']).font = data_font
                ws.cell(row=r, column=3).alignment = center
                ws.cell(row=r, column=4, value=unit_price).font = data_font
                ws.cell(row=r, column=4).alignment = right
                ws.cell(row=r, column=4).number_format = '#,##0'
                ws.cell(row=r, column=5, value=item['amount']).font = data_font
                ws.cell(row=r, column=5).alignment = right
                ws.cell(row=r, column=5).number_format = '#,##0'
                total += item['amount']

                for c in range(1, 6):
                    ws.cell(row=r, column=c).border = thin_border
                    if row_fill.fill_type:
                        ws.cell(row=r, column=c).fill = row_fill

            # 합계 행
            summary_row = 4 + len(items)
            ws.cell(row=summary_row, column=1, value='').border = thick_border
            ws.cell(row=summary_row, column=2, value='합 계 (V.A.T 별도)').font = summary_font
            ws.cell(row=summary_row, column=2).alignment = center
            ws.cell(row=summary_row, column=3, value=sum(i['md'] for i in items)).font = summary_font
            ws.cell(row=summary_row, column=3).alignment = center
            ws.cell(row=summary_row, column=4, value='').border = thick_border
            ws.cell(row=summary_row, column=5, value=total).font = summary_font
            ws.cell(row=summary_row, column=5).alignment = right
            ws.cell(row=summary_row, column=5).number_format = '#,##0'
            for c in range(1, 6):
                ws.cell(row=summary_row, column=c).border = thick_border
                ws.cell(row=summary_row, column=c).fill = summary_fill

            # VAT 행
            vat_row = summary_row + 1
            ws.cell(row=vat_row, column=2, value='부가세 (10%)').font = data_font
            ws.cell(row=vat_row, column=2).alignment = center
            ws.cell(row=vat_row, column=5, value=total * 0.1).font = data_font
            ws.cell(row=vat_row, column=5).alignment = right
            ws.cell(row=vat_row, column=5).number_format = '#,##0'
            for c in range(1, 6):
                ws.cell(row=vat_row, column=c).border = thin_border

            # 총합계 행
            grand_row = vat_row + 1
            ws.cell(row=grand_row, column=2, value='총 합 계 (V.A.T 포함)').font = Font(name='맑은 고딕', size=12, bold=True)
            ws.cell(row=grand_row, column=2).alignment = center
            ws.cell(row=grand_row, column=5, value=total * 1.1).font = Font(name='맑은 고딕', size=12, bold=True)
            ws.cell(row=grand_row, column=5).alignment = right
            ws.cell(row=grand_row, column=5).number_format = '#,##0'
            for c in range(1, 6):
                ws.cell(row=grand_row, column=c).border = thick_border
                ws.cell(row=grand_row, column=c).fill = PatternFill(start_color='D5F5E3', end_color='D5F5E3', fill_type='solid')

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
