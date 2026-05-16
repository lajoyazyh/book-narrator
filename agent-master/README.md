# Book Narrator Agent

基于 LangChain 的书籍解说生成系统，支持自动加载书籍、生成解说词、保存文件和生成音频。

## 📁 项目结构

```
book-narrator-agent/
├── books/                          # 存放待处理的书籍文件
├── data/                           # 数据文件
├── logs/                           # 日志文件
├── output/                         # 输出文件（解说词、音频等）
│   ├── audio/                      # 生成的音频文件
│   └── scripts/                    # 生成的解说词
├── src/                            # 源代码
│   ├── agents/                     # Agent 实现
│   │   └── langchain_agent.py      # LangChain Agent 实现
│   ├── api/                        # API 服务
│   │   └── server.py               # FastAPI 接口
│   ├── config/                     # 配置文件
│   │   ├── path.py                 # 路径配置
│   │   └── settings.py             # 应用配置
│   ├── prompts/                    # 提示词模板
│   │   ├── agent_prompts.py        # Agent 系统提示词
│   │   └── narration_prompts.py    # 解说提示词
│   ├── tools/                      # 工具类
│   │   ├── audio_generator.py      # 音频生成器
│   │   ├── book_loader.py          # 书籍加载器
│   │   ├── file_saver.py           # 文件保存器
│   │   ├── langchain_tools.py      # LangChain 工具包装
│   │   ├── narrator.py             # 解说生成器
│   │   └── todo.py                 # 工作计划管理
│   └── utils/                      # 工具函数
│       └── logger.py               # 日志工具
├── tests/                          # 测试文件
├── .env                            # 环境变量
├── api_main.py                     # API 服务入口
├── main.py                         # 主程序入口
└── requirements.txt                # 依赖列表
```

## 🔧 环境搭建

### 1. 克隆项目

```bash
git clone <repository-url>
cd Agent
```

### 2. 创建虚拟环境

```bash
conda create -n agent python=3.10
conda activate agent
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

必填项：
- `BASE_URL` - OpenAI 兼容 API 地址
- `MODEL_NAME` - 模型名称
- `API_KEY_ENV` - API 密钥

可选项（见 `.env.example` 注释说明）

## 🚀 项目运行

### 方式一：命令行运行

```bash
python main.py
```

### 方式二：启动 API 服务

```bash
python api_main.py
```

服务启动后：
- API 地址：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`
- ReDoc 文档：`http://localhost:8000/redoc`

## 📝 测试运行

在项目根目录执行以下命令运行测试：

```bash
python tests/test_00/test.py
```

## 📚 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/agent/run` | POST | 运行 Agent |
| `/api/v1/agent/context` | GET | 获取上下文状态 |
| `/api/v1/agent/reset` | POST | 重置上下文 |
| `/api/v1/audio/{filename}` | GET | 获取音频文件 |
| `/api/v1/audio/list` | GET | 列出音频文件 |

详细文档见 Agent 接口文档

## 📄 项目文档

| 文档 | 说明 |
|------|------|
| [需求文档] | 功能需求与验收标准 |
| [架构设计] | 系统架构与模块设计 |
| [API 文档] | 接口详细说明 |

## 🔄 CI/CD

