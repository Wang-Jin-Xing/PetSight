import httpx, base64, random, sys

BASE = "http://127.0.0.1:8000"

# probe
try:
    r = httpx.get(BASE + "/api/pets", timeout=5); print("[probe /api/pets]", r.status_code)
except Exception as e:
    print("[probe failed]", type(e).__name__, e); sys.exit(1)

# build a noisy big PNG 1000x1000 with random RGB -> base64 clearly > 400k
import zlib, struct
def noisy_png(w=1000, h=1000):
    raw = bytearray()
    rnd = random.Random(42)
    for _ in range(h):
        row = bytearray([0])
        for _ in range(w):
            row += bytes((rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)))
        raw += row
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    def chunk(tag, d):
        c = tag + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c))
    return b"PNG

" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")

png = noisy_png()
b64 = base64.b64encode(png).decode()
print("[big noisy base64 len]", len(b64), ">400000:", len(b64) > 400000)

payload = {
    "name": "回归-噪声大图", "species": "狗", "breed": "金毛",
    "body_condition": "正常", "coat_condition": "健康顺滑",
    "health_notes": "定期驱虫，按时接种疫苗", "confidence": 0.9,
    "image_data_url": "data:image/png;base64," + b64, "mode": "vlm",
}
r = httpx.post(BASE + "/api/pets", json=payload, timeout=15)
print("[save big noisy]", r.status_code)
if r.status_code not in (200, 201):
    print("  body:", r.text[:300]); sys.exit(1)
saved = r.json()
print("  saved id:", saved.get("id"), "| img_len:", len(saved.get("image_data_url") or ""))
g = httpx.get(f"{BASE}/api/pets/{saved['id']}", timeout=10)
print("[read back]", g.status_code, "| name:", g.json().get("name"), "| img_len:", len(g.json().get("image_data_url") or ""))
print("READBACK_OK" if g.status_code == 200 and g.json().get("image_data_url") else "READBACK_FAIL")
