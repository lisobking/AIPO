import pdfplumber
import re
import pandas as pd
from pathlib import Path

class PDFQuoteProcessor:
    def __init__(self):
        self.item_pattern = re.compile(r'(CrossEditor\d+)')
        self.price_pattern = re.compile(r'견적\s*합계\(VAT별도\)\s*([\d,]+)')
        self.period_pattern = re.compile(r'(\d{4}\.\d{2}\.\d{2}\s*~\s*\d{4}\.\d{2}\.\d{2})')

    def extract_data(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() for page in pdf.pages])
            
        # 1. 품목명 추출
        item_match = self.item_pattern.search(full_text)
        item_name = f"{item_match.group(1)} 유지보수 (1년)" if item_match else "알 수 없는 품목"

        # 2. 금액 추출
        price_match = self.price_pattern.search(full_text)
        unit_price = int(price_match.group(1).replace(',', '')) if price_match else 0

        # 3. 기간 추출 (비고란 활용)
        period_match = self.period_pattern.search(full_text)
        remark = f"기간: {period_match.group(1)}" if period_match else ""

        # 표준 데이터프레임 형태로 반환
        return pd.DataFrame([{
            '품목': item_name,
            '수량': 1,
            '단가': unit_price,
            '비고': remark
        }])

if __name__ == "__main__":
    # 개발자 2의 로컬 테스트
    processor = PDFQuoteProcessor()
    sample_pdf = Path("/Users/lisob/Desktop/project2/AutoPO_Project/sample/2026-0418 가온아이(202606 이건창호 그룹웨어용 크로스에디터3 유지보수 1년 견적서).pdf")
    if sample_pdf.exists():
        df = processor.extract_data(sample_pdf)
        print("--- 개발자 2: PDF 데이터 구출 성공 ---")
        print(df)
