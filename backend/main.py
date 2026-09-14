"""PetSight 后端入口：FastAPI 应用，挂载图片上传页面与档案接口。"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from service import db
from routers import vision, pets

app = FastAPI(title="PetSight · 宠物视觉建档助手", version="1.0.0")

# 本地调试时允许跨域（正式环境收紧为白名单）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    db.init()


app.include_router(vision.router)
app.include_router(pets.router)

# 托管前端上传页（纯静态，零构建即可运行）
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
