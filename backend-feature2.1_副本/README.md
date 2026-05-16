# Agent 评估平台后端

基于 FastAPI 的 Agent 应用评测平台后端，用于对书籍解说 Agent（LangChain）进行多维度自动化评估。支持前端自由选择 7 个评测模块的任意组合，在预采集的数据集上执行评测并返回结构化报告。

## 技术栈

| 组件     | 技术                               |
| -------- | ---------------------------------- |
| Web 框架 | FastAPI                            |
| ORM      | SQLAlchemy（默认 SQLite）          |
| 配置管理 | pydantic-settings + `.env`         |
| LLM 评测 | OpenAI SDK（兼容阿里云 PAI Judge） |
| 测试     | pytest + httpx                     |

## 项目结构

```
backend/
├── app/
│   ├── api/routes/           # API 路由
│   │   ├── evaluation.py     # 评测核心接口（任务/数据集/运行/摘要/对比）
│   │   ├── agent.py          # Agent 工作台接口（stub）
│   │   └── meta.py           # 健康检查
│   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── eval.py           # 评测相关 DTO（selectedParts, DimensionResult 等）
│   │   └── common.py         # 统一返回结构 ApiResponse<T>
│   ├── models/               # SQLAlchemy ORM 模型
│   │   ├── eval.py           # EvalTask, EvalRun
│   │   └── dataset.py        # Dataset
│   ├── services/evaluation/  # 评测核心逻辑
│   │   ├── eval_service.py   # 业务逻辑（CRUD + 执行 + 汇总）
│   │   ├── evaluators.py     # 评测器接口 + 注册表（编号 1-7 映射）
│   │   ├── effectiveness_evaluator.py  # 模块 5：效果维度（LLM Judge）
│   │   ├── safety_evaluator.py         # 模块 6：安全维度（LLM + difflib）
│   │   ├── performance_evaluator.py    # 模块 7：性能维度（纯计算）
│   │   ├── result_evaluator.py         # 模块 1：面向结果
│   │   ├── process_evaluator.py        # 模块 2：面向过程
│   │   ├── explicit_metrics.py         # 模块 3：显式指标
│   │   ├── fuzzy_metrics.py            # 模块 4：模糊指标（Ragas）
│   │   ├── ragas_adapter.py            # Ragas 评测适配（模块 4 调用）
│   │   └── llm_judge.py               # LLM-as-a-Judge 共享调用模块
│   ├── core/config.py        # 全局配置
│   └── db/                   # 数据库引擎与会话
├── scripts/
│   ├── collect_dataset.py    # 采集脚本：调 Agent 生成评测数据集
│   └── import_datasets.py    # 导入脚本：将 JSONL 文件写入数据库
├── datasets/                 # 评测数据集（JSONL）；含 L1–L4 与 eval_module_M*.jsonl
├── tests/
│   ├── conftest.py                 # pytest 共享 fixture
│   ├── eval/                       # 题本 .txt、README（L1–L4 + 模块 M1–M4）
│   ├── test_eval_modules.py        # 模块 5/6/7 测试
│   ├── test_eval_modules_1_2.py    # 模块 1/2 测试
│   ├── test_eval_modules_3_4.py    # 模块 3/4 测试
│   ├── test_eval_tasks.py          # 任务 CRUD 测试
│   └── test_health.py              # 健康检查
├── .env.example
└── requirements.txt
```

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入实际配置

# 3. 导入数据集到数据库
python -m scripts.import_datasets

# 4. 启动服务
uvicorn app.main:app --reload --port 8080
```

访问 `http://127.0.0.1:8080/docs` 查看 Swagger 文档。

## .env 配置说明

| 变量              | 说明                               | 默认值                   |
| ----------------- | ---------------------------------- | ------------------------ |
| `APP_NAME`        | 应用名称                           | `agent-eval-backend`     |
| `ENV`             | 运行环境                           | `dev`                    |
| `CORS_ORIGINS`    | 允许跨域的前端地址（逗号分隔）     | `http://localhost:5173`  |
| `DATABASE_URL`    | 数据库连接                         | `sqlite:///./app.db`     |
| `AGENT_BASE_URL`  | Agent 服务地址（仅采集数据集时用） | `http://localhost:8000`  |
| `OPENAI_API_KEY`  | LLM Judge API Key                  | 无（不配则用 stub 评分） |
| `OPENAI_BASE_URL` | LLM 兼容接口地址（如阿里云 PAI）   | 无                       |
| `OPENAI_MODEL`    | 评测用模型名称                     | `pai-judge`              |

## 评测模块

| 编号 | 名称     | 状态                         |
| ---- | -------- | ---------------------------- |
| 1    | 面向结果 | 已实现                       |
| 2    | 面向过程 | 已实现                       |
| 3    | 显式指标 | 已实现                       |
| 4    | 模糊指标 | 已实现（Ragas）              |
| 5    | 效果维度 | 已实现（LLM Judge）          |
| 6    | 安全维度 | 已实现（LLM + 文本相似度）   |
| 7    | 性能维度 | 已实现（纯计算）             |

## 主要接口

### 数据集
| 方法   | 路径                        | 说明                     |
| ------ | --------------------------- | ------------------------ |
| GET    | `/evaluation/datasets`      | 数据集列表（前端下拉框） |
| POST   | `/evaluation/datasets`      | 创建数据集               |
| DELETE | `/evaluation/datasets/{id}` | 删除数据集               |

### 评测任务
| 方法   | 路径                     | 说明                                    |
| ------ | ------------------------ | --------------------------------------- |
| GET    | `/evaluation/tasks`      | 任务列表                                |
| POST   | `/evaluation/tasks`      | 新建任务（传 `selectedParts: [5,6,7]`） |
| GET    | `/evaluation/tasks/{id}` | 任务详情                                |
| PATCH  | `/evaluation/tasks/{id}` | 更新任务                                |
| DELETE | `/evaluation/tasks/{id}` | 删除任务                                |

### 评测执行
| 方法 | 路径                          | 说明                 |
| ---- | ----------------------------- | -------------------- |
| POST | `/evaluation/tasks/{id}/runs` | 启动评测（后台执行） |
| GET  | `/evaluation/runs/{id}`       | 查询运行状态与结果   |

### 结果查询
| 方法 | 路径                           | 说明                                                           |
| ---- | ------------------------------ | -------------------------------------------------------------- |
| GET  | `/evaluation/summary?task_id=` | 评测摘要（`overallScore` + `dimensions[{code,score,detail}]`） |
| POST | `/evaluation/compare`          | 多任务对比                                                     |

### 其他
| 方法 | 路径      | 说明     |
| ---- | --------- | -------- |
| GET  | `/health` | 健康检查 |

## 工具脚本

```bash
# 采集数据集：调 Agent 获取真实回答，生成 JSONL（默认 M1～M4 模块专用题本）
python -m scripts.collect_dataset
python -m scripts.collect_dataset L1 L2 L3 L4   # 分层题本 L1–L4
python -m scripts.collect_dataset M1 M2 M3 M4   # 仅模块专用题本
python -m scripts.collect_dataset --mock       # 不调 Agent，生成骨架

# 导入数据集到数据库
python -m scripts.import_datasets
```

## 测试

```bash
python -m pytest tests/ -v
```

## 数据库

开发环境使用 SQLite（`app.db`），表结构变更时删除重建：

```bash
rm app.db
python -c "from app.db.base import Base; from app.db.session import engine; from app.models import eval, dataset, agent; Base.metadata.create_all(bind=engine)"
python -m scripts.import_datasets
```
