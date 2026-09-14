"""活体联调：构造合法 PNG → POST 到 运行中的服务 /api/vision/classify → 打印真实识别结果。"""
import io
import struct
import zlib
import sys

import httpx

BASE = "http://127.0.0.1:8000"


def make_png(w=96, h=96, color=(224, 160, 120)) -> bytes:
    """纯标准库生成一张合法 PNG（无 Pillow）。"""
    raw = bytearray()
    for _ in range(h):
        raw.append(0)  # filter type: None
        for _ in range(w):
            raw += bytes(color)
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8bit, RGB
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    return png


def main():
    png = make_png()
    print("PNG bytes:", len(png))
    try:
        r = httpx.post(
            f"{BASE}/api/vision/classify",
            files={"file": ("pet.png", png, "image/png")},
            data={"name": "联调测试宠"},
            timeout=90,
        )
    except Exception as e:
        print("HTTP ERROR:", type(e).__name__, e)
        return
    print("status:", r.status_code)
    print("body:", r.text[:2500])


if __name__ == "__main__":
    main()
