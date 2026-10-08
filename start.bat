@echo off
chcp 65001 >nul 2>&1
title FlowForge AI - Hankesong S1 [Shadu Team] v2.69
setlocal enabledelayedexpansion

REM ==========================================
REM   FlowForge AI - One-Click Launcher v2.69
REM   Team: Shadu Team | Hankesong S1 & ETH Wuhan 2026
REM   v2.69 Edition: StartAccel + WheelCache + ParallelLaunch + VersionBump
REM     M34-M40: All previous features
REM     + StartBatV14Config: BOM + ASCII REM
REM     + StartBatAccelerator: wheel cache
REM     + StepTimer: millisecond timing
REM     + ParallelLauncher: async browser
REM ==========================================

cd /d "%~dp0"

REM --- Global variable init ---
set LOG_FILE=%~dp0start_log.txt
set AUDIT_FILE=%~dp0start_audit.txt
set GUARD_PY=%~dp0scripts\start_guard.py
set BACKEND_DIR=%~dp0backend
REM TASK-201: CrossDirAdapter - fallback to known project root if backend or requirements.txt not found
set CDA_NEED_FALLBACK=0
if not exist "%BACKEND_DIR%\requirements.txt" set CDA_NEED_FALLBACK=1
if not exist "%BACKEND_DIR%\app\main.py" set CDA_NEED_FALLBACK=1
if !CDA_NEED_FALLBACK! EQU 1 (
    if exist "D:\西客松\backend\requirements.txt" (
        if exist "D:\西客松\backend\app\main.py" (
            set BACKEND_DIR=D:\西客松\backend
            set GUARD_PY=D:\西客松\scripts\start_guard.py
            cd /d "D:\西客松"
            call :log "CDA: local backend incomplete, using D:\西客松\backend"
            echo [CDA] Local backend incomplete, switching to D:\西客松\backend
        )
    )
)
REM TASK-503: VenvReuseAdapter - if D:\西客松\backend\venv\.installed exists, reuse it to skip pip install
if not exist "%BACKEND_DIR%\venv\.installed" (
    if exist "D:\西客松\backend\venv\.installed" (
        if exist "D:\西客松\backend\venv\Scripts\python.exe" (
            set BACKEND_DIR=D:\西客松\backend
            set GUARD_PY=D:\西客松\scripts\start_guard.py
            cd /d "D:\西客松"
            call :log "VRA: reusing D:\西客松\backend\venv (skip venv create + pip install)"
            echo [VRA] Reusing ready venv at D:\西客松\backend - skip pip install
        )
    )
)
set VENV_PY=%BACKEND_DIR%\venv\Scripts\python.exe
set REQ_FILE=%BACKEND_DIR%\requirements.txt
set ENV_FILE=%BACKEND_DIR%\.env
set ENV_EXAMPLE=%~dp0.env.example
set WHEEL_CACHE=%BACKEND_DIR%\wheel_cache
set HF_CACHE=%LOCALAPPDATA%\..\..\HuggingFaceCache
if not exist "%HF_CACHE%" set HF_CACHE=D:\HuggingFaceCache
set HF_WHEELS=%HF_CACHE%
set PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple
set PORT_PRIMARY=8080
set PORT_FALLBACK_1=8090
set PORT_FALLBACK_2=8091
set USE_PORT=%PORT_PRIMARY%
set RESTART_COUNT=0
set MAX_FAST_RESTART=5
set MAX_TOTAL_RESTART=20
set IS_ADMIN=0

REM --- Step timer init ---
set T0=%time%

REM --- Init log ---
echo. > "%LOG_FILE%"

call :log "=========================================="
call :log "  FlowForge AI Launcher v2.69 - %date% %time%"
call :log "  v2.69 Edition - Hankesong S1 + ETH Wuhan 2026"
call :log "=========================================="

echo.
echo ==========================================
echo   FlowForge AI - One-Click Launcher v2.69
echo   Team: Shadu Team ^| Hankesong S1 2026
echo   v2.69 Edition
echo ==========================================
echo.

REM ==========================================
REM TASK-099: FastStart Cache - skip slow checks
REM ==========================================
set FAST_CACHE=%BACKEND_DIR%\.start_fast_cache
set FAST_MODE=0
if exist "%FAST_CACHE%" if exist "%VENV_PY%" (
    set FAST_MODE=1
    call :log "FastStart: cache found, skipping slow checks"
    echo [FAST] Cache found - fast startup mode
)

if !FAST_MODE! EQU 1 (
    REM Quick port check only
    call :check_port_occupied %USE_PORT%
    if "!OCCUPIED_PIDS!" NEQ "" (
        call :log "FastStart: port occupied, fallback to full check"
        set FAST_MODE=0
    )
)

if !FAST_MODE! EQU 1 (
    REM Skip to server start directly
    call :log "FastStart: jumping to server start"
    echo [FAST] Skipping health checks ^(cached^)
    echo [FAST] Starting server directly...
    goto :fast_server_start
)

REM --- Encoding self-check ---
call :encoding_self_check

