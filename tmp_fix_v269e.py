"""Rewrite the CDA/VRA fallback blocks in start.bat with correct content."""
from pathlib import Path

bat_path = Path(r"D:\西客松\start.bat")
text = bat_path.read_bytes().decode("utf-8")
lines = text.split("\r\n")

# Find and rewrite the CDA fallback block (lines 28-37) and VRA block (lines 38-48)
# We'll identify by markers and replace the block content

new_cda_block = [
    "if !CDA_NEED_FALLBACK! EQU 1 (",
    '    if exist "D:\\西客松\\backend\\requirements.txt" (',
    '        if exist "D:\\西客松\\backend\\app\\main.py" (',
    '            set BACKEND_DIR=D:\\西客松\\backend',
    '            set GUARD_PY=D:\\西客松\\scripts\\start_guard.py',
    '            cd /d "D:\\西客松"',
    '            call :log "CDA: local backend incomplete, using D:\\西客松\\backend"',
    '            echo [CDA] Local backend incomplete, switching to D:\\西客松\\backend',
    "        )",
    "    )",
    ")",
]

new_vra_header = 'REM TASK-503: VenvReuseAdapter - if D:\\西客松\\backend\\venv\\.installed exists, reuse it to skip pip install'
new_vra_block = [
    'if not exist "%BACKEND_DIR%\\venv\\.installed" (',
    '    if exist "D:\\西客松\\backend\\venv\\.installed" (',
    '        if exist "D:\\西客松\\backend\\venv\\Scripts\\python.exe" (',
    '            set BACKEND_DIR=D:\\西客松\\backend',
    '            set GUARD_PY=D:\\西客松\\scripts\\start_guard.py',
    '            cd /d "D:\\西客松"',
    '            call :log "VRA: reusing D:\\西客松\\backend\\venv (skip venv create + pip install)"',
    '            echo [VRA] Reusing ready venv at D:\\西客松\\backend - skip pip install',
    "        )",
    "    )",
    ")",
]

# Find the CDA block start (line with "if !CDA_NEED_FALLBACK! EQU 1 (")
cda_start = None
for i, line in enumerate(lines):
    if "CDA_NEED_FALLBACK" in line and "EQU 1" in line:
        cda_start = i
        break

if cda_start is None:
    print("ERROR: CDA block not found")
else:
    # Find the VRA header (REM TASK-503)
    vra_header_idx = None
    for i in range(cda_start, min(cda_start + 30, len(lines))):
        if "TASK-503" in lines[i] or "VenvReuseAdapter" in lines[i]:
            vra_header_idx = i
            break
    
    # Find the VRA block start (if not exist ... venv .installed)
    vra_start = None
    if vra_header_idx is not None:
        for i in range(vra_header_idx, min(vra_header_idx + 5, len(lines))):
            if "venv" in lines[i] and "not exist" in lines[i] and ".installed" in lines[i]:
                vra_start = i
                break
    
    print(f"CDA block starts at line {cda_start+1}")
    print(f"VRA header at line {vra_header_idx+1 if vra_header_idx else 'N/A'}")
    print(f"VRA block starts at line {vra_start+1 if vra_start else 'N/A'}")
    
    # Replace VRA block first (to preserve indices)
    if vra_start is not None and vra_header_idx is not None:
        # Find end of VRA block (matching closing paren)
        vra_end = vra_start
        depth = 0
        for i in range(vra_start, min(vra_start + 20, len(lines))):
            depth += lines[i].count("(") - lines[i].count(")")
            if depth <= 0 and i > vra_start:
                vra_end = i
                break
        # Replace from vra_header to vra_end
        new_vra_full = [new_vra_header] + new_vra_block
        lines[vra_header_idx:vra_end+1] = new_vra_full
        print(f"  Replaced VRA block lines {vra_header_idx+1}-{vra_end+1} with {len(new_vra_full)} lines")
    
    # Re-find CDA block end (indices may have shifted)
    cda_end = cda_start
    depth = 0
    for i in range(cda_start, min(cda_start + 20, len(lines))):
        depth += lines[i].count("(") - lines[i].count(")")
        if depth <= 0 and i > cda_start:
            cda_end = i
            break
    # Replace CDA block
    lines[cda_start:cda_end+1] = new_cda_block
    print(f"  Replaced CDA block lines {cda_start+1}-{cda_end+1} with {len(new_cda_block)} lines")

text = "\r\n".join(lines)
bat_path.write_bytes(text.encode("utf-8"))

# Verify
verify = bat_path.read_bytes().decode("utf-8")
import re
garbled = re.findall(r'D:\\[^\x00-\x7f]+', verify)
if garbled:
    print(f"WARNING: garbled remaining: {garbled[:5]}")
else:
    print("OK: no garbled paths")

# Show the fixed region
vlines = verify.split("\r\n")
for i in range(cda_start - 2, min(cda_start + 25, len(vlines))):
    print(f"{i+1}: {vlines[i]}")