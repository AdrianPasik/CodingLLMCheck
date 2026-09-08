# windows use lms log stream --source model --json | ForEach-Object { $_ } | python lm-studio-token-counter.py
# linux lms log stream --source model --json| python lm-studio-token-counter.py
import sys
import json

# Force standard input to read as UTF-8 on Windows
if sys.platform == "win32" or "win64":
    sys.stdin.reconfigure(encoding='utf-8')

for line in sys.stdin:
    if line.strip():
        try:
            log_data = json.loads(line)
            #print(f"Queued log at: {log_data.get('timestamp')}", flush=True)
        except json.JSONDecodeError:
            continue