REM ==========================================
REM TASK-163: VersionAdapter cross-version adapt
REM ==========================================
call :log "[VA] VersionAdapter detecting Windows version..."
echo [VA] Detecting Windows version...

set WIN_VER=unknown
set HAS_PS=no
for /f "tokens=*" %%v in ('ver 2^>nul') do set WIN_VER=%%v
if defined PSModulePath set HAS_PS=yes

REM Detect timeout availability
set DELAY_CMD=timeout
timeout /t 1 /nobreak >nul 2>&1
if errorlevel 1 set DELAY_CMD=ping

call :log "VA: WIN_VER=%WIN_VER% HAS_PS=%HAS_PS% DELAY=%DELAY_CMD%"
echo   Windows: %WIN_VER%
echo   PowerShell: %HAS_PS% ^| Delay: %DELAY_CMD%

REM ==========================================
REM TASK-164: PermissionAdapter privilege adapt
REM ==========================================
call :log "[PA] PermissionAdapter detecting privilege..."
echo [PA] Detecting privilege level...

net session >nul 2>&1
if not errorlevel 1 (
    set IS_ADMIN=1
    call :log "PA: ADMIN privilege"
    echo   Privilege: ADMIN
) else (
    set IS_ADMIN=0
    call :log "PA: NON_ADMIN privilege - no UAC prompt"
    echo   Privilege: NON-ADMIN ^| no UAC prompt
)

REM ==========================================
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
REM TASK-159: IdempotencyGuard
REM ==========================================
call :log "[IG] IdempotencyGuard checking service running..."
echo [IG] Checking if service already running...

call :check_port_occupied %USE_PORT%
if "!OCCUPIED_PIDS!" NEQ "" (
    set IS_OUR_SERVICE=0
    for %%p in (!OCCUPIED_PIDS!) do (
        call :identify_process %%p
        if /i "!PROC_TYPE!"=="IS_ORPHAN" set IS_OUR_SERVICE=1
    )
    if !IS_OUR_SERVICE! EQU 1 (
        echo.
        echo ==========================================
        echo   Service already running at http://localhost:!USE_PORT!
        echo   IdempotencyGuard: no duplicate start.
        echo ==========================================
        echo.
        call :log "IG: service already running on port !USE_PORT! - idempotent exit"
        call :audit_guard "IDEMPOTENT_EXIT:service_running_on_!USE_PORT!"
        goto :eof
    )
)

call :audit_guard "IDEMPOTENCY_CHECK:port_!USE_PORT!_free"
call :log "IG: port !USE_PORT! free - proceed"

REM ==========================================
REM TASK-160: OrphanProcessCleaner
REM ==========================================
call :log "[OPC] OrphanProcessCleaner scanning..."
echo [OPC] Scanning orphan processes on port !USE_PORT!...

call :clean_orphan_on_port %USE_PORT%
if !ORPHAN_KILLED! GTR 0 (
    echo   Orphan processes terminated: !ORPHAN_KILLED!
    call :log "OPC: terminated !ORPHAN_KILLED! orphan(s) on !USE_PORT!"
    call :audit_guard "ORPHAN_CLEAN:!ORPHAN_KILLED!_on_!USE_PORT!"
) else (
    echo   No orphan process on port !USE_PORT!.
    call :log "OPC: no orphan on !USE_PORT!"
)

REM If primary port occupied by non-service, fallback
call :check_port_occupied %USE_PORT%
if "!OCCUPIED_PIDS!" NEQ "" (
    call :log "OPC: port !USE_PORT! still occupied by non-service - fallback"
    echo   Port !USE_PORT! occupied by non-service ^| fallback...
    set USE_PORT=%PORT_FALLBACK_1%
    call :check_port_occupied !USE_PORT!
    if "!OCCUPIED_PIDS!" NEQ "" (
        set USE_PORT=%PORT_FALLBACK_2%
        call :check_port_occupied !USE_PORT!
        if "!OCCUPIED_PIDS!" NEQ "" (
            echo.
            echo [ERROR] All ports %PORT_PRIMARY%/%PORT_FALLBACK_1%/%PORT_FALLBACK_2% occupied.
            call :log "ERROR: all ports occupied"
            goto :fail
        )
    )
    echo   Using fallback port: !USE_PORT!
    call :log "OPC: fallback to port !USE_PORT!"
)

REM ==========================================
REM Step 0: Find Python
REM ==========================================
call :log "[0/7] Detecting Python..."
echo [0/7] Detecting Python...

set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python
if not defined PYTHON_CMD where py >nul 2>&1 && set PYTHON_CMD=py -3
if not defined PYTHON_CMD where python3 >nul 2>&1 && set PYTHON_CMD=python3

