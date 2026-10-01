# -*- coding: utf-8 -*-
"""全局配置与路径管理"""
import os
from pathlib import Path

# 服务监听端口，默认 48001（避开 48000 端口）
PORT = int(os.environ.get("PORT", "48001"))

# 外部公开 Base URL（若留空则自动从每次 HTTP 请求头识别）
BASE_URL = os.environ.get("BASE_URL", "").strip().rstrip("/")

# 访问鉴权密钥。留空免密放行；非空时 /mcp 与管理后台强制开启鉴权
AUTH_KEY = os.environ.get("AUTH_KEY", "").strip()

# 工作目录与持久化存储路径
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = os.environ.get("REMOTION_WORKSPACE", str(BASE_DIR / "data"))
OUTPUT_DIR = os.environ.get("REMOTION_OUTPUT_DIR", os.path.join(WORKSPACE, "output"))
STORE_DIR = os.environ.get("REMOTION_STORE_DIR", os.path.join(WORKSPACE, "store"))
REMOTION_ENGINE_DIR = os.environ.get("REMOTION_ENGINE_DIR", str(BASE_DIR / "remotion_engine"))

# 确保持久化目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STORE_DIR, exist_ok=True)
