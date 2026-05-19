# 📝 박부장 에이전트 하네스 적용 및 README 카파시 방법론 개편

- **일시:** 2026-05-19
- **담당 에이전트:** Antigravity (AI Assistant)
- **작업 유형:** `docs`

## 🎯 목표 (Goal)
- 박부장(개발자 에이전트)이 불필요한 소스코드를 수정하거나 추가(Over-engineering)하지 않도록 강력한 하네스(Harness) 규칙 적용.
- 프로젝트 전체의 컨텍스트를 LLM 및 에이전트가 완벽하게 이해할 수 있도록 안드레이 카파시(Andrej Karpathy)의 MD 작성 방법론을 `README.md`에 적용.

## 🛠 수정/생성된 파일 (Touched Files)
1. **`agents/developer_agent.md`**
   - 내용: `🛡️ 하네스 엔지니어링 (Harness Engineering) 제약 사항` 섹션 추가.
   - 효과: 범위 격리(Scope Isolation), YAGNI 원칙, 환각 방지 등 에이전트 행동 지침 강제.
2. **`README.md`**
   - 내용: 기존의 일반적인 깃허브 소개글에서 '단일 진실 공급원(Single Source of Truth)' 역할을 하는 LLM 최적화 스펙 문서로 전면 개편.
   - 효과: 아키텍처, 디렉토리 권한, 하네스 방법론을 글로벌하게 명시하여 에이전트 간 컨텍스트 정렬.

## ✅ 검증 결과 (Verification)
- 마크다운 문법 오류 없이 정상적으로 파일이 저장되었음.
- 프로젝트의 실제 소스코드(`app_main.py` 등)는 전혀 건드리지 않고, 시스템 프롬프트(문서) 레벨에서의 통제력 확보 성공.

## ⏭️ 다음 작업자를 위한 인수인계 (Handover)
- 이후 코딩 관련 작업(예: Excel 파싱 엔진 수정 등)이 배정되면, 에이전트는 가장 먼저 변경된 `README.md`를 읽어 디렉토리 접근 권한을 확인해야 합니다.
- 개발 로직 변경 시 `agents/developer_agent.md`에 명시된 하네스 규칙에 따라 의존성 추가나 과도한 확장을 삼가고 지시된 타겟 코드만 수정해야 합니다.
