"""视觉识别服务单元测试：鲁棒 JSON 解析 + 本地降级（不触发真实网络调用）。"""
import base64
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from service import vlm  # noqa: E402


def test_json_with_code_fence():
    """模型输出带 ```json 包裹时应正确提取。"""
    raw = "```json\n{\"species\": \"猫\", \"breed\": \"英短\", \"confidence\": 0.8}\n```\n"
    assert vlm._extract_json(raw)["breed"] == "英短"


def test_json_like_text():
    """模型输出夹杂讲解文字时也能截取 JSON。"""
    raw = "分析结果如下：{\"species\":\"狗\",\"breed\":\"金毛\"} 谢谢。"
    assert vlm._extract_json(raw)["species"] == "狗"


def test_fallback_structure():
    """无 Key 或调用失败时返回可用的结构化兜底。"""
    tiny = base64.b64encode(b"\xff\xd8\xff\xe0fakejpeg").decode()
    ok = vlm.classify_pet_image(tiny, "image/jpeg")
    assert {"species", "breed", "body_condition", "coat_condition", "health_notes"} <= set(ok.keys())
    assert ok["confidence"] == 0.0


def test_normalize_fills_defaults():
    p = vlm._normalize({"species": "猫", "breed": "加菲"})
    assert p["species"] == "猫"
    assert p["body_condition"] != ""
    assert p["confidence"] == 0.0
