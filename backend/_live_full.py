"""活体全闭环：识别→保存档案→列档→导出 JSON。全部走运行中的服务。"""
import httpx

BASE = "http://127.0.0.1:8000"

def make_png(w=96, h=96):
    import struct, zlib
    raw = bytearray()
    for _ in range(h):
        raw.append(0)
        for _ in range(w):
            raw += bytes((224, 160, 120))
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    return png

def main():
    c = httpx.Client(base_url=BASE, timeout=90)
    # 1) 识别
    r = c.post("/api/vision/classify", files={"file": ("pet.png", make_png(), "image/png")}, data={"name": "联调豆豆"})
    rec = r.json()
    print("[识别]", r.status_code, "| mode=", rec.get("_mode"), "| species=", rec.get("species"))
    # 2) 保存档案
    payload = {
        "name": "联调豆豆", "species": rec.get("species"), "breed": rec.get("breed"),
        "body_condition": rec.get("body_condition"), "coat_condition": rec.get("coat_condition"),
        "health_notes": rec.get("health_notes"), "confidence": rec.get("confidence"),
        "image_data_url": rec.get("image_data_url"), "mode": rec.get("_mode"),
    }
    s = c.post("/api/pets", json=payload)
    pid = s.json().get("id")
    print("[保存档案]", s.status_code, "id=", pid)
    # 3) 读详情
    d = c.get(f"/api/pets/{pid}").json()
    print("[读取详情]", d.get("name"), d.get("breed"), "mode=", d.get("mode"))
    # 4) 导出
    ex = c.get("/api/pets/export/json").json()
    print("[导出条数]", len(ex))

if __name__ == "__main__":
    main()
