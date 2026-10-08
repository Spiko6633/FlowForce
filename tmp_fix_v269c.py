"""Fix the cd /d lines with trailing garbled char."""
from pathlib import Path

bat_path = Path(r"D:\西客松\start.bat")
text = bat_path.read_bytes().decode("utf-8")

# Find lines with cd /d "D:\西客松 followed by non-ASCII
import re
# Replace cd /d "D:\西客松<any non-quote>" -> cd /d "D:\西客松"
text = re.sub(r'cd /d "D:\\西客松[^"]*"', 'cd /d "D:\\西客松"', text)

# Also fix any remaining D:\西客松<non-ascii> patterns
# But be careful not to break D:\西客松\backend etc
# Only fix D:\西客松 followed by a non-ASCII char that's not backslash
text = re.sub(r'D:\\西客松([^\x00-\x7f\\])', r'D:\\西客松', text)

# Normalize CRLF
text = text.replace("\r\n", "\n").replace("\n", "\r\n")
bat_path.write_bytes(text.encode("utf-8"))

# Verify
verify = bat_path.read_bytes().decode("utf-8")
garbled = re.findall(r'D:\\西客松[^\x00-\x7f\\]', verify)
if garbled:
    print(f"WARNING: garbled remaining: {garbled[:5]}")
else:
    print("OK: no garbled after 西客松")

lines = verify.split("\r\n")
for i in [32, 33, 34, 44, 45, 46]:
    if i < len(lines):
        print(f"{i+1}: {lines[i]}")