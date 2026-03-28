# 🤖 多 Agent 软件开发框架

基于 **CrewAI** 构建的全自动软件开发 Agent 团队，能够根据自然语言需求自动完成从需求分析到代码交付的完整开发闭环。

---

## 🏗️ 架构

```
用户输入需求
     ↓
[Manager Agent] —— 总指挥
     ├──→ [PM Agent]          → 需求分析 → 技术规格文档
     ├──→ [Frontend Agent]    → 前端代码开发
     ├──→ [Backend Agent]     → 后端代码开发
     ├──→ [Integration Agent] → 前后端接口联调
     └──→ [QA Agent]          → 需求验证与测试报告
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd yuri
pip install -e .
```

### 2. 配置环境变量

在项目根目录（`crewAI-main/`）确保 `.env` 文件存在并包含：

```env
# LLM API Key（必须）
OPENAI_API_KEY=your_openai_api_key

# CrewAI Cloud 监控（可选）
CREWAI_PERSONAL_ACCESS_TOKEN=your_token
CREWAI_TRACING_ENABLED=true
```

### 3. 运行框架

```bash
# 方式一：交互式输入需求
cd yuri
python -m yuri.main

# 方式二：命令行直接传入需求
python -m yuri.main "构建一个用户管理系统，支持注册、登录和个人信息编辑"

# 方式三：使用 crewai CLI
crewai run
```

### 4. 查看输出

执行完成后，在 `yuri/output/` 目录下查看：

| 文件 | 内容 |
|------|------|
| `01_tech_spec.md` | PM Agent 输出的技术规格文档 |
| `02_frontend_code.md` | Frontend Agent 生成的前端代码 |
| `03_backend_code.md` | Backend Agent 生成的后端代码 |
| `04_integration_report.md` | Integration Agent 联调报告 |
| `05_qa_report.md` | QA Agent 验证报告 |
| `crew_execution.log` | 完整执行日志 |

---

## 🤖 Agent 团队

| Agent | 角色 | 职责 |
|-------|------|------|
| **Manager Agent** | 项目经理 | 协调所有 Agent，确保任务按序执行 |
| **PM Agent** | 产品经理 | 需求分析，输出技术规格文档 |
| **Frontend Agent** | 前端工程师 | 生成前端代码（HTML/React/Vue） |
| **Backend Agent** | 后端工程师 | 生成后端代码（FastAPI） |
| **Integration Agent** | 全栈工程师 | 前后端接口联调和修复 |
| **QA Agent** | 测试工程师 | 需求验证和测试报告 |

---

## 📁 项目结构

```
yuri/
├── PRD.md                          # 产品需求文档
├── README.md                       # 本文件
├── pyproject.toml                  # 项目配置
├── src/
│   └── yuri/
│       ├── __init__.py
│       ├── crew.py                 # Crew 主定义
│       ├── main.py                 # 入口文件
│       ├── config/
│       │   ├── agents.yaml         # Agent 配置
│       │   └── tasks.yaml          # Task 配置
│       └── tools/
│           ├── __init__.py
│           └── file_tools.py       # 文件操作工具
├── knowledge/
│   └── tech_stack_guidelines.md   # 技术栈指南（Agent 知识库）
├── tests/
│   └── test_crew.py               # 单元测试
└── output/                         # 执行输出（自动生成）
    ├── 01_tech_spec.md
    ├── 02_frontend_code.md
    ├── 03_backend_code.md
    ├── 04_integration_report.md
    ├── 05_qa_report.md
    └── crew_execution.log
```

---

## 🧪 运行测试

```bash
cd yuri
pytest tests/ -v
```

---

## 🔍 监控

框架集成了 CrewAI Cloud 监控，配置 `CREWAI_PERSONAL_ACCESS_TOKEN` 后可在 [https://app.crewai.com](https://app.crewai.com) 查看：

- 每次执行的完整追踪记录
- 各 Agent 的输入/输出日志
- Token 消耗统计
- 执行时间分析

---

## 📝 使用示例

```bash
# 示例需求 1：TODO 应用
python -m yuri.main "构建一个 TODO 任务管理应用，支持创建、编辑、删除任务，并支持按状态筛选"

# 示例需求 2：用户系统
python -m yuri.main "构建一个用户注册登录系统，使用 JWT 认证，支持邮箱验证"

# 示例需求 3：博客系统
python -m yuri.main "构建一个简单的博客系统，支持文章发布、编辑、评论功能"
```
