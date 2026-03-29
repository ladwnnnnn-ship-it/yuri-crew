# 技术栈指南

本文档为所有 Agent 提供技术栈选型的参考标准。

---

## 前端技术栈（推荐）

### 选项 A：纯 HTML/CSS/JS（适合简单项目）
- 直接使用原生 HTML5 + CSS3 + Vanilla JavaScript
- 使用 Fetch API 调用后端接口
- 适合快速原型和简单页面

### 选项 B：React（适合中复杂度项目）
- React 18 + Vite 构建
- Axios 处理 HTTP 请求
- React Router 处理路由
- CSS Modules 或 Tailwind CSS 处理样式

### 选项 C：Vue 3（适合中复杂度项目）
- Vue 3 + Vite 构建
- Pinia 状态管理
- Vue Router
- Axios HTTP 客户端

---

## 后端技术栈（推荐）

### 选项 A：FastAPI（推荐首选）
- Python 3.11+
- FastAPI 框架
- SQLAlchemy 2.0 ORM
- SQLite（开发）/ PostgreSQL（生产）
- Pydantic v2 数据验证
- Uvicorn ASGI 服务器

### 选项 B：Django REST Framework
- Python 3.11+
- Django 4.2+
- Django REST Framework
- SQLite / PostgreSQL

---

## API 设计规范

### RESTful 接口规范
```
GET    /api/v1/{resource}          → 获取列表
POST   /api/v1/{resource}          → 创建资源
GET    /api/v1/{resource}/{id}     → 获取单个资源
PUT    /api/v1/{resource}/{id}     → 完整更新
PATCH  /api/v1/{resource}/{id}     → 部分更新
DELETE /api/v1/{resource}/{id}     → 删除资源
```

### 统一响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200
}
```

### 错误响应格式
```json
{
  "success": false,
  "error": "错误描述",
  "code": 400
}
```

---

## CORS 配置（FastAPI 示例）

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 项目结构规范

### 前端项目结构
```
frontend/
├── index.html
├── src/
│   ├── api/          # API 调用层
│   ├── components/   # 可复用组件
│   ├── pages/        # 页面组件
│   ├── styles/       # 样式文件
│   └── utils/        # 工具函数
└── package.json
```

### 后端项目结构（FastAPI）
```
backend/
├── main.py           # 应用入口
├── app/
│   ├── api/          # 路由和控制器
│   ├── models/       # 数据库模型
│   ├── schemas/      # Pydantic 模式
│   ├── services/     # 业务逻辑
│   └── database.py   # 数据库连接
├── requirements.txt
└── README.md
```

---

## 代码质量要求

1. **注释**：所有函数和类必须有文档字符串
2. **错误处理**：所有 API 端点必须有 try-except 处理
3. **类型注解**：Python 代码使用类型注解
4. **命名规范**：
   - Python：snake_case
   - JavaScript：camelCase
   - 组件名：PascalCase
5. **测试**：核心业务逻辑必须有对应的单元测试
