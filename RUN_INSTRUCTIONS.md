# FlowForge AI - 运行说明

> 啥都队 | XiHack 2026 | 软件赛道 - AI Agent / Workflow | 版本 v1.50

---

## 一、环境要求

| 依赖 | 最低版本 | 检查命令 | 用途 |
|------|----------|----------|------|
| Python | 3.11 | `python --version` | 后端运行时（必需） |
| Node.js | 18+ | `node --version` | 前端构建（可选，已预构建） |
| 操作系统 | Windows 10 / 11 | - | 一键脚本运行环境 |

> 前端已预构建并内置于 `backend/static/`，仅当需要重新构建前端时才需 Node.js。

---

## 二、小 Demo 启动方式（路演 Demo）

**最简启动**：解压后双击 `start_roadshow.bat`。

`start_roadshow.bat` 会自动完成：
1. 进入 `demo_roadshow/` 目录
2. 检测并创建 Python 虚拟环境（`.venv/`）
3. 安装依赖（`requirements.txt`）
4. 启动后端服务（API + Web 一体）
5. 自动打开浏览器

启动后访问：**http://127.0.0.1:8081**

| 端口 | 用途 |
|------|------|
| 8081 | 小 Demo（路演）服务端口 |

---

## 三、完整平台启动方式

### 方式一：一键启动（推荐）

```bat
start.bat
```

`start.bat` 完全自包含，自动完成：
1. 环境检测：检查 Python 3.11+ 和 Node.js 18+（可选）
2. 创建虚拟环境：`backend/venv/`（若不存在）
3. 安装依赖：`pip install -r requirements.txt`（若未安装）
4. 生成配置：从 `.env.example` 创建 `.env`（若不存在）
5. 构建前端：构建并拷贝到 `backend/static/`（需 Node.js，若静态文件缺失）
6. 启动服务：在端口 8080 启动后端，崩溃自动重启
7. 打开浏览器：3 秒后自动打开 http://localhost:8080

无需任何手动配置，双击即可。

### 方式二：手动安装

#### 步骤 1：后端配置

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
```

#### 步骤 2：启动服务

```bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### 步骤 3：访问应用

打开 **http://localhost:8080**。

| 端口 | 用途 |
|------|------|
| 8080 | 完整平台后端服务端口 |
| 8081 | 小 Demo（路演）服务端口 |

---

## 四、访问端点

| 端点 | URL | 说明 |
|------|-----|------|
| Web UI | http://localhost:8080 | FlowForge AI 主界面 |
| API 文档 | http://localhost:8080/api/v1/docs | 交互式 Swagger 文档 |
| ReDoc | http://localhost:8080/api/v1/redoc | ReDoc 文档 |
| 健康检查 | http://localhost:8080/health | 服务健康状态 |
| 小 Demo | http://127.0.0.1:8081 | 路演小 Demo |

---

## 五、功能说明

- **可视化工作流构建**：拖拽式多智能体工作流设计
- **13 个智能体模板**：代码审查、测试生成、文档生成、安全扫描、重构等
- **15 个预设工作流**：常见研发场景开箱即用
- **NL2Workflow**：自然语言转工作流
- **五维评分**：正确性、完整性、时效性、创新性、稳定性
- **持续优化**：AI 驱动的迭代改进引擎
- **实时 SSE**：得分实时更新与瓶颈告警
- **模板市场**：工作流的发布与订阅
- **40 个 API 端点**：完整 REST API，附 OpenAPI 文档

---

## 六、配置说明

编辑 `backend/.env` 配置以下变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NVIDIA_BUILD_API_KEY` | （必填） | NVIDIA Build API 访问密钥 |
| `NVIDIA_BUILD_BASE_URL` | `https://integrate.api.nvidia.com/v1` | 模型端点基础 URL |
| `PORT` | `8080` | 服务绑定端口 |
| `AUTH_TOKEN` | `flowforge-demo-token` | Demo 认证令牌 |

> API Key 通过环境变量或 `.env` 注入，绝不写入仓库。

---

## 七、常见问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError` | 依赖未安装 | 重新运行 `start.bat` 或 `pip install -r requirements.txt` |
| 端口 8080 被占用 | 其他进程占用端口 | 停止占用进程或修改 `start.bat` 中端口 |
| `python` 未找到 | 未安装 Python | 从 https://python.org 安装 Python 3.11+ |
| `node` 未找到 | 未安装 Node.js | 从 https://nodejs.org 安装 Node.js 18+（可选，仅重建前端需要） |
| 虚拟环境创建失败 | Python 版本过低或权限不足 | 确保 Python 3.11+ 并以管理员运行 |
| 依赖安装失败 | 网络或 pip 问题 | 检查网络，尝试 `pip install --trusted-host pypi.org -r requirements.txt` |
| API 401 未授权 | 认证令牌不匹配 | 检查 `.env` 中 `AUTH_TOKEN` |
| API Key 未配置 | `.env` 缺少 `NVIDIA_BUILD_API_KEY` | 编辑 `backend/.env` 填入 API Key |
| 前端未加载 | `backend/static/index.html` 缺失 | 安装 Node.js 后运行 `start.bat`，或手动构建前端 |
| `start.bat` 无法运行 | 执行策略或编码问题 | 在命令提示符中运行 `cmd /c start.bat` |