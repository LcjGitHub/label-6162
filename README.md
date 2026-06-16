# 手写信封邮票组合收藏

Vue 3 + PrimeVue + Tailwind 前端，Flask + SQLite 后端。用于管理手写信封上的邮票与邮戳收藏信息。

## 技术栈

| 层级 | 技术 | 端口 |
|------|------|------|
| 前端 | Vue 3、PrimeVue、Tailwind CSS、Pinia、axios | **4101** |
| 后端 | Flask、SQLite（`backend/data/envelope.db`） | **4000** |

## 功能（MVP）

- 信封收藏 **DataTable** 列表（搜索、排序、分页）
- **详情 / 编辑 / 新建** 页面
- 字段：寄出地、目的地、年份、邮票描述、邮戳类型、品相
- 基础 CRUD，首次启动自动 **seed 5 条** 示例数据

## 目录结构

```
├── backend/          # Flask API
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   └── data/         # SQLite 数据库（运行时生成）
└── frontend/         # Vue 3 应用
    ├── src/
    └── package.json
```

## 启动方式

### 1. 后端（一条命令）

在项目根目录执行：

```bash
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && python app.py
```

> **macOS / Linux** 将激活命令改为：`source .venv/bin/activate`

后端启动后访问：<http://localhost:4000/api/envelopes>

### 2. 前端

**另开一个终端**，在项目根目录执行：

```bash
cd frontend && npm install && npm run dev
```

前端启动后访问：<http://localhost:4101>

## 依赖说明

- 后端依赖安装在 `backend/.venv` 虚拟环境内
- 前端依赖安装在 `frontend/node_modules` 内
- 无需全局安装 pnpm / yarn

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/envelopes` | 获取全部 |
| GET | `/api/envelopes/:id` | 获取单条 |
| POST | `/api/envelopes` | 新建 |
| PUT | `/api/envelopes/:id` | 更新 |
| DELETE | `/api/envelopes/:id` | 删除 |
