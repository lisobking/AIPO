# 📝 Flask 웹 서버 전환 및 드래그 앤 드롭 UI 구현

- **일시:** 2026-05-19
- **담당 에이전트:** PM, 박부장, 디자이너
- **작업 유형:** `feat`
- **Git Commit:** `cdefd4e`

## 🎯 목표 (Goal)
- 기존 CLI 스크립트를 Flask 웹 애플리케이션으로 전환.
- 드래그 앤 드롭 방식의 Apple 스타일 UI 구축.

## 🛠 수정/생성된 파일 (Touched Files)
1. **`app_main.py`**
   - Flask 라우팅(`/`, `/upload`) 추가.
   - 데이터 동적 삽입(`ws.insert_rows`) 적용.
2. **`web/index.html`** (신규)
   - UI/UX 구현 및 비동기 업로드 API 연동.

## ✅ 검증 결과 (Verification)
- 코드 레벨 작성 완료. (실제 런타임 테스트 대기)
- Git 커밋 `cdefd4e` 정상 동기화.

## ⏭️ 다음 작업자를 위한 인수인계 (Handover)
- **QC 에이전트**: 데이터 추출 무결성 검증 및 `pdf_processor.py` 연동 필요.
- **디자이너 에이전트**: 필요 시 `style.css` 외부 파일 분리 검토.