if not defined PYTHON_CMD (
    echo.
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    call :log "ERROR: Python not found"
    goto :fail
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VER=%%v
echo   Python: %PYTHON_VER%
call :log "Python: %PYTHON_VER%"

REM ==========================================
REM TASK-014: ParallelEnvProbe - parallel env detection
REM v1.50 historical note: parallel env probe + static audit (superseded by v2.69 fast path)
REM ==========================================
set SKIP_DIAG=0
if exist "%VENV_PY%" if exist "%BACKEND_DIR%\venv\.installed" set SKIP_DIAG=1

if !SKIP_DIAG! EQU 1 (
    call :log "[PEP] skipped (venv healthy + deps installed)"
    echo [PEP] Skipped ^(venv healthy^) - fast path
) else (
    call :log "[PEP] ParallelEnvProbe starting..."
    echo [PEP] Parallel environment probe ^(Python/venv/port/HF cache^)...
    if exist "%~dp0scripts\bat_helpers\parallel_env_probe.py" (
        "%PYTHON_CMD%" "%~dp0scripts\bat_helpers\parallel_env_probe.py" "%BACKEND_DIR%" %USE_PORT%
        if errorlevel 1 (
            call :log "[PEP] some probe failed"
            echo   [PEP] Some probe failed - continuing
        ) else (
            call :log "[PEP] all probes OK"
            echo   [PEP] All probes OK
        )
    ) else (
        call :log "[PEP] probe script missing, skip"
        echo   [PEP] Probe script missing, skip
    )
)

REM --- Static audit: goto labels + python -c + ASCII REM ---
REM v1.50 historical note: parallel env probe + static audit (superseded by v2.69 fast path)
if !SKIP_DIAG! EQU 1 (
    call :log "static audit: skipped (venv healthy)"
) else (
    if exist "%~dp0scripts\bat_helpers\bat_subroutine_auditor.py" (
        "%PYTHON_CMD%" "%~dp0scripts\bat_helpers\bat_subroutine_auditor.py" "%~dp0start.bat" >nul 2>&1
        if errorlevel 1 (
            echo [WARN] bat subroutine audit: goto label issue detected
            call :log "WARN: bat_subroutine_auditor reported label issue"
        ) else (
            call :log "bat_subroutine_auditor: labels OK"
        )
    ) else (
        call :log "bat_subroutine_auditor: script missing, skip audit"
    )
    REM TASK-013: python -c inline audit via independent script (no findstr false positive)
    if exist "%~dp0scripts\bat_helpers\python_c_auditor.py" (
        "%PYTHON_CMD%" "%~dp0scripts\bat_helpers\python_c_auditor.py" "%~dp0start.bat" >nul 2>&1
        if errorlevel 1 (
            echo [WARN] python -c inline detected in start.bat
            call :log "WARN: python_c_audit: hits detected"
        ) else (
            call :log "python_c_audit: 0 hits"
        )
    ) else (
        call :log "python_c_auditor: script missing, skip audit"
    )
)

REM --- Step 1: Backend dir ---
call :log "[1/7] Setting up backend directory..."
echo [1/7] Setting up backend directory...
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Cannot find backend directory at %BACKEND_DIR%
    call :log "ERROR: backend dir missing"
    goto :fail
)
cd /d "%BACKEND_DIR%"
echo   Backend: %CD%
call :log "Backend: %CD%"

REM ==========================================
REM TASK-161: AutoHealer
REM ==========================================
call :log "[AH] AutoHealer checking venv/dependencies/.env..."
echo [AH] AutoHealer health check...

REM --- Step 2: venv create/self-heal (skip if healthy) ---
set VENV_NEED_CREATE=0
if not exist "%VENV_PY%" (
    set VENV_NEED_CREATE=1
) else if exist "%GUARD_PY%" (
    "%VENV_PY%" "%GUARD_PY%" venv_health "%VENV_PY%" >nul 2>&1
    if errorlevel 1 set VENV_NEED_CREATE=1
) else (
    "%VENV_PY%" --version >nul 2>&1
    if errorlevel 1 set VENV_NEED_CREATE=1
)
if !VENV_NEED_CREATE! EQU 1 (
    if exist "%BACKEND_DIR%\venv" (
        call :log "AH: venv corrupted - auto-rebuild"
        echo   venv corrupted, auto-rebuilding...
        rmdir /s /q "%BACKEND_DIR%\venv" 2>nul
        call :audit_guard "AUTOHEAL:venv_rebuilt"
    )
    call :log "[2/7] Creating virtual environment..."
    echo [2/7] Creating Python virtual environment...
    if !IS_ADMIN! EQU 0 (
        %PYTHON_CMD% -m venv "%BACKEND_DIR%\venv"
        set VENV_RC=!errorlevel!
    ) else (
        %PYTHON_CMD% -m venv "%BACKEND_DIR%\venv"
        set VENV_RC=!errorlevel!
    )
    if !VENV_RC! NEQ 0 (
        call :log "AH: venv create failed (rc=!VENV_RC!) - retry plain"
        %PYTHON_CMD% -m venv "%BACKEND_DIR%\venv"
        set VENV_RC=!errorlevel!
        if !VENV_RC! NEQ 0 (
            echo [ERROR] Failed to create virtual environment ^(rc=!VENV_RC!^).
            call :log "ERROR: venv creation failed rc=!VENV_RC!"
            goto :fail
        )
    )
    echo   Virtual environment created.
    call :log "venv created"
) else (
    echo [2/7] Virtual environment healthy. ^(skip create^)
    call :log "venv healthy - skip create"
)

