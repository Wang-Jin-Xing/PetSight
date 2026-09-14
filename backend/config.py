"""PetSight 配置：从 .env / 环境变量读取，纯标准库实现。"""
from __future__ import annotations

import os
from pathlib import Path

# 项目根目录（backend 的上一级）
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env(PROJECT_ROOT / ".env")


def get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


VLM_API_KEY = get("VLM_API_KEY")
VLM_BASE_URL = get("VLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/").rstrip("/")
VLM_MODEL = get("VLM_MODEL", "glm-4v-flash")
VLM_TEMPERATURE = float(get("VLM_TEMPERATURE", "0.3"))
DATABASE_PATH = str((PROJECT_ROOT / get("DATABASE_PATH", "data/pets.db")).resolve())

HAS_VLM = bool(VLM_API_KEY)
