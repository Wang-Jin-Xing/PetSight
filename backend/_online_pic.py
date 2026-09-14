"""从公开图源下载一张宠物照片 → POST 到本机运行中的 /api/vision/classify → 打印真实识别。"""
import sys
import urllib.request
import io

import httpx

BASE = "http://127.0.0.1:8000"

# 候选图源（公开、稳定；按序尝试，取第一个能下到的图片）
URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/3/3e/GoldenRetriever8.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/5d/Golden_Retriever_Carlos_%2810581910556%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/6a/Domestic_cat_tabbies.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1b/Cat_November_2010-1a.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9c/Shiba_Inu_male_2010.jpg",
]

def _is_image(data: bytes) -> bool:
    return data[:2] == b"\xff\xd8" or data[:8] == b"\x89PNG\r\n\x1a\n"

def download(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=6) as r:  # 6 秒硬超时，避免卡死
        d = r.read()
    return d, (r.headers.get("Content-Type") or "")

def main():
    chosen = None
    for u in URLS:
        try:
            d, ct = download(u)
            if _is_image(d) and len(d) > 1000:
                ext = "png" if d[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
                mime = "image/png" if ext == "png" else "image/jpeg"
                chosen = (d, ext, mime, u)
                print("下载成功:", u, "| bytes=", len(d), "| mime=", mime, flush=True)
                break
        except Exception as e:
            print("跳过:", u, type(e).__name__, str(e)[:80], flush=True)
    if not chosen:
        print("所有公开图源均失败，改用 picsum 随机图（非宠物，仅验证链路）")
        try:
            d = urllib.request.urlopen("https://picsum.photos/400/300", timeout=30).read()
            chosen = (d, "jpg", "image/jpeg", "picsum.random")
        except Exception as e:
            print("picsum 也失败:", e)
            return
    data, ext, mime, src = chosen
    r = httpx.post(
        BASE + "/api/vision/classify",
        files={"file": (f"online.{ext}", data, mime)},
        data={"name": "网上抓取的宠物照片"},
        timeout=120,
    )
    print("HTTP", r.status_code)
    print(r.text[:1800])

if __name__ == "__main__":
    main()
