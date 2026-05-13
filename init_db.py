import sqlite3
import os
from pathlib import Path

def init_db(db_path):
    """박부장이 승인한 매핑 DB 초기화 및 스키마 설계"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 거래처 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. 품목 매핑 테이블 (성능을 위해 인덱스 추가)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id INTEGER,
        provider_item_name TEXT NOT NULL,
        internal_item_code TEXT NOT NULL,
        unit_price REAL,
        FOREIGN KEY (provider_id) REFERENCES providers (id),
        UNIQUE(provider_id, provider_item_name)
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mapping_provider ON item_mapping(provider_id)')

    # 3. 변환 이력 테이블 (보안 및 추적용)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversion_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        input_file TEXT NOT NULL,
        output_file TEXT,
        status TEXT, -- SUCCESS, FAILED
        error_message TEXT,
        processed_items INTEGER
    )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ 박부장: 'settings.db'가 성공적으로 초기화되었습니다. (경로: {db_path})")

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent
    DB_PATH = PROJECT_ROOT / "settings.db"
    init_db(DB_PATH)
