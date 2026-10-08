"""Fix remaining garbled path fragments in start.bat."""
from pathlib import Path

bat_path = Path(r"D:\西客松\start.bat")
text = bat_path.read_bytes().decode("utf-8")

# Fix remaining fragments
replacements = [
    ("西客松鏉綷backend", "西客松\\backend"),
    ("西客松鏉綷scripts", "西客松\\scripts"),
    ("西客松鏉綷", "西客松\\"),
    ('"D:\\西客松？', '"D:\\西客松"'),
    ("D:\\西客松？", "D:\\西客松"),
    ("西客松？", "西客松"),
]

for old, new in replacements:
    count = text.count(old)
    if count > 0:
        print(f"  replace {old!r} -> {new!r}: {count}")
        text = text.replace(old, new)

# Normalize CRLF
text = text.replace("\r\n", "\n").replace("\n", "\r\n")
bat_path.write_bytes(text.encode("utf-8"))

# Verify
verify = bat_path.read_bytes().decode("utf-8")
import re
garbled = re.findall(r'D:\\[^\x00-\x7f]+', verify)
if garbled:
    print(f"WARNING: garbled remaining: {garbled[:5]}")
else:
    print("OK: no garbled paths")

# Show lines 29-47
lines = verify.split("\r\n")
for i in range(28, 48):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}")