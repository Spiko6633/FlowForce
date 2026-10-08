import os

# 检查start.bat是否有可能导致闪退的问题
with open(r'D:\西客松\start.bat', 'rb') as f:
    content = f.read()

null_count = content.count(b'\x00')
print(f'Null字节: {null_count}')

lines = content.decode('utf-8', errors='replace').splitlines()
print(f'总行数: {len(lines)}')

# 检查关键路径
venv_py = r'D:\西客松\backend\venv\Scripts\python.exe'
print(f'venv存在: {os.path.exists(venv_py)}')
backend_path = r'D:\西客松\backend'
req_path = r'D:\西客松\backend\requirements.txt'
print(f'backend存在: {os.path.exists(backend_path)}')
print(f'requirements存在: {os.path.exists(req_path)}')

installed = r'D:\西客松\backend\venv\.installed'
print(f'.installed存在: {os.path.exists(installed)}')

fast_cache = r'D:\西客松\backend\.start_fast_cache'
print(f'fast_cache存在: {os.path.exists(fast_cache)}')

# 检查start_guard.py
guard_py = r'D:\西客松\scripts\start_guard.py'
print(f'start_guard.py存在: {os.path.exists(guard_py)}')

# 检查bat_helpers
helpers_dir = r'D:\西客松\scripts\bat_helpers'
if os.path.exists(helpers_dir):
    helpers = os.listdir(helpers_dir)
    print(f'bat_helpers: {helpers}')
else:
    print(f'bat_helpers目录不存在')

# 检查static目录
static_dir = r'D:\西客松\backend\static\index.html'
print(f'static/index.html存在: {os.path.exists(static_dir)}')

# 检查端口8080是否被占用
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', 8080))
s.close()
print(f'端口8080占用: {result == 0}')

# 检查乱码行数量
garbled_count = 0
for i, line in enumerate(lines, 1):
    if '婵' in line or '鎴' in line or '閻' in line or '鍚' in line or '濞' in line:
        garbled_count += 1
print(f'乱码行数: {garbled_count}')