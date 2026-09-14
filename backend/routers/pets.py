"""宠物健康档案接口：建档 / 列表 / 详情 / 删除 / 导出。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas import PetProfileIn, PetProfileOut
from service import db

router = APIRouter(prefix="/api/pets", tags=["pets"])


@router.post("", response_model=PetProfileOut, status_code=201)
def create_profile(payload: PetProfileIn):
    pet_id = db.create_pet(payload.model_dump())
    return db.get_pet(pet_id)


@router.get("", response_model=list[PetProfileOut])
def list_profiles():
    return db.list_pets()


@router.get("/{pet_id}", response_model=PetProfileOut)
def get_profile(pet_id: int):
    pet = db.get_pet(pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="档案不存在")
    return pet


@router.delete("/{pet_id}")
def delete_profile(pet_id: int):
    ok = db.delete_pet(pet_id)
    if not ok:
        raise HTTPException(status_code=404, detail="档案不存在")
    return {"deleted": pet_id}


@router.get("/export/json")
def export():
    return db.export_json()