REM --- Step 3: Dep install (wheel cache first, then online) ---

set NEED_INSTALL=0
if not exist "%BACKEND_DIR%\venv\.installed" (
    REM TASK-502: FastDepCheck - direct import test before pip install
    "%VENV_PY%" -c "import fastapi,uvicorn,pydantic;print('OK')" >nul 2>&1
    if not errorlevel 1 (
        echo   Dependencies already importable ^(fast check - skip pip install^)
        call :log "deps importable (fast check) - skip install"
        echo. > "%BACKEND_DIR%\venv\.installed"
        goto :dep_done
    )
    REM TASK-492: Check if deps already importable before pip install
    if exist "%GUARD_PY%" (
        "%VENV_PY%" "%GUARD_PY%" deps "%VENV_PY%" >nul 2>&1
        if not errorlevel 1 (
            echo   Dependencies already installed ^(skip pip install^)
            call :log "deps importable - skip install, creating marker"
            echo. > "%BACKEND_DIR%\venv\.installed"
            for /f "tokens=*" %%h in ('"%VENV_PY%" "%GUARD_PY%" hash "%REQ_FILE%" 2^>nul') do echo %%h> "%BACKEND_DIR%\venv\.req_hash"
        ) else (
            set NEED_INSTALL=1
        )
    ) else (
        set NEED_INSTALL=1
    )
) else (
    set STORED_HASH=
    if exist "%BACKEND_DIR%\venv\.req_hash" (
        set /p STORED_HASH=<"%BACKEND_DIR%\venv\.req_hash"
    )
    set CURRENT_HASH=
    if exist "%GUARD_PY%" (
        for /f "tokens=*" %%h in ('"%VENV_PY%" "%GUARD_PY%" hash "%REQ_FILE%" 2^>nul') do set CURRENT_HASH=%%h
    )
    if "!STORED_HASH!" NEQ "!CURRENT_HASH!" (
        set NEED_INSTALL=1
        call :log "AH: requirements hash changed - reinstall"
        echo   requirements.txt changed ^| reinstalling...
    )
)


if !NEED_INSTALL! EQU 1 (
    call :log "[3/7] Installing dependencies..."
    echo [3/7] Installing dependencies...
    REM Try wheel cache first (offline, fast) - include HF cache wheels
    if exist "%WHEEL_CACHE%\*.whl" (
        call :log "Trying wheel cache offline install (backend+HF)..."
        echo   Trying local wheel cache ^(offline^)...
        "%VENV_PY%" -m pip install --no-index --find-links "%WHEEL_CACHE%" --find-links "%HF_WHEELS%" -r requirements.txt -q 2>nul
        if not errorlevel 1 (
            echo   Wheel cache install OK.
            call :log "wheel cache install OK"
            goto :dep_done
        )
        call :log "Wheel cache miss, falling back to online"
        echo   Wheel cache incomplete, falling back to online...
    ) else (
        REM Try HF cache wheels even if backend wheel_cache empty
        if exist "%HF_WHEELS%\*.whl" (
            call :log "Trying HF cache wheels..."
            echo   Trying HuggingFace cache wheels...
            "%VENV_PY%" -m pip install --no-index --find-links "%HF_WHEELS%" -r requirements.txt -q 2>nul
            if not errorlevel 1 (
                echo   HF cache wheel install OK.
                call :log "HF wheel install OK"
                goto :dep_done
            )
            call :log "HF cache incomplete, falling back to online"
            echo   HF cache incomplete, falling back to online...
        )
    )
    set PIP_DISABLE_PIP_VERSION_CHECK=1
    set PIP_NO_INPUT=1
    "%VENV_PY%" -m pip install --upgrade pip --timeout 15 --retries 1 -q 2>nul
    REM Mixed mode: find-links first, mirror fallback (only for existing dirs)
    REM Acceleration: --prefer-binary + --no-compile + --progress-bar off
    if not exist "%WHEEL_CACHE%" mkdir "%WHEEL_CACHE%" 2>nul
    set FIND_LINKS=
    if exist "%WHEEL_CACHE%\*.whl" set FIND_LINKS=--find-links "%WHEEL_CACHE%"
    if exist "%HF_WHEELS%\*.whl" set FIND_LINKS=!FIND_LINKS! --find-links "%HF_WHEELS%"
    "%VENV_PY%" -m pip install !FIND_LINKS! -r requirements.txt --prefer-binary --no-compile --progress-bar off --timeout 15 --retries 1 -q -i "%PIP_MIRROR%"
    if errorlevel 1 (
        echo [WARN] pip install had issues, retrying with mirror only...
        "%VENV_PY%" -m pip install -r requirements.txt --prefer-binary -i "%PIP_MIRROR%" --timeout 15 --retries 1
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies.
            call :log "ERROR: pip install failed"
            goto :fail
        )
    )
