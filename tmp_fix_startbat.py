"""修复start.bat: 添加端口自动清理逻辑."""
path = r"D:\西客松\start.bat"
with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

old = "REM ==========================================\r\nREM TASK-159: IdempotencyGuard"
new = """REM ==========================================
REM TASK-200: AutoKillPort - kill stale process on port
REM ==========================================
call :log "[AKP] AutoKillPort checking port %USE_PORT%..."
call :check_port_occupied %USE_PORT%
if "!OCCUPIED_PIDS!" NEQ "" (
    for %%p in (!OCCUPIED_PIDS!) do (
        taskkill /f /pid %%p >nul 2>&1
        call :log "AKP: killed pid %%p on port %USE_PORT%"
    )
    timeout /t 2 /nobreak >nul
    call :log "AKP: port cleared"
)

REM ==========================================
REM TASK-159: IdempotencyGuard"""

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8", errors="replace") as f:
        f.write(content)
    print("start.bat修复成功: 添加了AutoKillPort逻辑")
else:
    print("未找到目标位置，尝试另一种方式")
    # 搜索包含IdempotencyGuard的行
    lines = content.split("\r\n")
    for i, line in enumerate(lines):
        if "TASK-159" in line and "IdempotencyGuard" in line:
            print(f"找到TASK-159在第{i+1}行: {line.strip()}")
            break