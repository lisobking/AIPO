import pandas as pd
from pathlib import Path

def create_test_quote():
    data = {
        '품목명': ['4K 모니터 32인치', '무선 키보드 세트'],
        '수량': [5, 10]
    }
    df = pd.DataFrame(data)
    
    output_path = Path("/Users/lisob/Desktop/project2/AutoPO_Project/workspace/01_input_quotes/Samsong_Quote.xlsx")
    df.to_excel(output_path, index=False)
    print(f"📄 테스트 견적서 생성 완료: {output_path.name}")

if __name__ == "__main__":
    create_test_quote()