:dep_done
    echo. > "%BACKEND_DIR%\venv\.installed"
    if exist "%GUARD_PY%" (
        for /f "tokens=*" %%h in ('"%VENV_PY%" "%GUARD_PY%" hash "%REQ_FILE%" 2^>nul') do echo %%h> "%BACKEND_DIR%\venv\.req_hash"
    )
    echo   Dependencies installed.
    call :log "deps installed"
    call :audit_guard "DEPS_INSTALLED:hash_updated"
) else (
    "%VENV_PY%" "%GUARD_PY%" deps "%VENV_PY%" >nul 2>&1
    if errorlevel 1 (
        call :log "AH: core deps missing - auto-reinstall"
        echo   Core dependencies missing, auto-reinstalling...
        "%VENV_PY%" -m pip install -r requirements.txt --timeout 30 --retries 2 -q
        if errorlevel 1 (
        "%VENV_PY%" -m pip install -r requirements.txt --timeout 30 --retries 2
        )
        echo. > "%BACKEND_DIR%\venv\.installed"
        call :audit_guard "AUTOHEAL:deps_reinstalled"
    )
    echo [3/7] Dependencies healthy. ^(skip install^)
    call :log "deps healthy - skip install"
)

REM --- Step 4: .env create/self-heal ---
set ENV_NEED_FIX=0
if not exist "%ENV_FILE%" (
    set ENV_NEED_FIX=1
) else (
    findstr /c:"NVIDIA_BUILD_API_KEY=" "%ENV_FILE%" >nul 2>&1
    if errorlevel 1 set ENV_NEED_FIX=1
)

if !ENV_NEED_FIX! EQU 1 (
    call :log "[4/7] Creating/repairing .env..."
    echo [4/7] Creating/repairing .env configuration...
    if exist "%ENV_EXAMPLE%" (
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul 2>&1
    ) else if exist "%BACKEND_DIR%\.env.example" (
        copy "%BACKEND_DIR%\.env.example" "%ENV_FILE%" >nul 2>&1
    ) else (
        echo NVIDIA_BUILD_API_KEY=your_api_key_here> "%ENV_FILE%"
    )
    findstr /c:"NVIDIA_BUILD_API_KEY=" "%ENV_FILE%" >nul 2>&1
    if errorlevel 1 (
        echo NVIDIA_BUILD_API_KEY=your_api_key_here>> "%ENV_FILE%"
    )
    echo   .env ready.
    call :log ".env ready"
    call :audit_guard "ENV_REPAIRED"
) else (
    echo [4/7] .env healthy.
    call :log ".env healthy"
)

REM --- Step 5: Check frontend (skip if static exists) ---
if not exist "%BACKEND_DIR%\static\index.html" (
    call :log "[5/7] Frontend static not found, checking Node.js..."
    where node >nul 2>&1
    if errorlevel 1 (
        echo [5/7] WARNING: Node.js not found. Backend API works, Web UI limited.
        if not exist "%BACKEND_DIR%\static" mkdir "%BACKEND_DIR%\static"
        call :log "Node.js not found"
    ) else (
        echo [5/7] Building frontend...
        cd /d "%~dp0frontend"
        if not exist "node_modules" (
            echo   Installing frontend dependencies...
            call npm install -q
        )
        call npm run build
        if errorlevel 1 (
            echo [WARN] Frontend build failed. Backend API still works.
            call :log "frontend build failed"
        ) else (
            cd /d "%BACKEND_DIR%"
            if not exist "%BACKEND_DIR%\static" mkdir "%BACKEND_DIR%\static"
            xcopy "%~dp0frontend\dist\*" "%BACKEND_DIR%\static\" /E /Y /Q >nul 2>&1
            echo   Frontend build completed.
            call :log "frontend built"
        )
        cd /d "%BACKEND_DIR%"
    )
) else (
    echo [5/7] Frontend static files present. ^(skip build^)
    call :log "frontend static present - skip build"
)

REM --- Step 6: Pre-flight app import check ---
call :log "[6/7] Pre-flight app import check..."
echo [6/7] Pre-flight app import check...
"%VENV_PY%" "%GUARD_PY%" app_import "%VENV_PY%" "%BACKEND_DIR%" >nul 2>&1
if errorlevel 1 (
    call :log "AH: app import failed - output stack + retry"
    echo   App import failed. Full error stack:
    echo ----------------------------------------
    "%VENV_PY%" "%GUARD_PY%" app_import "%VENV_PY%" "%BACKEND_DIR%" 2>&1
    echo ----------------------------------------
    echo   AutoHealer: retrying after dependency reinstall...
    "%VENV_PY%" -m pip install -r requirements.txt -q 2>nul
    "%VENV_PY%" "%GUARD_PY%" app_import "%VENV_PY%" "%BACKEND_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Application import failed after auto-heal retry.
        call :log "ERROR: app import failed after retry"
        call :audit_guard "APP_IMPORT_FAIL:after_retry"
        goto :fail
    )
    call :audit_guard "AUTOHEAL:app_import_recovered"
)
echo   App import OK.
call :log "app import OK"

