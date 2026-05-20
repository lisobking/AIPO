# 📝 Render 무료 서버 슬립 방지용 Keep-Alive 스크립트 구축 및 배포 가이드 제공

- **일시:** 2026-05-20
- **담당 에이전트:** PM (박부장), 개발자 1 (클코)
- **작업 유형:** `feat` / `docs`
- **Git Commit:** `N/A` (로컬 스크립트 및 가이드 추가)

## 🎯 목표 (Goal)
- **Render 무료 티어 슬립 문제 해결**: Render 무료 웹 서비스의 15분 무동작 시 컨테이너 정지(Sleep) 현상으로 발생하는 최초 접속 지연(Cold Start, 약 50초 이상) 현상 해소.
- **24/7 가용성 확보**: 주기적인 자동 호출 메커니즘을 적용하여 상시 활성화 상태로 유지.

## 💡 해결 방안 (Proposed Solutions)
1. **로컬 무중단 Keep-Alive 스크립트 (`scratch/keep_alive.py`)**:
   - 외부 종속성 없이 표준 라이브러리(`urllib.request`)만을 사용하여 10분 간격으로 `https://aipo.onrender.com/`에 HTTP 겟 요청을 전송하는 경량화 Python 스크립트 작성.
2. **클라우드 기반 Keep-Alive 서비스 연동 가이드**:
   - 로컬 PC가 꺼져도 작동할 수 있도록 업계 표준 무료 모니터링 서비스인 **UptimeRobot** 또는 **cron-job.org**를 연동하여 무료 서버의 상시 기동을 영구 보장하는 가이드 제공.

## 🛠️ 추가된 파일 (Touched Files)
1. **`scratch/keep_alive.py` [NEW]**:
   - 10분 주기 자체 핑 전송용 Python 스크립트.

## ✅ 결과 검증 (Verification)
- `scratch/keep_alive.py` 파일 실행을 통한 HTTP 200 정상 응답 수신 확인 완료.
