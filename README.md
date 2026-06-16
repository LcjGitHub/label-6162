# 手写信封邮票组合收藏系统

第三代视图框架配合组件库与样式工具的前端，轻量网框架配合本地关系型数据库的后端。用于管理手写信封上的邮票与邮戳收藏信息。

## 技术栈

| 层级 | 技术 | 端口 |
|------|------|------|
| 前端 | 第三代视图框架、组件库、样式工具、集中式存储、通用请求库 | **4101** |
| 后端 | 轻量网框架、本地关系型数据库（`backend/data/envelope.db`） | **4000** |

## 核心功能

- 信封收藏数据表格列表（搜索、排序、分页）
- 详情、编辑、新建页面
- 字段：寄出地、目的地、年份、邮票描述、邮戳类型、品相
- 完整增删改查，首次启动自动写入 5 条示例数据

## 目录结构

```
├── backend/          # 后端代码
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   └── data/         # 数据库目录
└── frontend/         # 前端代码
    ├── src/
    └── package.json
```

## 启动方式

### 后端（一条命令启动）

在项目根目录执行：

```
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && python app.py
```

> 苹果系统 / Linux 系统将激活命令改为：`source .venv/bin/activate`

后端启动后访问：<http://localhost:4000/api/envelopes>

### 前端（一条命令开发启动）

另开一个终端，在项目根目录执行：

```
cd frontend && npm install && npm run dev
```

前端启动后访问：<http://localhost:4101>

## 依赖说明

- 后端依赖安装在 `backend/.venv` 虚拟环境内
- 前端依赖安装在 `frontend/node_modules` 内
- 无需全局安装其他包管理工具

## 接口说明

| 方法 | 路径 | 说明 |
|------|------|------|
| 获取 | `/api/envelopes` | 获取全部 |
| 获取 | `/api/envelopes/:id` | 获取单条 |
| 新建 | `/api/envelopes` | 新建 |
| 更新 | `/api/envelopes/:id` | 更新 |
| 删除 | `/api/envelopes/:id` | 删除 |