REM --- Step 7: HealthGuardian pre-launch state recovery ---
call :log "[7/7] HealthGuardian pre-launch state recovery..."
echo [7/7] HealthGuardian state recovery...
if exist "%GUARD_PY%" (
    for /f "tokens=*" %%r in ('"%VENV_PY%" "%GUARD_PY%" recover "%BACKEND_DIR%" 2^>nul') do set RECOVER_RESULT=%%r
    if defined RECOVER_RESULT (
        echo   Recovery: !RECOVER_RESULT!
        call :log "HG recover: !RECOVER_RESULT!"
    ) else (
        echo   Recovery: NOOP
        call :log "HG recover: NOOP"
    )
) else (
    echo   Recovery: skipped ^(guard script missing^)
    call :log "HG recover: skipped"
)

REM ==========================================
REM Start server with HealthGuardian (parallel)
REM ==========================================
:fast_server_start
cd /d "%BACKEND_DIR%"
if not exist "data" mkdir data

REM Create fast-start cache after successful checks (TASK-015: structured cache)
if !FAST_MODE! EQU 0 (
    echo. > "%FAST_CACHE%"
    if exist "%~dp0scripts\bat_helpers\faststart_cache.py" (
        "%VENV_PY%" "%~dp0scripts\bat_helpers\faststart_cache.py" create "%BACKEND_DIR%" "%REQ_FILE%" !USE_PORT! >nul 2>&1
    )
    call :log "FastStart: cache created for next startup"
)

call :log "Starting server on port !USE_PORT!..."
call :audit_guard "SERVER_START:port_!USE_PORT!"
echo.
echo ==========================================
echo   FlowForge AI is starting...
echo   Port: !USE_PORT!
echo ==========================================
echo.
echo   Web UI     : http://localhost:!USE_PORT!
echo   API Docs   : http://localhost:!USE_PORT!/api/v1/docs
echo   Health     : http://localhost:!USE_PORT!/health
echo.
echo   Press Ctrl+C to stop.
echo   Server auto-restarts on crash ^(5s, HealthGuardian^).
echo ==========================================
echo.

REM Open browser after server is ready (health check loop, max 30s)
REM TASK-fix: use BACKEND_DIR parent root instead of %~dp0 to support CDA fallback
for %%I in ("%BACKEND_DIR%") do set FF_ROOT=%%~dpI
if exist "%FF_ROOT%scripts\wait_for_server.py" (
    start "" /b "%VENV_PY%" "%FF_ROOT%scripts\wait_for_server.py" !USE_PORT!
) else if exist "%~dp0scripts\wait_for_server.py" (
    start "" /b "%VENV_PY%" "%~dp0scripts\wait_for_server.py" !USE_PORT!
)

REM ==========================================
REM TASK-162: HealthGuardian permanent run loop
REM ==========================================
:RESTART_LOOP
call :pre_restart_check
if !PRE_CHECK_RC! NEQ 0 goto :permanent_fail
call :log "HG: uvicorn start attempt #!RESTART_COUNT! on port !USE_PORT!..."
"%VENV_PY%" -m uvicorn app.main:app --host 0.0.0.0 --port !USE_PORT!
set EXIT_CODE=!errorlevel!
call :log "HG: uvicorn exited with code !EXIT_CODE!"

if !EXIT_CODE! EQU 0 (
    call :log "HG: server stopped normally"
    echo.
    echo Server stopped normally. Press any key to close.
    call :audit_guard "SERVER_STOP:normal"
    call :print_timing
    pause
    goto :eof
)

call :classify_fault
if /i "!FAULT_TYPE!"=="permanent" goto :permanent_fail
if /i "!FAULT_TYPE!"=="normal" goto :eof

call :port_race_fallback
if /i "!PORT_SWITCHED!"=="1" goto RESTART_LOOP

REM transient fault handling
set /a RESTART_COUNT+=1
call :audit_guard "CRASH_RESTART:count_!RESTART_COUNT!_exit_!EXIT_CODE!"

if !RESTART_COUNT! GTR !MAX_TOTAL_RESTART! (
    echo.
    echo [ERROR] Restart count exhausted ^(!RESTART_COUNT!/!MAX_TOTAL_RESTART!^).
    echo   Please check start_log.txt for details.
    call :log "ERROR: restart exhausted !RESTART_COUNT!/!MAX_TOTAL_RESTART!"
    call :audit_guard "RESTART_EXHAUSTED:count_!RESTART_COUNT!"
    goto :fail
)

REM State recovery before restart
call :log "HG: recovering state before restart..."
if exist "%VENV_PY%" if exist "%GUARD_PY%" (
    for /f "tokens=*" %%r in ('"%VENV_PY%" "%GUARD_PY%" recover "%BACKEND_DIR%" 2^>nul') do set RECOVER_RESULT=%%r
    if defined RECOVER_RESULT call :log "HG recover on restart: !RECOVER_RESULT!"
) else if not exist "%VENV_PY%" (
    call :log "HG: recover skipped (VENV_PY missing) -> permanent fault"
    set FAULT_TYPE=permanent
    set DIAG_MESSAGE=venv interpreter missing, re-run start.bat to self-heal
    goto :permanent_fail
)

