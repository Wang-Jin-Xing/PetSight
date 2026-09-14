"""视觉识别服务：调用 OpenAI 兼容视觉大模型（SiliconFlow Qwen2.5-VL 等）；无 Key/失败时本地降级。"""

import base64
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Optional, List

from config import VLM_API_KEY, VLM_BASE_URL, VLM_MODEL, VLM_TEMPERATURE

# 期望模型输出的 JSON 结构
SCHEMA_PROMPT = (
    "你是一名资深宠物医生与宠物品种学专家。请分析这张宠物图片，只返回一个合法的 JSON 对象，不要输出任何其他文字、Markdown 或解释。字段如下：\n"
    "{\n"
    '  "species": "猫|狗|其他",\n'
    '  "breed": "最可能的品种，如：英短/金毛 等",\n'
    '  "body_condition": "体型判断，如：正常/偏瘦/偏胖/过于肥胖，附一句依据",\n'
    '  "coat_condition": "毛发状态，如：健康顺滑/毛发枯燥/局部掉毛",\n'
    '  "health_notes": "2-4 条可执行的健康观察与建议，逗号分隔",\n'
    '  "confidence": 0.0\n'
    "}\n"
)

# 备用视觉模型列表（主模型失败时依次尝试）
FALLBACK_MODELS = [
    "Qwen/Qwen3-VL-8B-Instruct",
    "Qwen/Qwen3-VL-32B-Instruct",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Pro/Qwen/Qwen2-VL-7B-Instruct",
]


def _strip_code_fence(text: str) -> str:
    """去除模型输出中的 ```json ... ``` 包裹，提取其中的 JSON。"""
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    return t


def _extract_json(text: str) -> Optional[dict]:
    """稳定地从模型输出里提取 JSON 对象。"""
    t = _strip_code_fence(text)
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(t[start : end + 1])
        except json.JSONDecodeError:
            pass
    # 兜底：按行解析 key:value（容错模型输出缺失引号/逗号）
    data: Dict[str, str] = {}
    for line in t.splitlines():
        m = re.match(r'"?([^"]+)"?\s*:\s*"?([^"]*?)"?,?\s*$', line.strip())
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data or None


def _normalize(payload: dict) -> dict:
    """标准化 VLM 返回字段，确保每个 key 都有合法默认值；health_notes 统一为逗号分隔字符串。"""
    notes = payload.get("health_notes", "")
    if isinstance(notes, list):
        notes = "，".join(str(n) for n in notes)
    elif not isinstance(notes, str):
        notes = str(notes)
    return {
        "species": str(payload.get("species", "未知")),
        "breed": str(payload.get("breed", "未知")),
        "body_condition": str(payload.get("body_condition", "——")),
        "coat_condition": str(payload.get("coat_condition", "——")),
        "health_notes": notes.strip() or "——",
        "confidence": float(payload.get("confidence", 0.0) or 0.0),
    }


def _call_one_model(image_data_url: str, model: str) -> Optional[dict]:
    """单次调用指定视觉模型，成功返回 dict，失败返回 None。"""
    url = f"{VLM_BASE_URL}/chat/completions"
    body = {
        "model": model,
        "temperature": VLM_TEMPERATURE,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SCHEMA_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {VLM_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    content = payload["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content)
    return _extract_json(content)


def _call_vlm_with_fallback(image_data_url: str) -> dict:
    """先尝试配置的主模型，失败则依次尝试备用视觉模型；返回 dict 或含 _error 的 dict。"""
    # 构建模型尝试列表：配置主模型 + 备用列表（去重）
    tried = []
    models_to_try: List[str] = []
    for m in [VLM_MODEL] + FALLBACK_MODELS:
        if m and m not in tried:
            models_to_try.append(m)
            tried.append(m)

    last_err = ""
    for model in models_to_try:
        try:
            extracted = _call_one_model(image_data_url, model)
            if extracted:
                return extracted
            last_err = f"模型 {model} 未返回合法 JSON"
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", "ignore")[:200]
            except Exception:
                pass
            last_err = f"HTTP {e.code} ({model}): {err_body}"
        except Exception as e:
            last_err = f"{type(e).__name__} ({model}): {e}"
    return {"_error": last_err}


def _local_fallback() -> dict:
    """本地降级：无 Key 或调用失败时的确定性结果，保证流程可完整演示。"""
    return {
        "species": "未知",
        "breed": "未知",
        "body_condition": "——（未配置视觉模型，无法自动判断）",
        "coat_condition": "——（未配置视觉模型，无法自动判断）",
        "health_notes": "请配置可用的视觉大模型 API Key 以启用真实图片识别；当前为本地降级模式。",
        "confidence": 0.0,
        "_mode": "local_fallback",
    }


def classify_pet_image(image_base64: str, mime: str = "image/jpeg") -> dict:
    """识别宠物图片，返回结构化档案字段。始终返回可用的 dict。"""
    image_data_url = f"data:{mime};base64,{image_base64}"
    if not VLM_API_KEY:
        return _local_fallback()
    payload = _call_vlm_with_fallback(image_data_url)
    if "_error" in payload:
        return {**_local_fallback(), "_mode": "vlm_error", "_error": payload["_error"]}
    return {**_normalize(payload), "_mode": "vlm"}
