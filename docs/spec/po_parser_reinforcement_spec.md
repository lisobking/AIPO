# 👔 [기술 사양서] 발주서(PO) 변환 엔진 기능 보강 규격서

> **문서 식별자:** `SP-20260520-PO-REINFORCE`  
> **상태:** `APPROVED (대기 중)`  
> **목적:** 추후 사용자의 개발 재개 명령 시, 즉시 코드를 수정하고 배포할 수 있도록 세부 설계 사양 및 구현 방안을 보존합니다.

---

## 📅 1. 개요 및 배경

현재 AutoPO Draft Master 2.0의 **발주서(PO) 변환기(`app_main.py` 내 `process_file`)**는 기본적인 품목명 매핑만 수행하는 초기 단계에 머물러 있습니다. 

실제 기업용 발주서로서 완전한 신뢰성과 격식을 확보하기 위해, 본 규격서의 가이드에 따라 **수량 동적 분석**, **기준 매핑 DB 연동**, **대용량 행 추가 시 스타일 보존**, 그리고 **PDF 파싱 하이브리드 연동**을 순차적으로 수행합니다.

---

## 🛠️ 2. 상세 개발 규격 (Technical Specifications)

### 📌 1단계: 견적서 수량(Quantity) 및 단가(Unit Price) 동적 파싱
* **대상 함수**: `app_main.py` -> `AutoPOManager.process_file`
* **구현 사양**:
  1. 입력 Excel 데이터프레임(`input_df`)의 컬럼 중 `수량`, `QTY`, `갯수` 등의 키워드가 포함된 컬럼을 자동으로 탐지합니다.
  2. 파싱 시 공백이나 문자가 섞인 경우(`10 개` 등) 정규식 `\d+`을 활용해 숫자만 정수형(`int`)으로 변환합니다.
  3. 변환된 실제 수량을 발주서 템플릿의 **E열(수량)**에 주입합니다.
     * `ws.cell(row=start_row + r_idx, column=5, value=parsed_qty)`

---

### 📌 2단계: 기준 매핑 DB(`settings.db`) 연동
* **대상 함수**: `app_main.py` -> `AutoPOManager.process_file`
* **구현 사양**:
  1. 변환 시작 시, 파일명에서 추출된 공급업체(Provider)명을 기반으로 데이터베이스를 조회합니다.
     ```python
     # 예시 로직
     conn = sqlite3.connect(PROJECT_ROOT / "settings.db")
     cursor = conn.cursor()
     cursor.execute("SELECT id FROM providers WHERE name = ?", (provider_name,))
     ```
  2. 추출된 품목명(`item_name`)으로 `item_mapping` 테이블을 조회하여 매핑된 **내부 공식 품목 코드**와 **단가**를 인출합니다.
  3. **코드 및 단가 매핑 정책**:
     * **DB 등록 품목**: 조회된 `internal_item_code`를 **C열**에 주입하고, DB 단가를 우선 적용하여 **F열**에 기입합니다.
     * **DB 미등록 품목**: 사용자의 승인 대기 지침에 따라 임의의 예비용 임시 코드인 **`TEMP-UNREG-[순번]`**으로 기입하고, 견적서에 표시된 원본 단가를 폴백(Fallback)으로 적용합니다.

---

### 📌 3단계: 10개 초과 대용량 품목 스타일 복제 (Design UX)
* **대상 함수**: `app_main.py` -> `AutoPOManager.process_file`
* **구현 사양**:
  1. `process_effort_to_quote`에 구현된 `copy_cell_style` 함수를 발주서 빌더에도 동일하게 이식합니다.
  2. 품목수가 10개 이상이 되어 `ws.insert_rows(start_row + r_idx)`가 실행될 때, 삽입된 새 행의 각 셀에 템플릿 기본 행(16행)의 **테두리(Borders), 폰트(Font), 정렬(Alignment) 스타일**을 완벽하게 복사합니다.

---

### 📌 4단계: 엑셀 연산 수식 표준화 및 합계 연동
* **대상 함수**: `app_main.py` -> `AutoPOManager.process_file`
* **구현 사양**:
  1. **합계 금액(G열)**: 단순 상수를 입력하는 대신, 자동 계산을 위한 수식 `=E{r}*F{r}`을 주입합니다.
  2. **하단 소계 및 세액/총계**:
     * 동적으로 늘어난 마지막 품목 행 바로 아래 영역을 스캔하여 소계 셀 위치를 파악합니다.
     * 해당 소계 셀에 `=SUM(G16:G{last_row})` 수식을 동적으로 빌드하여 주입합니다.

---

### 📌 5단계: PDF 견적서 하이브리드 파싱 통합
* **대상 라우터**: `app_main.py` -> `/upload`
* **구현 사양**:
  1. 업로드된 파일의 확장자가 `.pdf`인 경우, `PDFQuoteProcessor` 클래스를 활용해 데이터를 `DataFrame` 형태로 선제적으로 추출합니다.
  2. 추출 완료된 DataFrame을 `process_file` 함수에 인자로 전달하여 엑셀 템플릿에 안전하게 기록하도록 어댑터를 개편합니다.

---

## 🔍 3. 품질 검증(QC) 스크립트 리팩토링 규격

* **대상 파일**: `qc_validation.py`
* **구현 사양**:
  1. `in_df['수량'].sum()`과 생성된 발주서의 `out_df['수량'].sum()`을 비교할 때, 하드코딩 `1`로 인해 발생하던 정합성 오류를 검출 및 패스하도록 동적 대조 로직으로 업데이트합니다.
  2. DB 연동 후, 발주서 내 C열의 품목 코드들이 실제 DB의 `internal_item_code` 혹은 규정된 임시 코드 규격(`TEMP-UNREG-x`)과 일치하는지 교차 검증하는 검사 루틴을 신설합니다.

---

## 🚀 4. 추후 실행 명령어 가이드 (Run Book)

개발 재개 명령 수신 시, 다음 단계를 순서대로 집행하여 실 작업을 전개합니다.

```bash
# 1단계: DB 스키마 및 샘플 데이터 상태 점검
python3 init_db.py
python3 insert_sample_data.py

# 2단계: app_main.py 소스코드 수정 (본 기술사양서 2장 가이드 적용)

# 3단계: 로컬 QC 검증 수행 및 정합성 테스트 통과 확인
PYTHONPATH=. python3 qc_validation.py

# 4단계: Git 커밋 및 Render 원격 배포 트리거
git add app_main.py qc_validation.py
git commit -m "feat: 발주서(PO) 엔진 고도화 - 수량 동적 파싱, DB 연동 및 PDF 파서 통합"
git push origin main
```

---
**문서 보존처: /docs/spec/po_parser_reinforcement_spec.md**  
*Strategic PM Director Park & The Antigravity AI Team*
