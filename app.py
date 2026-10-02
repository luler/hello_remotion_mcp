# -*- coding: utf-8 -*-
"""FastAPI 应用：同时提供 Remotion MCP（Streamable HTTP）、REST 接口与资产管理后台。

运行：
    uvicorn app:app --host 0.0.0.0 --port 48001
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import time
from urllib.parse import parse_qs

import anyio
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

import config
import mcp_server as M
import rules
from remotion_engine.renderer import render_code_to_video, render_spec_to_video
from themes import PLATFORMS, SAMPLE_SPECS, THEMES
from web_admin import get_admin_html


def check_auth(authorization: str | None = None, auth_key: str | None = None) -> bool:
    """若配置了 AUTH_KEY，验证 Authorization 请求头或 URL Query 参数 auth_key。"""
    if not config.AUTH_KEY:
        return True

    if authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == config.AUTH_KEY:
            return True
        elif len(parts) == 1 and parts[0] == config.AUTH_KEY:
            return True

    if auth_key and auth_key == config.AUTH_KEY:
        return True

    return False


class VerifyIn(BaseModel):
    key: str = ""


class BatchDeleteIn(BaseModel):
    ids: list[str] = Field(default_factory=list, description="待删除的视频 ID 列表")


class RenderSpecIn(BaseModel):
    spec: dict = Field(..., description="视频 Spec 结构")
    name: str = ""
    timeout: int | None = Field(None, description="渲染超时秒数（可选，留空则使用全局 RENDER_TIMEOUT 环境变量）")


class RenderCodeIn(BaseModel):
    files: dict = Field(..., description="React 源码多文件字典")
    entry_file: str = "/src/Video.tsx"
    title: str = "Custom Video"
    duration_in_frames: int = 150
    fps: int = 30
    width: int = 1920
    height: int = 1080
    input_props: dict | None = None
    timeout: int | None = Field(None, description="渲染超时秒数（可选，留空则使用全局 RENDER_TIMEOUT 环境变量）")



@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # streamable_http_app() 会惰性建立 session_manager，必须在启动前通过 run() 保持
    async with M.server.session_manager.run():
        yield


app = FastAPI(
    title="remotion-studio",
    description="Remotion 视频生成与资产管理服务：FastAPI + MCP",
    version="0.3.0",
    lifespan=lifespan,
)


class BaseUrlMiddleware:
    """ASGI 中间件：
    1. 提取真实 Host 与协议，注入上下文供 URL 动态拼接；
    2. 解决客户端请求 /mcp 时被 Starlette 307 重定向的问题；
    3. 若配置了 AUTH_KEY，拦截并验证 /mcp 端点的 Bearer 授权请求头。
    """
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            method = scope.get("method", "GET").upper()

            if path == "/mcp":
                path = "/mcp/"
                scope["path"] = "/mcp/"

            headers_list = scope.get("headers", [])
            headers = dict(headers_list)
            x_proto = headers.get(b"x-forwarded-proto", b"").decode("latin-1")
            proto = x_proto or scope.get("scheme", "http")
            x_host = headers.get(b"x-forwarded-host", b"").decode("latin-1")
            host_header = headers.get(b"host", b"").decode("latin-1")
            host = x_host or host_header or ""
            if host:
                M.current_request_base_url.set(f"{proto}://{host}")

            if config.AUTH_KEY and (path == "/mcp" or path.startswith("/mcp/")):
                if method != "OPTIONS":
                    auth_header = headers.get(b"authorization", b"").decode("latin-1").strip()
                    authorized = False
                    if auth_header:
                        parts = auth_header.split()
                        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == config.AUTH_KEY:
                            authorized = True
                        elif len(parts) == 1 and parts[0] == config.AUTH_KEY:
                            authorized = True

                    if not authorized:
                        query_str = scope.get("query_string", b"").decode("latin-1")
                        qs = parse_qs(query_str)
                        if qs.get("auth_key", [None])[0] == config.AUTH_KEY or qs.get("token", [None])[0] == config.AUTH_KEY:
                            authorized = True

                    if not authorized:
                        body = b'{"error": "Unauthorized: missing or invalid Bearer token"}\n'
                        await send({
                            "type": "http.response.start",
                            "status": 401,
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode("ascii")),
                                (b"www-authenticate", b'Bearer realm="remotion-studio"'),
                                (b"access-control-allow-origin", b"*"),
                            ],
                        })
                        await send({
                            "type": "http.response.body",
                            "body": body,
                        })
                        return

        await self.inner_app(scope, receive, send)


app.add_middleware(BaseUrlMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 MCP 端点
_mcp_app = M.server.streamable_http_app(streamable_http_path="/")
app.mount("/mcp", _mcp_app)


# ==================== 管理后台前端页面 ====================

@app.get("/admin", response_class=HTMLResponse)
@app.get("/manage", response_class=HTMLResponse)
def admin_page():
    """现代化 Remotion 视频资产在线管理后台 (SPA)。"""
    return HTMLResponse(get_admin_html())


# ==================== 管理后台 API 接口 ====================

@app.post("/api/admin/verify")
def api_admin_verify(
    payload: VerifyIn | None = None,
    authorization: str | None = Header(None),
):
    """校验管理员访问凭证。"""
    if not config.AUTH_KEY:
        return {"ok": True, "auth_required": False}

    candidate = (payload.key if payload else "") or ""
    if not candidate and authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            candidate = parts[1]
        elif len(parts) == 1:
            candidate = parts[0]

    if candidate == config.AUTH_KEY:
        return {"ok": True, "auth_required": True}
    raise HTTPException(status_code=401, detail="Invalid AUTH_KEY")


@app.get("/api/admin/files")
def api_admin_files(
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
    search: str = Query("", description="搜索关键词"),
    page: int = Query(1, ge=1, description="当前页码（从 1 开始）"),
    page_size: int = Query(12, ge=0, le=500, description="每页显示数量，0 表示获取全部"),
):
    """获取已生成的视频资产列表（支持分页与关键词检索，严格按生成时间倒序）。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    import math

    limit = page_size if page_size > 0 else 0
    offset = (page - 1) * page_size if page_size > 0 else 0

    items, total = M.STORE.list(search=search, limit=limit, offset=offset)
    base = M.get_base_url()

    results = []
    for it in items:
        vid = it["id"]
        b = it.get("bytes", 0)
        results.append({
            "id": vid,
            "title": it.get("title", ""),
            "name": it.get("name", ""),
            "mode": it.get("mode", ""),
            "video_url": f"{base}/api/video/{vid}.mp4",
            "download_url": f"{base}/api/download/{vid}.mp4",
            "poster_url": f"{base}/api/poster/{vid}.jpg" if it.get("poster_path") else "",
            "duration_seconds": it.get("duration_seconds", 0),
            "duration_frames": it.get("duration_frames", 0),
            "fps": it.get("fps", 30),
            "resolution": f"{it.get('width', 1920)}x{it.get('height', 1080)}",
            "size_mb": round(b / (1024 * 1024), 2),
            "created_at": it.get("created_at", ""),
            "spec": it.get("spec"),
            "files": it.get("files"),
        })

    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    total_disk_bytes = M.STORE.total_bytes() if hasattr(M.STORE, "total_bytes") else 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(total_pages, 1),
        "total_disk_bytes": total_disk_bytes,
        "files": results,
    }


