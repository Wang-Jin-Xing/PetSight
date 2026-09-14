# ===== PetSight 后端镜像 =====
# Python 3.11 + FastAPI + SQLite + 视觉大模型(VLM)
# 基础镜像可通过构建参数 PYTHON_BASE 覆盖（国内网络可用加速地址）
ARG PYTHON_BASE=python:3.11-slim
FROM ${PYTHON_BASE}

WORKDIR /app

# Python 运行环境：
# - PYTHONUNBUFFERED：日志实时输出，便于 docker logs 查看
# - PYTHONDONTWRITEBYTECODE：不生成 .pyc，保持镜像干净
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 先单独复制并安装依赖，利用 Docker 分层缓存（代码变更不重装依赖）
# PIP_INDEX_URL 可覆盖为国内 PyPI 镜像（如华为云 / 清华 tuna / 阿里云）
ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    PIP_NO_CACHE_DIR=0 pip install \
        -i ${PIP_INDEX_URL} \
        --retries 8 --timeout 120 \
        -r requirements.txt

# 复制项目源码
COPY . .

# 数据目录（SQLite 档案库），运行时由 compose 挂载命名卷覆盖
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]