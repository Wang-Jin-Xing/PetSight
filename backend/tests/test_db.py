"""档案存储单元测试（纯标准库 SQLite，不依赖网络/FastAPI）。"""
import os
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))  # 让 backend 目录可被测试导入

# 使用独立测试库，避免污染演示数据
TEST_DB = str(BACKEND / "data" / "test_pets.db")
os.environ["DATABASE_PATH"] = TEST_DB
import sys  # noqa: E402

from service import db  # noqa: E402

# 重新加载 config（读到测试库路径）
import importlib  # noqa: E402
import service.db as _db_module  # noqa: E402

_db_module.config.DATABASE_PATH = TEST_DB


@pytest.fixture(autouse=True)
def _clean():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_create_and_get_pet():
    pid = db.create_pet({
        "name": "豆豆", "species": "猫", "breed": "英短",
        "body_condition": "正常", "coat_condition": "健康顺滑",
        "health_notes": "定期驱虫", "confidence": 0.9, "mode": "vlm",
    })
    pet = db.get_pet(pid)
    assert pet is not None
    assert pet["name"] == "豆豆"
    assert pet["breed"] == "英短"
    assert pet["confidence"] == 0.9
    assert pet["mode"] == "vlm"


def test_list_and_export():
    db.create_pet({"name": "A", "species": "狗", "breed": "金毛", "confidence": 0.5})
    db.create_pet({"name": "B", "species": "猫", "breed": "加菲"})
    pets = db.list_pets()
    assert len(pets) == 2
    exported = db.export_json()
    assert len(exported) == 2
    assert set(exported[0].keys()) >= {"id", "name", "species", "breed"}


def test_get_missing_returns_none():
    assert db.get_pet(9999) is None