@app.get("/api/admin/ids")
def api_admin_ids(
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
    search: str = Query("", description="搜索关键词"),
):
    """获取所有匹配条件的视频 ID 列表（用于全选所有视频进行跨页批量操作）。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    ids = M.STORE.list_ids(search=search)
    return {"total": len(ids), "ids": ids}


@app.post("/api/admin/delete")
def api_admin_delete(
    payload: BatchDeleteIn,
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
):
    """批量彻底删除视频文件及关联封面图。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    deleted = 0
    for vid in payload.ids:
        rec = M.STORE.get(vid)
        if rec:
            if rec.get("path") and os.path.exists(rec["path"]):
                try:
                    os.remove(rec["path"])
                except OSError:
                    pass
            if rec.get("poster_path") and os.path.exists(rec["poster_path"]):
                try:
                    os.remove(rec["poster_path"])
                except OSError:
                    pass
            M.STORE.delete(rec["id"])
            deleted += 1
        else:
            # 容错直接按文件名删除
            cand_video = os.path.join(M.OUTPUT_DIR, f"{vid}.mp4" if not vid.endswith(".mp4") else vid)
            cand_poster = os.path.join(M.OUTPUT_DIR, f"{vid}.jpg" if not vid.endswith(".jpg") else vid)
            if os.path.exists(cand_video):
                try:
                    os.remove(cand_video)
                except OSError:
                    pass
            if os.path.exists(cand_poster):
                try:
                    os.remove(cand_poster)
                except OSError:
                    pass
            M.STORE.delete(vid)
            deleted += 1

    return {"ok": True, "deleted_count": deleted}


