# 📘 동적 공수산정서 파서 및 미지 고객사 대응 확장 사양서
*(Effort Parser Generic Extension & Specification Guide)*

## 🎯 1. 개요 및 목적
현재 AutoPO Draft Master 2.0 시스템은 개발 및 검증용 샘플인 `유한양행` 및 `NH투자증권` 등의 파일명을 기반으로 작동하고 있습니다. 
실운영 환경에서 **임의의 새로운 고객사 및 다양한 형태의 파일명/공수산정서 양식**이 업로드되더라도, 코드 변경 없이 지능적이고 동적으로 회사명과 제안 건명을 유추하여 표준 견적서 템플릿에 안전하게 정합시키기 위한 파서 확장 가이드라인과 설계 스펙을 기술합니다.

---

## ⚙️ 2. 파일명 기반 동적 메타데이터 유추 알고리즘
파일명에 포함될 수 있는 예측 불가한 문장 구조 속에서 **고객사명(Customer Name)**과 **제안건명(Proposal Subject)**을 추출하는 범용 정규화 파이프라인 설계안입니다.

### 2.1 구분자 기반 토큰 분리 엔진 (Delimiter-based Tokenizer)
파일명을 공백, 언더바(`_`), 대시(`-`) 등 표준 구분자로 파싱하여 토큰들을 배열화합니다.
- **규칙 1**: 첫 번째 토큰을 **고객사명**으로 유추합니다.
- **규칙 2**: 두 번째 토큰부터 "공수", "산정", "기술지원" 등 무효 키워드가 나오기 전까지의 문자열을 결합하여 **제안건명**으로 유추합니다.

```python
# [예시 확장 구현 코드안]
import re
import unicodedata

def extract_meta_from_filename(filename):
    # NFC 정규화 및 확장자 제거
    clean_name = unicodedata.normalize('NFC', Path(filename).stem)
    
    # 괄호 및 불필요한 날짜 패턴 제거 (예: (2), 2026.02.02 등)
    clean_name = re.sub(r'\(\d+\)', '', clean_name)
    clean_name = re.sub(r'\b\d{4}[.\-/]\d{2}[.\-/]\d{2}\b', '', clean_name)
    
    # 언더바, 대시, 공백 기준 분할
    tokens = [t.strip() for t in re.split(r'[_,\-\s]+', clean_name) if t.strip()]
    
    customer = "신규 고객사"
    subject = "그룹웨어 시스템 기술지원"
    
    if len(tokens) >= 1:
        customer = tokens[0]  # 첫 번째 토큰은 항상 회사/기관명
        
    if len(tokens) >= 2:
        # 무효 키워드가 아닌 토큰들을 제안건명으로 정합
        invalid_keywords = {"공수", "산정", "내역서", "ezMail60", "xlsx", "xls"}
        subject_tokens = [t for t in tokens[1:] if not any(k in t for k in invalid_keywords)]
        if subject_tokens:
            subject = " ".join(subject_tokens)
            
    return customer, subject
```

---

## 📊 3. 미지 공수산정서 엑셀 양식 유연성 가이드
고객사별로 업로드하는 엑셀 내의 컬럼 구조나 헤더 명칭이 불규칙할 때 대응하기 위한 **지능형 컬럼 탐색 사전(Synonyms Dictionary)** 설계 표준입니다.

### 3.1 키워드 동의어 매핑 레이어 (Synonyms Mapping Layer)
현재 `find_effort_col`과 `find_item_col`을 아래의 사전식 매핑 구조로 확장하여 유연성을 최대화합니다.

| 탐색 대상 셀 | 감지 핵심 키워드 사전 (Synonyms Dict) | 대체 컬럼 인덱스 (Fallback) |
| :--- | :--- | :--- |
| **공수 (M/D 수량)** | `['공수', 'M/D', 'MD', 'man/day', '수량', '인원', '공량', 'effort']` | `.xlsx` 파일에서 숫자로만 이루어진 열을 탐색하여 자동 맵핑 |
| **내역 (품목/기능명)** | `['항목', '내역', '설명', '품목', '기능', '작업', 'task', 'description']` | 공수 열의 왼쪽에 존재하는 가장 텍스트가 풍부한 열로 지정 |

---

## 🛠️ 4. 가온아이 표준 견적서 통합/분산 맵핑 전략 (Dual-Mode UI)
새로운 형태의 공수산정서가 들어왔을 때, 엑셀을 채우는 방식을 시스템 파라미터나 UI 옵션을 통해 **듀얼 모드(Dual-mode)**로 정합합니다.

### 1) 통합 표기 모드 (Template Preservation Mode)
- **대상**: 유한양행 등 대기업에 제출하는 고도로 간소화된 표준 견적서.
- **동작**: 템플릿의 원래 `프로젝트 관리`, `요구사항 설계`, `개발` 공정 틀을 그대로 유지한 채, `개발` 행 수량 셀에 파싱된 총합산 M/M 수량을 일괄 주입하고 개별 품목은 백업 시트나 세부 설명에만 둡니다.

### 2) 개별 품목 확장 모드 (Itemized Expansion Mode)
- **대상**: 중소기업이나 세부 공수 단가를 투명하게 1:1로 매칭해야 하는 중대형 제안서.
- **동작**: 공수산정서에 있는 모든 개별 품목들을 엑셀에 한 줄씩 삽입하여, 모든 세부 품목의 개별 수량(M/M)과 단가, 합계 수식을 일일이 바인딩하여 출력합니다.

---

## 📝 5. 다음 개발자/AI 에이전트를 위한 Action Items
- [ ] **파일명 정규화 테스트베드 구축**: `extract_meta_from_filename`을 탑재하여 미지 고객사 업로드 시 자동 감지 기능 시뮬레이션.
- [ ] **동의어 파싱 사전 DB화**: `app_main.py` 내의 헤더 탐지 로직에 유연한 정규식 키워드(Regex Synonyms) 주입.
- [ ] **UI 모드 스위치 추가**: 웹 UI 상에서 `통합 간소화 견적서`와 `세부 품목 기입 견적서` 중 하나를 사용자가 명시적으로 선택할 수 있도록 옵션 스위치 추가 고려.
