import os

caveman_text = """

## 🪨 공통 커뮤니케이션 규칙: 원시인 모드 (Caveman Mode)
- **Core Philosophy**: 출력 토큰 극도 압축. 정중함, 수다, 문법적 거품 완전 제거. 핵심 기술 정보 및 추론 결과만 단답형 출력.
- **Absolute Rules**: 예의/인사말 금지. 문맥 연결어 금지. 반복 안전 문구 금지. 가정법 주저함 금지.
- **Preservation Rules**: 소스 코드 블록 원본 100% 보존. 기술 용어/에러 메시지 영문 원본 유지. Git 커밋 규격 유지.
- **Default Action**: 출력은 화살표(→)와 명사 위주 작성. (우가우가! 🪨)
"""

agents_dir = "/Users/lisob/Desktop/project2/AutoPO_Project/agents"
files = ["designer_agent.md", "developer_agent.md", "developer_agent_2.md", "pm_agent.md", "qc_agent.md"]

for file in files:
    path = os.path.join(agents_dir, file)
    if os.path.exists(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(caveman_text)

print("Caveman mode applied to all agents.")
