# PetSight · 宠物视觉建档助手

> **第二个 AI 项目**：上传宠物照片 → SiliconFlow 视觉大模型（Qwen2.5-VL）识别品种/体型/毛发与健康提示 → 沉淀为可检索的健康档案。
> 与 **PetPals**（多智能体+RAG电商）组成宠物领域一脉相承的项目体系。
> 这个项目为简历补齐了**多模态 / 视觉理解**能力，是差异化亮点。

**作者**：Wang Jin Xing
**技术栈**：FastAPI · SiliconFlow Qwen2.5-VL（OpenAI 兼容）· React（静态托管前端）· SQLite · Docker

---

## 一、这个项目能干什么

| 功能 | 说明 |
|------|------|
| 📷 多模态识别 | 上传宠物照片 → Qwen2.5-VL / GLM-4V 输出：物种 / 品种 / 体型判断 / 毛发状态 / 健康建议 + 置信度 |
| 🐾 档案沉淀 | 识别结果自动结构化，写入 SQLite，形成每只宠物的健康档案卡 |
| 📋 档案管理 | 新建档案、档案列表、单档案详情、JSON 导出 |
| 🛡 优雅降级 | 未配置 Visual API Key 或调用失败时，自动回退为本地确定性逻辑，项目仍可完整演示 |

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

## 三、本地启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

打开浏览器 👉 **http://localhost:8000** —— 上传一张宠物照片即可演示。

- 接口自测页：http://localhost:8000/docs（Swagger）
- 视觉识别接口：`POST /api/vision/classify`（multipart file）
- 档案接口：`POST /api/pets` / `GET /api/pets` / `GET /api/pets/{id}`

### 配置视觉模型（.env，已含你的 SiliconFlow Key）

```env
VLM_API_KEY=你的SiliconFlow API Key
VLM_BASE_URL=https://api.siliconflow.cn/v1
VLM_MODEL=Qwen/Qwen2.5-VL-7B-Instruct   # 识别失败会自动尝试备用视觉模型
```

> ⚠️ `.env` 已被 `.gitignore` 排除，**不会提交**。正式演示前可在 SiliconFlow 控制台重置 Key。

## 四、Docker 一键启动

```bash
docker compose up -d --build
```

访问 http://localhost:8000

## 五、目录结构

```
PetSight/
├── .env                 # SiliconFlow 视觉 Key（已被 gitignore 排除）
├── docker-compose.yml
├── backend/
│   ├── main.py          # FastAPI 入口，挂载静态前端 + 路由
│   ├── config.py        # 配置读取（纯标准库解析 .env）
│   ├── schemas.py       # Pydantic 入参/出参
│   ├── routers/
│   │   ├── vision.py    # 图片识别接口
│   │   └── pets.py      # 档案接口
│   ├── service/
│   │   ├── vlm.py       # Qwen2.5-VL 调用 + 本地降级 + 鲁棒JSON解析
│   │   └── db.py        # SQLite 档案存储（纯标准库，零ORM依赖）
│   ├── static/index.html# 单页前端：上传预览 + 结果渲染 + 档案列表
│   ├── Dockerfile
│   └── requirements.txt
```

## 六、面试讲稿（一段话）

> 独立开发多模态宠物建档助手 PetSight：上传宠物照片后，通过Qwen2.5-VL / GLM-4V 等视觉大模型 识别品种、体型与毛发健康状态，自动结构化并沉淀为可检索的健康档案；接口层做了**鲁棒 JSON 解析**与**模型降级**（flash→plus→本地兜底），确保无 Key 也能完整演示。它与 PetPals（多智能体+RAG）构成「多智能体应用 + 多模态视觉」互补体系，印证我从文本到多模态的完整 AI 应用开发能力。

---

*PetSight · AI 应用开发实习求职项目 #2*