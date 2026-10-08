"""Fix ALL garbled Chinese path variants in start.bat and bump to v2.69."""
from pathlib import Path
import re

bat_path = Path(r"D:\西客松\start.bat")
data = bat_path.read_bytes()

# Decode as UTF-8
text = data.decode("utf-8", errors="replace")

# Find all garbled sequences that look like corrupted 西客松
# Common variants:
#   瑗垮鏉綷 = UTF-8 bytes of 西客松 decoded as GBK then re-encoded
#   čĽżĺŽ˘ć = another mojibake variant
# Strategy: replace any non-ASCII sequence between "D:\" and "\backend" or end of path

# First, replace all known garbled variants with correct Chinese
garbled_patterns = [
    "瑗垮鏉綷",
    "čĽżĺŽ˘ć\u009d",  # may have control char
    "čĽżĺŽ˘ć",
]

# More robust: find D:\ followed by non-ASCII chars and replace with D:\西客松\
# Pattern: D:\[non-ascii chars] -> D:\西客松\
def fix_path(m):
    return "D:\\西客松\\"

# Replace D:\<garbled>\backend -> D:\西客松\backend
text_new = re.sub(r'D:\\[^\x00-\x7f]+\\backend', r'D:\\西客松\\backend', text)
# Replace D:\<garbled>\scripts -> D:\西客松\scripts  
text_new = re.sub(r'D:\\[^\x00-\x7f]+\\scripts', r'D:\\西客松\\scripts', text_new)
# Replace cd /d "D:\<garbled>" -> cd /d "D:\西客松"
text_new = re.sub(r'cd /d "D:\\[^\x00-\x7f]+"', r'cd /d "D:\\西客松"', text_new)
# Replace D:\<garbled>\backend\venv -> D:\西客松\backend\venv (already covered above)
# Replace "D:\<garbled>\" patterns in strings
text_new = re.sub(r'D:\\[^\x00-\x7f]+\\', r'D:\\西客松\\', text_new)
# Replace remaining D:\<garbled> at end of line
text_new = re.sub(r'D:\\[^\x00-\x7f]+\b', r'D:\\西客松', text_new)

# Count changes
changes = 0
for i, (a, b) in enumerate(zip(text.split('\n'), text_new.split('\n'))):
    if a != b:
        changes += 1
        print(f"  line {i+1} changed")
print(f"Total lines changed: {changes}")

text = text_new

# Bump version v2.68 -> v2.69 (should already be done, but ensure)
if "v2.68" in text:
    text = text.replace("v2.68", "v2.69")
    print("  version v2.68 -> v2.69 bumped")

# Normalize line endings to CRLF
text = text.replace("\r\n", "\n").replace("\n", "\r\n")

# Write as UTF-8 without BOM
bat_path.write_bytes(text.encode("utf-8"))

# Verify
verify = bat_path.read_bytes().decode("utf-8")
# Check no garbled non-ASCII between D:\ and \backend
garbled_remaining = re.findall(r'D:\\[^\x00-\x7f]+', verify)
if garbled_remaining:
    print(f"WARNING: garbled paths still remaining: {garbled_remaining[:5]}")
else:
    print("OK: no garbled paths remaining")

# Check correct path present
if "西客松" in verify:
    print("OK: correct Chinese path present")
else:
    print("WARNING: correct Chinese path not found")

if "v2.69" in verify:
    print("OK: version v2.69 present")
else:
    print("WARNING: version v2.69 not found")

print(f"Written {len(text)} chars to {bat_path}")