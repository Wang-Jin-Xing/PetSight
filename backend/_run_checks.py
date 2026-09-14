"""零依赖校验：等价执行 tests/ 里的断言（无 pytest 环境也能跑，用于 CI/演示前自检）。"""
import base64
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

import config  # noqa
import service.db as db  # noqa
import service.vlm as vlm  # noqa

# 独立测试库隔离
TEST_DB = str(BACKEND / "data" / "check_pets.db")
config.DATABASE_PATH = TEST_DB


def reset_db():
    if Path(TEST_DB).exists():
        Path(TEST_DB).unlink()
    db.init()


passed = 0


def check(name, cond):
    global passed
    assert cond, name
    passed += 1
    print(f"  PASS {name}")


# --- db 闭环 ---
reset_db()
pid = db.create_pet({"name": "豆豆", "species": "猫", "breed": "英短",
                     "body_condition": "正常", "coat_condition": "健康顺滑",
                     "health_notes": "定期驱虫", "confidence": 0.9, "mode": "vlm"})
pet = db.get_pet(pid)
check("db.create+get", pet is not None and pet["name"] == "豆豆" and pet["confidence"] == 0.9)
db.create_pet({"name": "A", "species": "狗", "breed": "金毛", "confidence": 0.5})
db.create_pet({"name": "B", "species": "猫", "breed": "加菲"})
check("db.list len=3", len(db.list_pets()) == 3)
check("db.export fields", set(db.export_json()[0]) >= {"id", "name", "species", "breed"})
check("db.get missing None", db.get_pet(9999) is None)

# --- vlm 解析 ---
check("vlm json code-fence", vlm._extract_json("```json\n{\"species\": \"猫\", \"breed\": \"英短\"}\n```")["breed"] == "英短")
check("vlm json in prose", vlm._extract_json("结果如下：{\"species\":\"狗\",\"breed\":\"金毛\"}")["species"] == "狗")
tiny = base64.b64encode(b"\xff\xd8\xff\xe0fakejpeg").decode()
fallback = vlm.classify_pet_image(tiny, "image/jpeg")
check("vlm fallback fields", {"species", "breed", "body_condition", "coat_condition", "health_notes"} <= set(fallback))
check("vlm fallback conf 0", fallback["confidence"] == 0.0)
n = vlm._normalize({"species": "猫", "breed": "加菲"})
check("vlm normalize defaults", n["species"] == "猫" and n["body_condition"] != "" and n["confidence"] == 0.0)

print(f"\nALL {passed} checks PASSED")
