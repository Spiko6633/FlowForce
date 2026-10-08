# FlowForge AI - 啥都队

> **面向软件研发效能的多智能体工作流编排平台**
> 赛事：XiHack 2026 | 赛道：软件赛道 - AI Agent / Workflow | 队伍：啥都队
> 版本：v2.01

## 命题声明

| 字段 | 内容 |
|------|------|
| **赛道** | 软件赛道 - AI Agent / Workflow |
| **命题** | 面向软件研发效能的多智能体工作流编排平台 |
| **作品名** | FlowForge AI |
| **队伍名** | 啥都队 |
| **赛事** | XiHack 2026 |
| **核心功能** | 代码审查、测试生成、文档生成、安全扫描、自动协作 |
| **主题契合** | 开物成器 - 工作流市场使作品赛后持续生长 |

## 项目介绍

FlowForge AI 是一个可视化的多智能体工作流编排平台，让软件研发团队像搭积木一样组合可复用的 AI 智能体，自动完成代码审查、测试生成、文档撰写、缺陷诊断、安全扫描等全流水线工作，并以可执行的有向无环图（DAG）工作流形式运行。

平台围绕"编排 + 生成 + 评分"闭环设计：用户通过拖拽或自然语言描述生成工作流，调度引擎并行执行各智能体节点，五维评分体系实时度量产出质量并反馈优化，形成持续提升的研发飞轮。

## 功能特性

- **可视化 DAG 编排** — 拖拽式工作流构建器，实时环检测与契约校验
- **NL2Workflow** — 自然语言一句话生成完整工作流
- **多智能体执行引擎** — 拓扑并行调度，支持重试、超时、断点续跑
- **5 类研发智能体** — 代码审查、测试生成、文档生成、缺陷诊断、安全扫描
- **模板市场** — 智能体模板的发布、订阅、版本追踪与复用
- **五维评分看板** — 正确性、完整性、时效性、创新性、稳定性，SSE 实时推送、增量追踪、瓶颈定位
- **节点级归因** — 每个节点的执行轨迹、耗时、产出可追溯
- **跨设备自适应** — 前端响应式设计，适配桌面/平板/折叠屏

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3.5、TypeScript、Vue Flow、Naive UI、Tailwind CSS、Pinia、ECharts |
| 后端 | Python 3.11、FastAPI、SQLModel、asyncio、tree-sitter |
| 模型 | NVIDIA Build API（OpenAI 兼容）：Llama 3.1 / Mixtral / Qwen2.5 / DeepSeek-V3 |
| 存储 | SQLite（WAL 模式） |
| 实时 | Server-Sent Events（SSE） |

## 架构

```
前端 (Vue 3 + TypeScript + Vue Flow + Naive UI)
    ↕ REST + SSE
后端 (Python + FastAPI + asyncio DAG 调度器)
    ↕
模型 (NVIDIA Build API: Llama 3.1 / Mixtral / Qwen2.5 / DeepSeek-V3)
```

## 安装与运行

> 详细运行说明请见 [RUN_INSTRUCTIONS.md](./RUN_INSTRUCTIONS.md)

### 环境要求

| 依赖 | 最低版本 | 用途 |
|------|----------|------|
| Python | 3.11 | 后端运行时 |
| Node.js | 18+ | 前端构建（可选，已预构建） |

### 方式一：一键启动（推荐）

```bat
start.bat
```

`start.bat` 完全自包含，自动完成：环境检测 → 创建虚拟环境 → 安装依赖 → 生成配置 → 构建前端 → 启动服务 → 打开浏览器。

启动后访问 **http://localhost:8080**。

### 方式二：小 Demo 启动

解压后双击 `start_roadshow.bat`，即可启动路演小 Demo（端口 8081）。

### 方式三：手动安装

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env   # 编辑并填入 API Key
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 使用说明

1. 启动服务后，浏览器自动打开主界面
2. 在画布上拖拽智能体节点，连线构建工作流 DAG
3. 或在 NL2Workflow 输入框用自然语言描述需求，一键生成工作流
4. 点击"运行"执行工作流，实时查看各节点状态与产出
5. 在评分看板查看五维得分、瓶颈分析与优化建议
6. 可将工作流发布到模板市场供复用

### API 文档

- Swagger UI：`http://localhost:8080/api/v1/docs`
- ReDoc：`http://localhost:8080/api/v1/redoc`
- OpenAPI JSON：`http://localhost:8080/api/v1/openapi.json`

## 评分体系

| 维度 | 权重 | 说明 |
|------|------|------|
| 正确性 | 0.25 | 产出准确性与可执行性 |
| 完整性 | 0.20 | 场景覆盖度 |
| 时效性 | 0.20 | 执行延迟相对基线 |
| 创新性 | 0.15 | 工作流设计创意 |
| 稳定性 | 0.20 | 成功率与重试惩罚 |

## 配置说明

- **API Key**：在 `.env` 中设置 `NVIDIA_BUILD_API_KEY`（从不写入仓库）
- **评分权重**：通过 `PUT /api/v1/scores/weights` 热更新
- **模型分配**：`data/config.json#model_allocation`

## AI生成内容统计（v2.01）

- **511个真实AI NL2Workflow场景** — 通过claude/gpt-5.6-sol/deepseek三模型协作生成
- **308个真实AI文档章节** — 覆盖架构/安全/运维/合规/性能/UX等49+维度
- **44个内容版本** — v1.54至v1.99持续迭代，每轮3模型协作
- **累计API消耗** — ~47.5万tokens，真实AI生成非模板填充
- **内容索引** — 详见 `deliverables/CONTENT_INDEX.md`

## 许可证

MIT License — 本项目为 XiHack 2026 参赛作品。