if !RESTART_COUNT! GTR !MAX_FAST_RESTART! (
    echo.
    echo [WARN] Restart count !RESTART_COUNT! ^> !MAX_FAST_RESTART!.
    echo   Extending restart interval to 30s to prevent crash storm.
    echo   Last exit code: !EXIT_CODE!
    call :log "HG: ALARM restart_count=!RESTART_COUNT! > max - 30s interval"
    call :delay 30
) else (
    echo.
    echo [WARN] Server exited with code !EXIT_CODE!. Restarting in 5s...
    echo   Restart attempt: !RESTART_COUNT! / !MAX_FAST_RESTART! fast-restart budget
    call :log "HG: 5s restart - count=!RESTART_COUNT!"
    call :delay 5
)

goto RESTART_LOOP

REM ==========================================
REM Subroutine definitions
REM ==========================================

REM --- Encoding self-check ---
:encoding_self_check
REM Verify BOM via independent Python script (no certutil, no quote conflicts)
if not exist "%~dp0start.bat" goto :eof
if not exist "%~dp0scripts\bat_helpers\encoding_check.py" goto :eof
set ENC_PY=%PYTHON_CMD%
if not defined ENC_PY if exist "%VENV_PY%" set ENC_PY=%VENV_PY%
if not defined ENC_PY goto :eof
"%ENC_PY%" "%~dp0scripts\bat_helpers\encoding_check.py" "%~dp0start.bat" >nul 2>&1
if not errorlevel 1 (
    call :log "Encoding self-check: BOM OK"
) else (
    call :log "Encoding self-check: no BOM (OK for cmd.exe, pure ASCII)"
)
goto :eof

REM --- Print timing ---
:print_timing
echo.
echo ==========================================
echo   Startup Timing Summary
echo   Start: %T0%  End: %time%
echo ==========================================
echo.
call :log "Timing: start=%T0% end=%time%"
goto :eof

REM --- Log ---
:log
echo [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

REM --- Idempotent audit log ---
:audit_guard
if not exist "%GUARD_PY%" goto :eof
if not exist "%VENV_PY%" goto :eof
"%VENV_PY%" "%GUARD_PY%" audit "%AUDIT_FILE%" "%~1" >nul 2>&1
goto :eof

REM --- Classify fault type based on EXIT_CODE ---
:classify_fault
set FAULT_TYPE=transient
set DIAG_MESSAGE=unknown transient fault
if !EXIT_CODE! EQU 0 (
    set FAULT_TYPE=normal
    set DIAG_MESSAGE=server stopped normally
    goto :eof
)
if !EXIT_CODE! EQU 3 (
    set FAULT_TYPE=permanent
    set DIAG_MESSAGE=venv interpreter missing or path not found (exit=3)
    goto :eof
)
if !EXIT_CODE! EQU 9009 (
    set FAULT_TYPE=permanent
    set DIAG_MESSAGE=command not found (exit=9009), venv may be corrupted
    goto :eof
)
if not exist "%VENV_PY%" (
    set FAULT_TYPE=permanent
    set DIAG_MESSAGE=VENV_PY missing - venv interpreter deleted
    goto :eof
)
goto :eof

REM --- Permanent fault exit ---
:permanent_fail
echo.
echo ==========================================
echo [ERROR] Permanent fault: !FAULT_TYPE! ^(exit=!EXIT_CODE!^)
echo   !DIAG_MESSAGE!
echo   Suggestion: re-run start.bat to trigger self-heal, or check:
echo     - venv at: %BACKEND_DIR%\venv
echo     - log:     %LOG_FILE%
echo     - audit:   %AUDIT_FILE%
echo ==========================================
echo.
call :log "PERMANENT_FAULT: type=!FAULT_TYPE! exit=!EXIT_CODE! msg=!DIAG_MESSAGE!"
call :audit_guard "PERMANENT_FAULT:!FAULT_TYPE!_exit_!EXIT_CODE!"
call :print_timing
pause
goto :fail

REM --- Pre-restart check (venv_health + app_import) ---
:pre_restart_check
set PRE_CHECK_RC=0
if not exist "%VENV_PY%" (
    set PRE_CHECK_RC=1
    set FAULT_TYPE=permanent
    set DIAG_MESSAGE=VENV_PY missing before uvicorn start
    call :log "HG: pre_restart_check FAIL - VENV_PY missing"
    goto :eof
)
if exist "%GUARD_PY%" (
    "%VENV_PY%" "%GUARD_PY%" venv_health "%VENV_PY%" >nul 2>&1
    if errorlevel 1 (
        set PRE_CHECK_RC=1
        set FAULT_TYPE=permanent
        set DIAG_MESSAGE=venv_health check failed before restart
        call :log "HG: pre_restart_check FAIL - venv_health"
        goto :eof
    )
    cd /d "%BACKEND_DIR%"
    "%VENV_PY%" "%GUARD_PY%" app_import "%VENV_PY%" "%BACKEND_DIR%" >nul 2>&1
    if errorlevel 1 (
        set PRE_CHECK_RC=1
        set FAULT_TYPE=permanent
        set DIAG_MESSAGE=app_import check failed before restart
        call :log "HG: pre_restart_check FAIL - app_import"
        goto :eof
    )
)
call :log "HG: pre_restart_check OK"
goto :eof

REM --- Port race fallback (runtime port switch) ---
:port_race_fallback
set PORT_SWITCHED=0
if not exist "%BACKEND_DIR%\.uvicorn_stderr.tmp" goto :eof
findstr /i "Address already in use" "%BACKEND_DIR%\.uvicorn_stderr.tmp" >nul 2>&1
if errorlevel 1 (
    findstr /i "WinError 10048" "%BACKEND_DIR%\.uvicorn_stderr.tmp" >nul 2>&1
    if errorlevel 1 (
        findstr /i "bind" "%BACKEND_DIR%\.uvicorn_stderr.tmp" >nul 2>&1
        if errorlevel 1 goto :eof
    )
)
call :log "HG: port race detected on !USE_PORT!"
if !USE_PORT! EQU %PORT_PRIMARY% (
    set USE_PORT=%PORT_FALLBACK_1%
    set PORT_SWITCHED=1
    call :audit_guard "PORT_FALLBACK:race_%PORT_PRIMARY%_to_%PORT_FALLBACK_1%"
    call :log "HG: port race fallback to !USE_PORT!"
    goto :eof
)
if !USE_PORT! EQU %PORT_FALLBACK_1% (
    set USE_PORT=%PORT_FALLBACK_2%
    set PORT_SWITCHED=1
    call :audit_guard "PORT_FALLBACK:race_%PORT_FALLBACK_1%_to_%PORT_FALLBACK_2%"
    call :log "HG: port race fallback to !USE_PORT!"
    goto :eof
)
set FAULT_TYPE=permanent
set DIAG_MESSAGE=all candidate ports occupied (race)
call :log "HG: all ports race-exhausted"
goto :eof

REM --- Cross-version delay ---
:delay
if "!DELAY_CMD!"=="ping" (
    set /a _ping_n=%~1+1
    ping -n !_ping_n! 127.0.0.1 >nul 2>&1
) else (
    timeout /t %~1 /nobreak >nul 2>&1
)
goto :eof

REM --- Check port occupied, result in OCCUPIED_PIDS ---
:check_port_occupied
set OCCUPIED_PIDS=
set _port=%~1
if exist "%GUARD_PY%" (
    if exist "%VENV_PY%" (
        for /f "tokens=*" %%p in ('"%VENV_PY%" "%GUARD_PY%" port !_port! 2^>nul') do (
            if not "%%p"=="" (
                if defined OCCUPIED_PIDS (
                    set OCCUPIED_PIDS=!OCCUPIED_PIDS! %%p
                ) else (
                    set OCCUPIED_PIDS=%%p
                )
            )
        )
        goto :eof
    )
)
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":!_port! " ^| findstr "LISTENING"') do (
    if not "%%p"=="0" (
        if defined OCCUPIED_PIDS (
            set OCCUPIED_PIDS=!OCCUPIED_PIDS! %%p
        ) else (
            set OCCUPIED_PIDS=%%p
        )
    )
)
goto :eof