# ==================== 视频点播流与下载接口 ====================

def _resolve_video_record(item_id: str):
    raw_id = item_id
    for suffix in [".mp4", ".mov", ".webm"]:
        if raw_id.endswith(suffix):
            raw_id = raw_id[:-len(suffix)]
            break

    rec = M.STORE.get(raw_id)
    if rec and rec.get("path") and os.path.exists(rec["path"]):
        return rec, rec["path"], rec.get("title", raw_id)

    cand = os.path.join(M.OUTPUT_DIR, f"{raw_id}.mp4")
    if os.path.exists(cand):
        return rec, cand, raw_id

    cand2 = os.path.join(M.OUTPUT_DIR, item_id)
    if os.path.exists(cand2):
        return rec, cand2, raw_id

    return None, None, None


@app.api_route("/api/video/{item_id:path}", methods=["GET", "HEAD"])
async def api_stream_video(
    item_id: str,
    request: Request,
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
):
    """在线流式播放视频（完整支持 HTTP 206 Range 分段加载与平滑拖动寻道，兼容 HEAD 预检）。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    rec, path, title = _resolve_video_record(item_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found")

    file_size = os.path.getsize(path)

    if request.method == "HEAD":
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
        }
        return Response(status_code=200, headers=headers)

    range_header = request.headers.get("range")
    if not range_header:
        return FileResponse(path, media_type="video/mp4")

    # 处理 HTTP Range 分段请求
    try:
        byte_range = range_header.strip().replace("bytes=", "").split("-")
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
        end = min(end, file_size - 1)
        chunk_size = (end - start) + 1

        async def iter_chunk():
            async with await anyio.open_file(path, "rb") as f:
                await f.seek(start)
                bytes_left = chunk_size
                while bytes_left > 0:
                    read_len = min(65536, bytes_left)
                    data = await f.read(read_len)
                    if not data:
                        break
                    bytes_left -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iter_chunk(), status_code=206, headers=headers)
    except Exception:
        return FileResponse(path, media_type="video/mp4")


@app.api_route("/api/download/{item_id:path}", methods=["GET", "HEAD"])
def api_download_video(
    item_id: str,
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
):
    """强制附件下载 MP4 高清视频文件。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    rec, path, title = _resolve_video_record(item_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found")

    fname = f"{title}.mp4" if not title.endswith(".mp4") else title
    return FileResponse(path, filename=fname, media_type="application/octet-stream")


@app.api_route("/api/poster/{item_id:path}", methods=["GET", "HEAD"])
def api_get_poster(
    item_id: str,
    authorization: str | None = Header(None),
    auth_key: str | None = Query(None),
):
    """获取视频对应的高清封面图。"""
    if config.AUTH_KEY and not check_auth(authorization=authorization, auth_key=auth_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    raw_id = item_id
    for suffix in [".jpg", ".jpeg", ".png", ".mp4"]:
        if raw_id.endswith(suffix):
            raw_id = raw_id[:-len(suffix)]
            break

    rec = M.STORE.get(raw_id)
    if rec and rec.get("poster_path") and os.path.exists(rec["poster_path"]):
        return FileResponse(rec["poster_path"], media_type="image/jpeg")

    cand = os.path.join(M.OUTPUT_DIR, f"{raw_id}.jpg")
    if os.path.exists(cand):
        return FileResponse(cand, media_type="image/jpeg")

    raise HTTPException(status_code=404, detail="Poster not found")


# ==================== 渲染 REST 端点 ====================

@app.post("/api/render/spec")
async def api_render_spec(payload: RenderSpecIn):
    """REST API: 依据声明式 Spec 生成视频。"""
    item_id = M.STORE.new_id("vid_spec")
    title = payload.spec.get("title") or payload.name or "Remotion Video"

    res = await render_spec_to_video(
        spec=payload.spec,
        item_id=item_id,
        output_dir=M.OUTPUT_DIR,
        timeout=payload.timeout,
    )
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("error"))

    M.STORE.register(
        name=f"{item_id}.mp4",
        path=res["output_path"],
        title=title,
        mode="spec",
        poster_path=res.get("poster_path", ""),
        spec=payload.spec,
        item_id=item_id,
        duration_seconds=res["duration_seconds"],
        duration_frames=res["duration_frames"],
        fps=res["fps"],
        width=res["width"],
        height=res["height"],
    )

    base = M.get_base_url()
    return {
        "ok": True,
        "video_id": item_id,
        "title": title,
        "video_url": f"{base}/api/video/{item_id}.mp4",
        "download_url": f"{base}/api/download/{item_id}.mp4",
        "poster_url": f"{base}/api/poster/{item_id}.jpg" if res.get("poster_path") else "",
        "duration_seconds": res["duration_seconds"],
        "resolution": f"{res['width']}x{res['height']}",
        "file_size_mb": res["file_size_mb"],
    }


@app.post("/api/render/code")
async def api_render_code(payload: RenderCodeIn):
    """REST API: 依据 React 源码多文件字典生成视频。"""
    item_id = M.STORE.new_id("vid_code")

    res = await render_code_to_video(
        files=payload.files,
        item_id=item_id,
        output_dir=M.OUTPUT_DIR,
        entry_file=payload.entry_file,
        title=payload.title,
        duration_in_frames=payload.duration_in_frames,
        fps=payload.fps,
        width=payload.width,
        height=payload.height,
        input_props=payload.input_props,
        timeout=payload.timeout,
    )
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("error"))

    M.STORE.register(
        name=f"{item_id}.mp4",
        path=res["output_path"],
        title=payload.title,
        mode="code",
        poster_path=res.get("poster_path", ""),
        files=payload.files,
        item_id=item_id,
        duration_seconds=res["duration_seconds"],
        duration_frames=res["duration_frames"],
        fps=res["fps"],
        width=res["width"],
        height=res["height"],
    )

    base = M.get_base_url()
    return {
        "ok": True,
        "video_id": item_id,
        "title": payload.title,
        "video_url": f"{base}/api/video/{item_id}.mp4",
        "download_url": f"{base}/api/download/{item_id}.mp4",
        "poster_url": f"{base}/api/poster/{item_id}.jpg" if res.get("poster_path") else "",
        "duration_seconds": res["duration_seconds"],
        "resolution": f"{res['width']}x{res['height']}",
        "file_size_mb": res["file_size_mb"],
    }


# ==================== 资源与信息端点 ====================

@app.get("/api/themes")
def api_get_themes():
    return {"themes": THEMES, "platforms": PLATFORMS}


@app.get("/api/templates")
def api_get_templates():
    return {"templates": SAMPLE_SPECS}


@app.get("/api/rules")
def api_get_rules():
    return {
        "index": rules.RULE_INDEX,
        "react_code": rules.RULE_REACT_CODE,
        "animations": rules.RULE_REMOTION_ANIMATIONS,
        "timing": rules.RULE_REMOTION_TIMING,
        "sequencing": rules.RULE_REMOTION_SEQUENCING,
        "transitions": rules.RULE_REMOTION_TRANSITIONS,
        "text_animations": rules.RULE_REMOTION_TEXT_ANIMATIONS,
        "trimming": rules.RULE_REMOTION_TRIMMING,
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "remotion-studio", "time": time.time()}


@app.get("/")
def index():
    return {
        "service": "remotion-studio",
        "version": "0.3.0",
        "endpoints": {
            "mcp": "/mcp",
            "admin": "/admin",
            "docs": "/docs",
            "healthz": "/healthz",
        },
        "description": "基于 FastAPI + Remotion 4.x + MCP 的视频生成服务",
    }
