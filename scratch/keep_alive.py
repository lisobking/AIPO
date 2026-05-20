import time
import urllib.request

URL = "https://aipo.onrender.com/"

print(f"🚀 Starting keep-alive ping for {URL}")
print("Render free tier containers sleep after 15 minutes of inactivity.")
print("This script pings the server every 10 minutes to keep it active 24/7.")
print("Press Ctrl+C to stop.\n")

while True:
    try:
        start_time = time.time()
        # 헤더를 추가하여 봇 필터링 우회 및 표준 브라우저 요청 모사
        req = urllib.request.Request(
            URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutoPO-KeepAlive/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.getcode()
            elapsed = time.time() - start_time
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🟢 Ping Success: Status {status} ({elapsed:.2f}s)")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🔴 Ping Failed: {e}")
    
    # Render 무료 티어의 15분 제한을 방지하기 위해 10분(600초) 간격으로 핑 전송
    time.sleep(600)
