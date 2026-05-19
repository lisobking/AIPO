import os
import subprocess

timeline_dir = "/Users/lisob/Desktop/project2/AutoPO_Project/docs/timeline"
entries_dir = os.path.join(timeline_dir, "entries")
index_file = os.path.join(timeline_dir, "index.md")

os.makedirs(entries_dir, exist_ok=True)

cmd = 'git log --format="%h|%cs|%s" -n 5 d0866de'
output = subprocess.check_output(cmd, shell=True, text=True)

commits = output.strip().split('\n')
commits.reverse() # Oldest first

lines_to_append = []

for commit in commits:
    parts = commit.split('|', 2)
    if len(parts) < 3: continue
    h, date, msg = parts
    date_clean = date.replace('-', '')
    
    c_type = "feat"
    msg_lower = msg.lower()
    if "fix" in msg_lower or "corruption" in msg_lower: c_type = "fix"
    elif "opening" in msg_lower or "init" in msg_lower: c_type = "arch"
    
    filename = f"{date_clean}_{c_type}_{h}.md"
    filepath = os.path.join(entries_dir, filename)
    
    content = f"""# 📝 {msg}

- **일시:** {date}
- **담당 에이전트:** PM (소급 기록)
- **작업 유형:** `{c_type}`
- **Git Commit:** `{h}`

## 🎯 소급 기록 (Retroactive Log)
- 과거 작업 내역 일괄 소급.
- {msg}
- 상세 코드 변경 내역은 VS Code 타임라인 및 Git 내역 참조.

## ✅ 검증 결과 (Verification)
- 소급 처리 완료.
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    summary = msg.replace('|', '').strip()
    if len(summary) > 50: summary = summary[:47] + "..."
    lines_to_append.append(f"| {date} | `{c_type}` | {summary} | `{h}` | [상세보기](./entries/{filename}) |")

with open(index_file, "a", encoding="utf-8") as f:
    f.write("\n" + "\n".join(lines_to_append) + "\n")

print("소급 완료")
