import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import pdfplumber
import re
from copy import copy

# 프로젝트 루트 및 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
UPLOAD_FOLDER = PROJECT_ROOT / "workspace" / "01_input_quotes"
RESULT_FOLDER = PROJECT_ROOT / "workspace" / "02_output_pos"
# 새로 지정된 샘플 발주서를 표준 템플릿으로 사용 (자사 정보 보존용)
STD_TEMPLATE = PROJECT_ROOT / "template" / "Standard_PO_Template.xlsx"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

# 디렉토리 보장
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

class PDFQuoteProcessor:
    """개발자 2: 지능형 PDF 문맥 분석 엔진"""
    def process(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            tables = [page.extract_table() for page in pdf.pages]
            
        items = []
        for table in tables:
            if not table: continue
            for row in table:
                if not row or not any(row): continue
                
                # 행 전체에서 가장 이름다운 텍스트 찾기
                name = ""
                price = 0
                noise = ["발신자", "주소", "종목", "사업부", "유효기간", "고객사", "견적명", "합계", "총액", "이건창호", "가온아이", "ITEM", "MODEL"]
                
                for val in row:
                    v_str = str(val).strip()
                    if len(v_str) > 2 and not any(k in v_str for k in noise):
                        if not name or len(v_str) > len(name): # 가장 긴 텍스트를 이름 후보로
                            name = v_str
                    
                    # 가격 탐색
                    try:
                        s = v_str.replace(',', '').replace('원', '')
                        if s.replace('.','').isdigit() and float(s) > 1000:
                            price = float(s)
                    except: pass

                if not name or any(k in name.upper() for k in ["TEL", "FAX", "EMAIL", "■", "★"]): continue
                
                details = []
                for val in row:
                    v_str = str(val).strip()
                    if '\n' in v_str or '-' in v_str or '기간' in v_str:
                        details.extend([d.strip() for d in v_str.split('\n') if len(d.strip()) > 2 and d != name])

                if price > 0 or any(k in name.upper() for k in ["유지보수", "EDITOR", "에디터", "SERVER", "서버", "MAINTENANCE"]):
                    if not any(item['main'] == name for item in items):
                        items.append({'main': name, 'details': details, 'qty': 1, 'price': price})
        return items

class WebPOManager:
    """개발자 1: 엑셀 무결성 제어 및 시스템 통합"""
    def find_header_row(self, file_path):
        df_raw = pd.read_excel(file_path, header=None)
        for i, row in df_raw.iterrows():
            row_text = "".join([str(val).replace(" ", "") for val in row if not pd.isna(val)])
            if any(k in row_text for k in ['품목', '품명', 'ITEM', 'DESCRIPTION']): return i
        return 0

    def convert(self, file_path):
        ext = file_path.suffix.lower()
        items_to_write = []
        
        # 1. 데이터 추출
        if ext == '.pdf':
            pdf_engine = PDFQuoteProcessor()
            items_to_write = pdf_engine.process(file_path)
        else:
            header_idx = self.find_header_row(file_path)
            input_df = pd.read_excel(file_path, header=header_idx)
            
            # 컬럼 매핑 (주인공인 '품명'을 최우선 탐색)
            cols = [str(c).replace(" ", "").upper() for c in input_df.columns]
            def find_col(aliases, default_idx):
                for alias in aliases:
                    for i, col in enumerate(cols):
                        if alias in col: return input_df.columns[i]
                return input_df.columns[default_idx]

            target_col = find_col(['품명', 'ITEMNAME', 'DESCRIPTION', '품목'], 2)
            qty_col = find_col(['수량', 'QTY', 'QUANTITY'], 5)
            price_col = find_col(['단가', 'PRICE', 'UNITPRICE', '공급가', '공급단가', 'PRICE', 'COST'], 4)

            def safe_float(val):
                if pd.isna(val): return 0.0
                try:
                    # 모든 화폐 기호 및 콤마 제거
                    s = re.sub(r'[^0-9.]', '', str(val))
                    return float(s) if s else 0.0
                except: return 0.0

            # 3. 데이터 패턴 자동 보정 (중요: 키워드 매핑이 의심될 때 숫자가 많은 열을 수량/단가로 재지정)
            numeric_counts = input_df.select_dtypes(include=['number']).count()
            if len(numeric_counts) >= 2:
                # 숫자가 가장 많은 두 열을 단가와 수량 후보로 검토
                top_numeric_cols = numeric_counts.sort_values(ascending=False).index.tolist()
                # 단가는 보통 금액이 크므로, 평균값이 큰 쪽을 가격으로 추정하는 지능형 로직
                col1_vals = pd.to_numeric(input_df[top_numeric_cols[0]], errors='coerce').fillna(0)
                col2_vals = pd.to_numeric(input_df[top_numeric_cols[1]], errors='coerce').fillna(0)
                col1_avg = col1_vals.mean()
                col2_avg = col2_vals.mean()
                
                # 기존 매핑이 부실할 경우(평균 0) 보정
                current_price_avg = pd.to_numeric(input_df[price_col], errors='coerce').fillna(0).mean()
                current_qty_avg = pd.to_numeric(input_df[qty_col], errors='coerce').fillna(0).mean()

                if current_price_avg == 0:
                    price_col = top_numeric_cols[0] if col1_avg > col2_avg else top_numeric_cols[1]
                if current_qty_avg == 0:
                    qty_col = top_numeric_cols[1] if col1_avg > col2_avg else top_numeric_cols[0]

            processed = []
            noise_keywords = ["견적문의", "TEL", "FAX", "이메일", "■", "★", "TOTAL", "합계", "문의", "<", ">", "WWW.", "HTTP"]

            for _, row in input_df.iterrows():
                # 품명 열 데이터를 강제로 문자열로 변환하여 에러 방지
                name = str(row[target_col]).strip() if not pd.isna(row[target_col]) else ""
                name_upper = name.upper()
                if not name or name_upper in ["ITEM", "QTY", "PRICE", "MODELNO.", "품목", "NO", "DESCRIPTION"]: continue
                if any(k in name_upper for k in noise_keywords): continue
                
                qty = safe_float(row[qty_col])
                price = safe_float(row[price_col])

                if qty > 0 or price > 0:
                    processed.append({'main': name, 'details': [], 'qty': qty, 'price': price})
                elif processed and len(name) > 1:
                    processed[-1]['details'].append(name)
            items_to_write = processed

        # 2. 템플릿 기반 주입 (자사 정보 보존 전략)
        output_filename = f"PO_Draft_{file_path.stem}.xlsx"
        output_path = RESULT_FOLDER / output_filename
        shutil.copy(STD_TEMPLATE, output_path)
        
        wb = load_workbook(output_path)
        ws = wb.active
        
        # 본문 영역(18행 이하)만 정화 후 데이터 주입
        start_row = 18
        for r in range(start_row, start_row + 30):
            for c in range(2, 8):
                try: ws.cell(row=r, column=c).value = None
                except: pass

        current_row = start_row
        item_no = 1
        for idx, item in enumerate(items_to_write):
            # 대분류(수량/단가 모두 0)인 경우 NO 생략
            if item['qty'] > 0 or item['price'] > 0:
                ws.cell(row=current_row, column=2, value=item_no)
                item_no += 1
            
            ws.cell(row=current_row, column=4, value=item['main'])
            
            # 0이 아닌 경우만 값 주입 (여백의 미)
            if item['qty'] > 0: ws.cell(row=current_row, column=5, value=item['qty'])
            if item['price'] > 0: ws.cell(row=current_row, column=6, value=item['price'])
            if item['qty'] > 0 and item['price'] > 0:
                ws.cell(row=current_row, column=7, value=item['qty'] * item['price'])
            
            ws.cell(row=current_row, column=4).alignment = Alignment(wrapText=True, vertical='center')
            current_row += 1
            
            for detail in item['details']:
                ws.insert_rows(current_row)
                target_cell = ws.cell(row=current_row, column=4, value=f"- {detail.strip()}")
                # 디자이너의 터치: 상세내역 들여쓰기 및 폰트 크기 조절
                target_cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
                
                # 개발자 1: 서식(테두리 등) 완벽 복제
                for c in range(2, 8):
                    source_cell = ws.cell(row=start_row, column=c)
                    new_cell = ws.cell(row=current_row, column=c)
                    if source_cell.has_style:
                        new_cell.border = copy(source_cell.border)
                        new_cell.font = copy(source_cell.font)
                current_row += 1

        wb.save(output_path)
        return output_filename

@app.route('/')
def index(): return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    file_path = UPLOAD_FOLDER / file.filename
    file.save(str(file_path))
    manager = WebPOManager()
    res_name = manager.convert(file_path)
    return jsonify({'success': True, 'filename': res_name})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(str(RESULT_FOLDER), filename, as_attachment=True)

if __name__ == '__main__':
    # Render 등 클라우드 환경의 포트 대응
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
