# web/app.py
# 🚀 Render 플랫폼 Start Command 대응을 위한 포워딩 엔트리포인트
# 최상위 app_main.py의 Flask app 인스턴스를 동적으로 바인딩하여 실행합니다.

import os
import sys
from pathlib import Path

# 최상위 프로젝트 루트 디렉토리를 sys.path에 수동 바인딩
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

# 최신 2.0 엔진(app_main.py)의 Flask 앱 객체 임포트
from app_main import app

if __name__ == '__main__':
    # 클라우드/Render 환경 포트 바인딩 및 구동
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
