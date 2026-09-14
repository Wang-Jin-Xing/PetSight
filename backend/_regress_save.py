import httpx, base64, sys, os

BASE = "http://127.0.0.1:8000"

# probe
try:
    r = httpx.get(BASE + "/api/pets", timeout=5)
    print("[probe /api/pets]", r.status_code)
except Exception as e:
    print("[probe failed]", type(e).__name__, e); sys.exit(1)

# build a >400k base64 string (noise-ish, deterministic)
seed = os.urandom(520000)
b64 = base64.b64encode(seed).decode()
print("[big base64 len]", len(b64), ">400000:", len(b64) > 400000)

payload = {
    "name": "回归-大图", "species": "狗", "breed": "金毛",
    "body_condition": "正常", "coat_condition": "健康顺滑",
    "health_notes": "定期驱虫，按时接种疫苗", "confidence": 0.9,
    "image_data_url": "data:image/jpeg;base64," + b64, "mode": "vlm",
}
r = httpx.post(BASE + "/api/pets", json=payload, timeout=15)
print("[save big]", r.status_code)
if r.status_code not in (200, 201):
    print("  body:", r.text[:300]); sys.exit(1)
saved = r.json()
print("  saved id:", saved.get("id"), "| img_len:", len(saved.get("image_data_url") or ""))

g = httpx.get(f"{BASE}/api/pets/" + str(saved["id"]), timeout=10)
gj = g.json()
print("[read back]", g.status_code, "| name:", gj.get("name"), "| img_len:", len(gj.get("image_data_url") or ""))
print("READBACK_OK" if g.status_code == 200 and gj.get("image_data_url") else "READBACK_FAIL")
