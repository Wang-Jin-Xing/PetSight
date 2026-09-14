"""视觉识别接口：上传宠物照片 → 视觉模型识别 → 返回结构化档案。"""
from __future__ import annotations

import base64
import io

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from service.vlm import classify_pet_image

router = APIRouter(prefix="/api/vision", tags=["vision"])

MAX_BYTES = 5 * 1024 * 1024  # 5MB 上限


@router.post("/classify")
async def classify(
    file: UploadFile = File(..., description="宠物照片"),
    name: str = Form("未命名", description="宠物昵称（可选）"),
):
    """读取图片，调用 GLM-4V 识别，返回结构化档案字段。"""
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="图片过大，请上传 5MB 以内的照片")
    if not data:
        raise HTTPException(status_code=400, detail="未读取到图片内容")

    mime = file.content_type or "image/jpeg"
    b64 = base64.b64encode(data).decode("ascii")

    result = classify_pet_image(b64, mime)
    result.setdefault("name", name or "未命名")
    result.setdefault("image_data_url", f"data:{mime};base64,{b64}")
    return result
