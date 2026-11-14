import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('web/src/main.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if any(k in l for k in ['target-fingerprint', 'target-selector', 'innerHTML']):
        print(f"{i+1}: {l.strip()[:100]}")
