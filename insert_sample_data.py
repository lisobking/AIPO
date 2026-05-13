import sqlite3
from pathlib import Path

def insert_samples(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 샘플 거래처 등록
    providers = [
        ('삼송전자', '02-123-4567'),
        ('헬지디스플레이', '02-987-6543'),
        ('애뿔코리아', '010-1111-2222')
    ]
    cursor.executemany("INSERT OR IGNORE INTO providers (name, contact) VALUES (?, ?)", providers)

    # 2. 샘플 품목 매핑 (업체 품목명 -> 내부 코드)
    # 삼송전자(ID: 1)
    mappings = [
        (1, '4K 모니터 32인치', 'MON-32-4K', 450000),
        (1, '무선 키보드 세트', 'KB-WL-GEN', 35000),
        (2, 'OLED 패널 55', 'PNL-55-OLED', 1200000),
        (3, 'M3 맥북 에어', 'LAP-MB-M3', 1590000)
    ]
    cursor.executemany("INSERT OR IGNORE INTO item_mapping (provider_id, provider_item_name, internal_item_code, unit_price) VALUES (?, ?, ?, ?)", mappings)

    conn.commit()
    conn.close()
    print("✅ PM: 샘플 데이터(거래처 3곳, 매핑 4건) 주입 완료.")

if __name__ == "__main__":
    DB_PATH = Path(__file__).parent / "settings.db"
    insert_samples(DB_PATH)