REM --- Identify process type, result in PROC_TYPE ---
:identify_process
set PROC_TYPE=UNKNOWN
set _pid=%~1
if exist "%GUARD_PY%" (
    if exist "%VENV_PY%" (
        for /f "tokens=*" %%t in ('"%VENV_PY%" "%GUARD_PY%" identify !_pid! 2^>nul') do (
            if not "%%t"=="" set PROC_TYPE=%%t
        )
        goto :eof
    )
)
for /f "tokens=*" %%c in ('wmic process where "ProcessId=!_pid!" get CommandLine 2^>nul ^| findstr /v "CommandLine"') do (
    echo %%c | findstr /i "uvicorn" >nul 2>&1
    if not errorlevel 1 (
        echo %%c | findstr /i "app.main" >nul 2>&1
        if not errorlevel 1 set PROC_TYPE=IS_ORPHAN
    )
)
goto :eof

REM --- Clean orphan on port, result in ORPHAN_KILLED ---
:clean_orphan_on_port
set ORPHAN_KILLED=0
set _cport=%~1
call :check_port_occupied !_cport!
if "!OCCUPIED_PIDS!"=="" goto :eof
for %%p in (!OCCUPIED_PIDS!) do (
    call :identify_process %%p
    if /i "!PROC_TYPE!"=="IS_ORPHAN" (
        taskkill /F /PID %%p >nul 2>&1
        if not errorlevel 1 (
            set /a ORPHAN_KILLED+=1
            call :log "OPC: orphan PID %%p on port !_cport! terminated"
            echo   Orphan PID %%p terminated.
        )
    )
)
goto :eof

REM ==========================================
REM Failure handling
REM ==========================================
:fail
if exist "%FAST_CACHE%" del "%FAST_CACHE%" >nul 2>&1
echo.
echo ==========================================
echo   Startup FAILED. See start_log.txt for details.
echo   Audit log: start_audit.txt
echo ==========================================
echo.
call :log "=== STARTUP FAILED ==="
call :audit_guard "STARTUP_FAIL"
pause
goto :eof

