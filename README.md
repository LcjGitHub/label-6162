# 手写信封邮票组合收藏系统

第三代视图框架配合组件库与样式工具的前端，轻量网框架配合本地关系型数据库的后端。用于管理手写信封上的邮票与邮戳收藏信息、邮戳图鉴的独立管理，以及收藏标签的分类管理。

## 技术栈

| 层级 | 技术 | 端口 |
|------|------|------|
| 前端 | 第三代视图框架、组件库、样式工具、集中式存储、通用请求库 | **4101** |
| 后端 | 轻量网框架、本地关系型数据库（`backend/data/envelope.db`） | **4000** |

## 核心功能

### 信封收藏

- 信封收藏数据表格列表（搜索、排序、分页）
- 详情、编辑、新建页面
- 字段：寄出地、目的地、年份、邮票描述、邮戳类型、品相、备注（可选，最多 1000 字符）
- 完整增删改查，首次启动自动写入 5 条示例数据
- **批量导入**：支持 CSV 文件批量导入收藏记录，含实时预览、表头校验、逐行校验与错误提示
  - CSV 表头：寄出地,目的地,年份,邮票描述,邮戳类型,品相,备注
  - 备注列为可选，允许为空
- **多标签绑定**：每个信封可绑定多个收藏标签，支持在新建/编辑时多选

### 邮戳图鉴

- 邮戳图鉴数据表格列表（搜索、排序、分页）
- 详情、编辑、新建页面
- 字段：名称、形状、常见用途、简介
- 完整增删改查，首次启动自动写入 3 条示例数据
- 独立路由、状态管理与接口层，与信封收藏模块互不耦合

#### 邮戳图鉴示例数据

| 名称 | 形状 | 常见用途 | 简介 |
|------|------|----------|------|
| 圆形日戳 | 圆形 | 日常信件盖销 | 最常见的邮戳类型，通常为圆形，包含地名、日期和时间信息，用于盖销邮票证明邮件已付邮资。 |
| 方形纪念戳 | 方形 | 纪念活动与特殊事件 | 为纪念重大事件、节日或邮票发行而特制的方形邮戳，通常带有主题图案和纪念文字，具有收藏价值。 |
| 风景日戳 | 圆形 | 旅游景点邮局 | 刻有当地风景名胜图案的特种日戳，常见于旅游景区邮局，兼具邮政功能与纪念意义，深受集邮爱好者喜爱。 |

### 标签管理

- 标签卡片式列表，可直观查看所有标签及对应颜色
- 新建、重命名、删除标签
- 字段：名称、颜色（10 种预设颜色可选）
- 完整增删改查，首次启动自动写入 3 条预设标签
- 独立路由、状态管理与接口层
- 删除标签时自动解除所有信封上的该标签关联（级联删除）

#### 预设标签示例

| 名称 | 颜色 | 色值 |
|------|------|------|
| 珍品收藏 | 红色 | `#ef4444` |
| 文革时期 | 橙色 | `#f59e0b` |
| 生肖系列 | 绿色 | `#10b981` |

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
    │   ├── api/        # 接口层
    │   │   ├── envelope.js
    │   │   ├── postmark.js
    │   │   └── tag.js
    │   ├── stores/     # 状态管理
    │   │   ├── envelope.js
    │   │   ├── postmark.js
    │   │   └── tag.js
    │   ├── views/      # 页面组件
    │   │   ├── Dashboard.vue
    │   │   ├── EnvelopeList.vue
    │   │   ├── EnvelopeDetail.vue
    │   │   ├── PostmarkList.vue
    │   │   ├── PostmarkDetail.vue
    │   │   └── TagList.vue
    │   └── router/     # 路由配置
    │       └── index.js
    └── package.json
```

## 启动方式

### 后端（一条命令启动）

在项目根目录执行：

```
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && python app.py
```

> 苹果系统 / Linux 系统将激活命令改为：`source .venv/bin/activate`

后端启动后访问：
- 信封收藏：<http://localhost:4000/api/envelopes>
- 邮戳图鉴：<http://localhost:4000/api/postmarks>
- 标签管理：<http://localhost:4000/api/tags>
- 收藏统计：<http://localhost:4000/api/envelopes/stats>

### 前端（一条命令开发启动）

另开一个终端，在项目根目录执行：

```
cd frontend && npm install && npm run dev
```

前端启动后访问：
- 首页：<http://localhost:4101>
- 数据看板：<http://localhost:4101/dashboard>

## 依赖说明

- 后端依赖安装在 `backend/.venv` 虚拟环境内
- 前端依赖安装在 `frontend/node_modules` 内
- 无需全局安装其他包管理工具

## 接口说明

### 信封收藏接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/envelopes` | 获取全部信封（含关联标签列表） |
| GET | `/api/envelopes/:id` | 获取单条信封（含关联标签列表） |
| POST | `/api/envelopes` | 新建信封（支持 `tag_ids` 字段同时绑定标签） |
| PUT | `/api/envelopes/:id` | 更新信封（支持 `tag_ids` 字段同时更新标签） |
| DELETE | `/api/envelopes/:id` | 删除信封 |
| GET | `/api/envelopes/stats` | 获取收藏统计数据（总数、按品相分组、按年代区间分组） |

### 邮戳图鉴接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/postmarks` | 获取全部邮戳 |
| GET | `/api/postmarks/:id` | 获取单条邮戳 |
| POST | `/api/postmarks` | 新建邮戳 |
| PUT | `/api/postmarks/:id` | 更新邮戳 |
| DELETE | `/api/postmarks/:id` | 删除邮戳 |

### 标签管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tags` | 获取全部标签 |
| GET | `/api/tags/:id` | 获取单条标签 |
| POST | `/api/tags` | 新建标签（请求体：`{ name, color? }`） |
| PUT | `/api/tags/:id` | 更新标签（重命名/改色，请求体：`{ name, color? }`） |
| DELETE | `/api/tags/:id` | 删除标签（级联删除所有信封关联） |

### 信封标签绑定接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/envelopes/:id/tags` | 获取指定信封的所有标签 |
| PUT | `/api/envelopes/:id/tags` | 全量更新信封的标签（请求体：`{ tag_ids: [1, 2, 3] }`） |

## 前端访问路径

| 模块 | 路径 | 说明 |
|------|------|------|
| 收藏统计 | `/dashboard` | 收藏数据统计看板 |
| 信封收藏 | `/` | 信封列表页 |
| 信封收藏 | `/envelopes/new` | 新建信封（含标签多选） |
| 信封收藏 | `/envelopes/:id` | 信封详情（含彩色标签展示） |
| 信封收藏 | `/envelopes/:id/edit` | 编辑信封（含标签多选） |
| 邮戳图鉴 | `/postmarks` | 邮戳列表页 |
| 邮戳图鉴 | `/postmarks/new` | 新建邮戳 |
| 邮戳图鉴 | `/postmarks/:id` | 邮戳详情 |
| 邮戳图鉴 | `/postmarks/:id/edit` | 编辑邮戳 |
| 标签管理 | `/tags` | 标签列表（新建、重命名、删除） |
