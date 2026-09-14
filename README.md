# PetSight · 宠物视觉建档助手

> 一个**多模态 AI 应用**：上传宠物照片 → 视觉大模型（智谱 GLM-4V）识别品种/体型/毛发/健康建议 → 自动沉淀为可检索的健康档案。
> 与 **PetPals**（多智能体+RAG 电商）组成宠物领域互补项目体系，分别覆盖「多智能体应用」与「多模态视觉理解」能力。

**作者**：Wang Jin Xing
**仓库**：https://github.com/Wang-Jin-Xing/PetSight
**技术栈**：FastAPI · 智谱 GLM-4V（OpenAI 兼容）· 纯静态 HTML 前端 · SQLite · Docker

---

## 技术亮点

- **多模态视觉理解**：调用视觉大模型（GLM-4V）分析宠物图片，输出物种、品种、体型、毛发、健康建议等结构化字段
- **鲁棒 JSON 解析**：自动剥离 markdown 代码块、容错截取 JSON、key:value 兜底，避免模型输出格式波动导致崩溃
- **模型降级策略**：主模型失败自动尝试备用模型（glm-4v），全失败时回退本地确定性逻辑，无 API Key 也能完整演示
- **纯标准库实现**：SQLite 存储用原生 sqlite3、HTTP 调用用 urllib、配置解析用纯标准库，零 ORM/零 requests 依赖
- **Docker 一键部署**：单容器 FastAPI + 静态前端，数据卷持久化档案库

---

## 一、功能说明

| 功能 | 说明 |
|------|------|
| 多模态识别 | 上传宠物照片 → GLM-4V 输出：物种 / 品种 / 体型判断 / 毛发状态 / 健康建议 + 置信度 |
| 档案沉淀 | 识别结果自动结构化写入 SQLite，形成每只宠物的健康档案卡 |
| 档案管理 | 新建档案、档案列表、单档案详情、JSON 导出 |
| 优雅降级 | 未配置 VLM API Key 或调用失败时，自动回退本地确定性逻辑，项目仍可完整演示 |

## 二、识别返回结构（JSON Schema）

```json
{
  "species": "猫",
  "breed": "英国短毛猫",
  "body_condition": "体型正常，无明显消瘦或肥胖",
  "coat_condition": "毛发健康顺滑",
  "health_notes": "按期接种疫苗；每季度体内驱虫；注意饮水",
  "confidence": 0.93
}
```

后端用 `_extract_json` 做**鲁棒解析**：自动剥离 markdown 代码块、容错截取 JSON、key:value 兜底，避免模型偶发输出格式问题导致崩溃。

## 三、Docker 一键启动（推荐）

```bash
docker compose up -d --build
```

浏览器访问 👉 **http://localhost:8001**

上传一张宠物照片即可演示识别效果。

### 配置视觉模型（.env）

```env
# 智谱 GLM-4V（视觉模型），兼容 OpenAI 协议
VLM_API_KEY=你的智谱 API Key
VLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
VLM_MODEL=glm-4v-flash
```

> 不配置也能跑：自动降级为本地确定性逻辑，所有功能仍可用。

### 数据持久化

档案数据存在 Docker 命名卷 `petsight-data` 里，容器删除重建数据不会丢。只有 `docker compose down -v` 才会清除。

## 四、本地开发模式

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

- 首页：http://localhost:8000
- 接口自测页：http://localhost:8000/docs（Swagger UI）
- 视觉识别接口：`POST /api/vision/classify`（multipart file）
- 档案接口：`POST /api/pets` / `GET /api/pets` / `GET /api/pets/{id}`

## 五、目录结构

```
PetSight/
├── .env                    # 视觉模型配置（已被 gitignore 排除）
├── docker-compose.yml      # Docker 一键编排
├── .dockerignore
├── README.md
├── backend/
│   ├── main.py             # FastAPI 入口，挂载静态前端 + 路由
│   ├── config.py           # 配置读取（纯标准库解析 .env）
│   ├── schemas.py          # Pydantic 入参/出参
│   ├── routers/
│   │   ├── vision.py       # 图片识别接口（5MB 限制、base64 编码）
│   │   └── pets.py         # 档案 CRUD 接口
│   ├── service/
│   │   ├── vlm.py          # GLM-4V 调用 + 模型降级 + 鲁棒 JSON 解析
│   │   └── db.py           # SQLite 档案存储（纯标准库 sqlite3，零 ORM）
│   ├── static/index.html   # 单页前端：上传预览 + 结果渲染 + 档案列表
│   ├── tests/              # pytest 测试用例
│   ├── Dockerfile
│   └── requirements.txt
```

## 六、面试讲稿（一段话）

> 独立开发多模态宠物建档助手 PetSight：上传宠物照片后，通过 GLM-4V 视觉大模型识别品种、体型与毛发健康状态，自动结构化并沉淀为可检索的健康档案。工程上做了三层保障：① 鲁棒 JSON 解析（剥离代码块、容错截取、key:value 兜底）应对模型输出波动；② 模型降级链（glm-4v-flash → glm-4v → 本地兜底）确保无 Key 也能完整演示；③ 纯标准库实现（sqlite3 + urllib），零 ORM/零 requests 依赖。它与 PetPals（多智能体+RAG）构成「多智能体应用 + 多模态视觉」互补体系，印证我从文本到多模态的完整 AI 应用开发能力。

---

*PetSight · AI 应用开发实习求职项目 #2*