"""SiliconFlow 连通性探测：验证 Key 有效 + 列出可用模型（便于挑选正确视觉模型 ID）。"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VLM_API_KEY, VLM_BASE_URL

def probe(base: str, key: str) -> None:
    url = base.rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print("OK models endpoint. total:", len(data.get("data", [])))
        # 过滤出视觉类模型（含 vl / vision / llama-3.2-11b / gemma-3 等多模态）
        fields = []
        for m in data.get("data", []):
            mid = m.get("id", "")
            low = mid.lower()
            if ("vl" in low) or ("vision" in low) or ("gemma-3" in low) or ("11b" in low and "llama" in low) or ("2b" in low):
                fields.append(mid)
        print("--- 视觉/多模态候选模型 ---")
        for mid in sorted(fields[:60]):
            print("  ", mid)
    except urllib.error.HTTPError as e:
        print("HTTPError", e.code, e.read().decode("utf-8", "ignore")[:300])
    except Exception as e:
        print("ERR", type(e).__name__, e)

if __name__ == "__main__":
    print("base:", VLM_BASE_URL, "| key set:", bool(VLM_API_KEY))
    probe(VLM_BASE_URL, VLM_API_KEY)
