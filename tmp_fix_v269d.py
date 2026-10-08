"""Rewrite the specific garbled lines in start.bat directly."""
from pathlib import Path

bat_path = Path(r"D:\西客松\start.bat")
text = bat_path.read_bytes().decode("utf-8")
lines = text.split("\r\n")

# Fix line 33 (index 32): cd /d "D:\西客松"  + call :log ...
# The line got mangled, restore it
for i in range(len(lines)):
    line = lines[i]
    # Fix cd /d lines that lost their closing quote
    if 'cd /d "D:\\西客松"' in line and line.count('"') < 4:
        # This line should be just: cd /d "D:\西客松"
        lines[i] = '            cd /d "D:\\西客松"'
        print(f"  fixed line {i+1}: {lines[i]}")
    # Fix lines where call :log got merged
    if 'cd /d "D:\\西客松"CDA:' in line:
        lines[i] = '            cd /d "D:\\西客松"'
        print(f"  fixed merged line {i+1}: {lines[i]}")
    if 'cd /d "D:\\西客松"VRA:' in line:
        lines[i] = '            cd /d "D:\\西客松"'
        print(f"  fixed merged line {i+1}: {lines[i]}")

# Check if call :log lines after cd are missing
# Line 33 should be cd, line 34 should be call :log
# Let's verify lines 33-35 and 45-47
for idx in [32, 33, 34, 44, 45, 46]:
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx]}")

text = "\r\n".join(lines)
bat_path.write_bytes(text.encode("utf-8"))
print("Done")