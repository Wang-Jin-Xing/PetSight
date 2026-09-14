"""接口入参/出参校验（Pydantic v2）。"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class PetProfileIn(BaseModel):
    """建档入参：识别结果 + 用户补充，落库为宠物健康档案。"""
    name: str = Field(..., min_length=1, max_length=50, description="宠物昵称")
    species: str = Field("未知", max_length=20)
    breed: str = Field("未知", max_length=40)
    body_condition: str = Field("", max_length=200)
    coat_condition: str = Field("", max_length=200)
    health_notes: str = Field("", max_length=1000)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    image_data_url: Optional[str] = Field(None, max_length=2000000)
    mode: str = Field("vlm", max_length=20)


class PetProfileOut(BaseModel):
    id: int
    name: str
    species: str
    breed: str
    body_condition: str
    coat_condition: str
    health_notes: str
    confidence: float
    mode: str
    image_data_url: Optional[str] = None
    created_at: Optional[str] = None
