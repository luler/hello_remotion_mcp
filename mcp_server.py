# -*- coding: utf-8 -*-
"""Remotion Studio MCP 服务（基于 MCP Python SDK 的 MCPServer / FastMCP）。

提供两种利用 Remotion 制作视频的核心模式：
1. create_video_from_spec: 声明式场景设计系统模式（TitleScene, BarChart, CodeBlock, EndScreen等）
2. create_video_from_code: 自由式 React/Remotion 源码组件模式
3. 视频资产查询、管理与规则知识库
"""
from __future__ import annotations

import contextvars
import json
import os
import time
from typing import Any

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
    except ImportError:
        from mcp.server import FastMCP as MCPServer

try:
    from mcp.server.transport_security import TransportSecurityMiddleware, TransportSecuritySettings
    TransportSecurityMiddleware._validate_host = lambda self, host: True
    TransportSecurityMiddleware._validate_origin = lambda self, origin: True
    _transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=["*"],
        allowed_origins=["*"],
    )
except Exception:
    _transport_security = None

import config
import rules
import shotcraft_kb
import task_manager
from remotion_engine.renderer import render_code_to_video, render_spec_to_video
from store import VideoStore
from themes import PLATFORMS, SAMPLE_SPECS, THEMES

# 初始化存储与任务管理器
STORE = VideoStore(config.STORE_DIR)
TASKS = task_manager.TaskManager(config.STORE_DIR)
OUTPUT_DIR = config.OUTPUT_DIR

# 动态保存每次 HTTP 请求传入的真实 Host 基础路径
current_request_base_url: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_request_base_url", default=None
)
# 动态保存每次 HTTP 请求传入的真实 Client ID（支持 URL 参数、Header 与 MCP Session 自动注入）
current_request_client_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_request_client_id", default=None
)


def get_base_url() -> str:
    """获取当前服务外部可访问的 Base URL（自适应 Host 头、环境变量或端口兜底）。"""
    if config.BASE_URL:
        return config.BASE_URL.rstrip("/")
    ctx_base = current_request_base_url.get()
    if ctx_base:
        return ctx_base.rstrip("/")
    return f"http://127.0.0.1:{config.PORT}"


def resolve_client_id(explicit_client_id: str = "") -> str:
    """自动解析客户端唯一标识：优先使用显式参数，次之继承当前 HTTP 连接/Header 注入的客户端标识。"""
    if explicit_client_id and explicit_client_id.strip():
        return explicit_client_id.strip()
    ctx_cid = current_request_client_id.get() or ""
    return ctx_cid.strip()


_server_kwargs = {
    "name": "remotion-studio",
    "version": "0.3.0",
    "instructions": (
        "你是一个顶尖的视频导演与 Remotion 动效工程专家。\n\n"
        "【核心视频制作能力】\n"
        "系统整合了声明式 Spec 与自由式 React 两种视频生成模式，并全面支持同步即时渲染与异步任务队列：\n"
        "1. 异步任务模式（制作长视频/多镜头推荐首选，彻底杜绝网络超时与碎片化）：\n"
        "   - 当视频包含 3 个及以上镜头或预计时长较长时，必须优先使用 `submit_video_task_from_spec`（或 `submit_video_task_from_code`）；\n"
        "   - 接口在 50ms 内立即返回唯一任务 ID (`task_id`) 与预估耗时，完全不受客户端/反代 HTTP 60s/120s 超时限制；\n"
        "   - 提交后若未完成，调用 `get_video_task_status(task_id, wait_seconds=300)` 进行长轮询等待成片就地返回（极大减少 Token 往返消耗）；若客户端偶发网络断开重试，系统会根据上下文中的 task_id 智能无缝找回进度，绝不丢失；\n"
        "   - 渲染完成后直接获取视频卡片，严禁因为担心超时把一个完整主题拆分成 5~6 个碎片短视频！\n"
        "2. 声明式 Spec 模式 (`create_video_from_spec` / `submit_video_task_from_spec`)：\n"
        "   - 输入 JSON 结构定义即可直接生成高水准商业级动画视频；\n"
        "   - 支持 8 大专业主题色彩（tech, cyberpunk, finance, minimal, business, education, lifestyle, gaming）；\n"
        "   - 支持全平台自适应画幅预设：youtube(16:9), tiktok/shorts(9:16), instagram_square(1:1)；\n"
        "   - 内置高质量动画组件：TitleScene(片头/标题)、BrandInkOpen(电影级墨线十字准星开场)、MarkerUnderlineTitle(记号笔高亮标题)、"
        "BarChart(柱状图)、HorizontalBarChart(水平排行榜)、"
        "PieChart(饼图/圆环图)、LineChart(折线趋势图)、CodeBlock(代码高亮视窗与打字机)、"
        "TextOverlay(核心观点金句)、EndScreen(片尾关注与号召行动)、ComparisonCard(对比分析)、MetricCard(核心数据看板)、Timeline(里程碑时间轴)；\n"
        "   - 内置丝滑转场过渡（Fade, Slide）。\n"
        "3. 自由式 React 代码模式 (`create_video_from_code` / `submit_video_task_from_code`)：\n"
        "   - 允许大模型直接提供多文件 React/Remotion 源码（以字典形式传入 files）；\n"
        "   - 支持导入 remotion 核心 API（AbsoluteFill, spring, interpolate, Sequence, useCurrentFrame 等）；\n"
        "   - 自动编译渲染为高帧率 MP4 视频。\n"
        "4. 电影感镜头配方卡知识库 (Video-Shotcraft，157张镜头卡与214个动效组件)：\n"
        "   - 提供片头(opening), 2.5D运镜(camera), UI动效(ui-entrance), 交互演示(interaction), 数据高亮(data), 高级字效(typography), 光效质感(effects), 节奏停顿(rhythm), 转场(transition), 片尾(outro)等10大分类；\n"
        "   - 可随时调用 `list_shotcraft_categories`, `search_shotcraft_shots`, `get_shotcraft_recipe` 检索电影感参数与动效拆解。\n\n"
        "【视频制作防超时闭环与任务互斥铁律】\n"
        "1. 智能等待与长轮询（最大化节约 Token）：\n"
        "   - 提交任务后，客户端使用 `get_video_task_status(task_id, wait_seconds=300)` 进行长轮询等待；\n"
        "   - 后台渲染完成瞬间会立即在本次调用中返回最终成片卡片，免去多轮无效轮询问答，节约 90% 以上 Token；\n"
        "   - 若因网络闪断或客户端硬超时导致重连，大模型只需凭借上下文中的 `task_id`（或留空自动推断）即可无缝恢复进度查询，绝对不会出现任务丢失或找不到；\n"
        "2. 任务互斥与放弃/取消逻辑（闭环控制）：\n"
        "   - 系统限制同一时间只有一个活跃渲染任务。若用户在任务进行中又发起了新视频需求：\n"
        "     * 系统会自动拦截并明确提示：当前已有视频任务【标题】（Task ID: ...）正在进行中；\n"
        "     * 若用户明确表示不想做上一个视频了或想换题目，大模型必须先调用 `cancel_video_task()` 终止上一任务并释放算力，然后再发起新视频制作！\n"
        "     * 若用户坚持强制覆盖，也可在提交工具时传入 `force=True` 强制终止旧任务。\n"
        "3. 中断重连与状态找回：\n"
        "   - 若网络闪断、客户端超时，或用户后续询问‘做好了吗’、‘视频进度如何’：\n"
        "     * 优先通过 `get_video_task_status(task_id)` 查询已知任务；\n"
        "     * 若未提供任务 ID，调用 `get_video_task_status()`（留空自动查最新）获取进度；\n"
        "     * 若已完成直接输出 `user_display_markdown` 视频卡片；若仍在渲染中则汇报进度与耗时，严禁在未确认后台状态前盲目重新发起渲染！\n"
        "4. 严禁碎剪：遇到篇幅较长的科普、汇报、政策解读或商业方案，必须作为一个完整视频合成，绝不可拆成碎片！\n"
        "5. 最终回复强制铁律：在最终给用户的回复中，你【必须直接原样输出 user_display_markdown】！"
        "必须确保封面图通过 `![封面](poster_url)` 渲染大图展示，并展示在线播放与下载的超链接，绝对严禁折叠或擅自省略图片与链接！"
    ),
}

if _transport_security is not None:
    _server_kwargs["transport_security"] = _transport_security

try:
    server = MCPServer(**_server_kwargs)
except TypeError:
    _server_kwargs.pop("transport_security", None)
    server = MCPServer(**_server_kwargs)

if _transport_security is not None:
    if hasattr(server, "settings") and hasattr(server.settings, "transport_security"):
        server.settings.transport_security = _transport_security


# ==================== 核心视频制作与任务管理工具 ====================

@server.tool()
async def cancel_video_task(
    task_id: str = "",
    reason: str = "",
    client_id: str = "",
) -> str:
    """终止并取消正在进行中的视频制作任务，释放底层 Chromium 与 FFmpeg 渲染算力。

    当用户不想继续制作当前视频、或者想切换题目重新制作时，调用此工具结束上一个任务。

    Args:
        task_id: 待取消的任务 ID (如 task_spec_...)，若留空则自动取消当前客户端（或系统）正在运行的活跃任务
        reason: 取消原因说明（可选）
        client_id: 客户端唯一标识符（可选，用于多客户端环境精准识别）

    Returns:
        JSON 格式取消执行结果
    """
    cid = resolve_client_id(client_id)
    res = TASKS.cancel_task(task_id=task_id, reason=reason, client_id=cid)
    if not res.get("ok") and task_id and not (client_id and client_id.strip()):
        res = TASKS.cancel_task(task_id=task_id, reason=reason)
    return json.dumps(res, ensure_ascii=False, indent=2)


@server.tool()
async def submit_video_task_from_spec(
    spec: dict[str, Any],
    name: str = "",
    wait_seconds: float = 300.0,
    force: bool = False,
    timeout: int | None = None,
    client_id: str = "",
) -> str:
    """声明式 Spec 视频生成（长轮询就地返回成片或平滑转后台，支持多客户端隔离与并发互斥保护，最大支持渲染 30 分钟）。

    执行机制：
    1. 互斥保护与多客户端隔离：同一客户端若已有任务正在渲染且 force=False，系统会自动拦截并提醒用户；不同客户端（不同 client_id）互不影响；若 force=True 则直接终止旧任务。
    2. 智能等待与长轮询（默认 300 秒）：在此期间若渲染完成，直接在本次调用中返回最终成片与 Markdown 播放卡片（极大减少大模型往返 Token 消耗）；若超时未完则平滑返回 task_id，由客户端继续查询。

    Args:
        spec: 视频规格定义，必须包含 scenes 场景列表
        name: 可选文件名标识，留空则自动生成唯一 ID
        wait_seconds: 初始长轮询等待秒数（默认 300.0 秒就地等待成片；设为 0 则纯异步秒级返回 task_id）
        force: 若当前已有其他任务在渲染，是否强制终止旧任务并开启新任务（默认 False）
        timeout: 渲染总超时上限（秒，默认 1800 秒）
        client_id: 客户端唯一标识符（用于多客户端独立任务隔离）
    """
    cid = resolve_client_id(client_id)
    task = TASKS.create_spec_task(
        spec=spec,
        name=name,
        timeout=timeout,
        force=force,
        client_id=cid,
        output_dir=OUTPUT_DIR,
        render_fn=render_spec_to_video,
        register_fn=STORE.register,
        get_base_url_fn=get_base_url,
    )

    if task.get("conflict"):
        return json.dumps(task, ensure_ascii=False, indent=2)

    task_id = task["task_id"]

    # 若指定了就地等待（默认 35 秒，支持按需传入更长等待）
    safe_wait = max(0.0, float(wait_seconds))
    if safe_wait > 0:
        finished = await TASKS.wait_for_task(task_id, timeout=safe_wait)
        status = finished.get("status")
        if status == "completed":
            res = finished.get("result") or {}
            return json.dumps({
                "ok": True,
                "task_id": task_id,
                "status": "completed",
                "title": finished.get("title", ""),
                "render_time_seconds": finished.get("render_time_seconds", 0.0),
                "video_url": res.get("video_url", ""),
                "download_url": res.get("download_url", ""),
                "poster_url": res.get("poster_url", ""),
                "duration_seconds": res.get("duration_seconds", 0),
                "resolution": res.get("resolution", ""),
                "file_size_mb": res.get("file_size_mb", 0.0),
                "user_display_markdown": res.get("user_display_markdown", ""),
            }, ensure_ascii=False, indent=2)
        elif status == "failed":
            return json.dumps({
                "ok": False,
                "task_id": task_id,
                "status": "failed",
                "error": finished.get("error", "Unknown error"),
            }, ensure_ascii=False, indent=2)
        elif status == "cancelled":
            return json.dumps({
                "ok": False,
                "task_id": task_id,
                "status": "cancelled",
                "error": finished.get("error", "任务已被取消"),
            }, ensure_ascii=False, indent=2)

    # 超过 wait_seconds 仍未渲染完（属于长视频），在客户端超时前平滑交还 task_id
    cur_task = TASKS.get_task(task_id, client_id=cid) or task
    elapsed = cur_task.get("elapsed_seconds", 0.0)
    est = cur_task.get("estimated_render_seconds", 60.0)
    return json.dumps({
        "ok": True,
        "task_id": task_id,
        "title": cur_task.get("title", ""),
        "status": "rendering",
        "scenes_count": cur_task.get("scenes_count", 0),
        "estimated_duration_seconds": cur_task.get("estimated_duration_seconds", 0),
        "elapsed_seconds": elapsed,
        "estimated_render_seconds": est,
        "message": (
            f"视频正在后台全速渲染中（Task ID: {task_id}，已执行 {elapsed}s / 预估约 {est}s）。"
            f"为最大化节省大模型 Token 消耗，请稍候约 300 秒（5分钟）后再调用 get_video_task_status(task_id, wait_seconds=300) 查询一次（长等待期间若渲染完成会立即返回成片，请勿频繁轮询）；或直接告知用户正在后台渲染，等待用户再次提问时查询。"
        ),
    }, ensure_ascii=False, indent=2)


@server.tool()
async def submit_video_task_from_code(
    files: str | dict[str, str],
    title: str = "Custom Remotion Video",
    entry_file: str = "/src/Video.tsx",
    duration_in_frames: int = 150,
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    input_props: dict[str, Any] | None = None,
    wait_seconds: float = 300.0,
    force: bool = False,
    timeout: int | None = None,
    client_id: str = "",
) -> str:
    """React 源码模式视频生成（长轮询就地返回成片或平滑转后台，支持并发冲突拦截与多客户端隔离，最大支持渲染 30 分钟）。"""
    file_map: dict[str, str] = {}
    if isinstance(files, str):
        try:
            file_map = json.loads(files)
        except Exception as e:
            return json.dumps({"ok": False, "error": f"Invalid files JSON string: {e}"})
    elif isinstance(files, dict):
        file_map = files
    else:
        return json.dumps({"ok": False, "error": "files must be a dict or valid JSON string"})

    if not file_map:
        return json.dumps({"ok": False, "error": "files cannot be empty"})

    cid = resolve_client_id(client_id)
    task = TASKS.create_code_task(
        files=file_map,
        entry_file=entry_file,
        title=title,
        duration_in_frames=duration_in_frames,
        fps=fps,
        width=width,
        height=height,
        input_props=input_props,
        timeout=timeout,
        force=force,
        client_id=cid,
        output_dir=OUTPUT_DIR,
        render_fn=render_code_to_video,
        register_fn=STORE.register,
        get_base_url_fn=get_base_url,
    )

    if task.get("conflict"):
        return json.dumps(task, ensure_ascii=False, indent=2)

    task_id = task["task_id"]

    safe_wait = max(0.0, float(wait_seconds))
    if safe_wait > 0:
        finished = await TASKS.wait_for_task(task_id, timeout=safe_wait)
        status = finished.get("status")
        if status == "completed":
            res = finished.get("result") or {}
            return json.dumps({
                "ok": True,
                "task_id": task_id,
                "status": "completed",
                "title": finished.get("title", ""),
                "render_time_seconds": finished.get("render_time_seconds", 0.0),
                "video_url": res.get("video_url", ""),
                "download_url": res.get("download_url", ""),
                "poster_url": res.get("poster_url", ""),
                "duration_seconds": res.get("duration_seconds", 0),
                "resolution": res.get("resolution", ""),
                "file_size_mb": res.get("file_size_mb", 0.0),
                "user_display_markdown": res.get("user_display_markdown", ""),
            }, ensure_ascii=False, indent=2)
        elif status == "failed":
            return json.dumps({
                "ok": False,
                "task_id": task_id,
                "status": "failed",
                "error": finished.get("error", "Unknown error"),
            }, ensure_ascii=False, indent=2)
        elif status == "cancelled":
            return json.dumps({
                "ok": False,
                "task_id": task_id,
                "status": "cancelled",
                "error": finished.get("error", "任务已被取消"),
            }, ensure_ascii=False, indent=2)

    cur_task = TASKS.get_task(task_id, client_id=cid) or task
    elapsed = cur_task.get("elapsed_seconds", 0.0)
    est = cur_task.get("estimated_render_seconds", 60.0)
    return json.dumps({
        "ok": True,
        "task_id": task_id,
        "title": cur_task.get("title", ""),
        "status": "rendering",
        "elapsed_seconds": elapsed,
        "estimated_render_seconds": est,
        "message": (
            f"React 源码视频任务正在后台全速渲染中（Task ID: {task_id}，已执行 {elapsed}s / 预估约 {est}s）。"
            f"为最大化节省大模型 Token 消耗，请稍候约 300 秒（5分钟）后再调用 get_video_task_status(task_id, wait_seconds=300) 查询一次（长等待期间若渲染完成会立即返回成片，请勿频繁轮询）；或直接告知用户正在后台渲染，等待用户再次提问时查询。"
        ),
    }, ensure_ascii=False, indent=2)


@server.tool()
async def get_video_task_status(task_id: str = "", wait_seconds: float = 300.0, client_id: str = "") -> str:
    """根据任务 ID 查询视频渲染进度与最终生成结果。若留空 task_id 则自动从上下文推断最新任务。

    Args:
        task_id: 提交任务时返回的 task_id (如 task_spec_...)，留空则自动从会话上下文中匹配最新活跃任务
        wait_seconds: 长轮询等待秒数（默认 300 秒，在此期间一旦渲染完成会立即就地返回成片，极大减少大模型往返轮询产生的 Token 消耗；即便客户端发生网络超时重试，系统亦能通过上下文精准识别原任务）
        client_id: 客户端唯一标识符（可选，用于多客户端环境精准识别）

    Returns:
        JSON 格式任务状态。当 status 为 'completed' 时，包含完整视频 URL、封面图 URL 与 user_display_markdown。
    """
    cid = resolve_client_id(client_id)
    if not task_id:
        # 1. 优先根据客户端空间识别当前上下文的活跃任务
        active = TASKS.get_active_task(client_id=cid)
        if not active:
            # 2. 上下文智能兜底：若网络重连或未指明客户端，自动匹配当前会话最近的活跃任务
            active = TASKS.get_active_task()
        if active:
            task_id = active["task_id"]
        else:
            tasks = TASKS.list_tasks(limit=1, client_id=cid)
            if not tasks:
                tasks = TASKS.list_tasks(limit=1, all_clients=True)
            if not tasks:
                return json.dumps({"ok": False, "error": "当前没有正在执行或历史的视频渲染任务"}, ensure_ascii=False)
            task_id = tasks[0]["task_id"]

    wait_timeout = max(0.0, float(wait_seconds))
    if wait_timeout > 0:
        task = await TASKS.wait_for_task(task_id, timeout=wait_timeout)
    else:
        task = TASKS.get_task(task_id, client_id=cid)

    # 3. 上下文跨会话智能找回：若按特定 client_id 未命中，使用全局 task_id 兜底检索（持有唯一 task_id 证明来源上下文合法）
    if not task:
        task = TASKS.get_task(task_id)

    if not task:
        return json.dumps({"ok": False, "error": f"Task not found: {task_id}"}, ensure_ascii=False)

    # 4. 越权防御：仅当显式传入了互斥的 client_id 时才严格拦截；对持有合法随机 task_id 的会话上下文请求宽容放行
    if client_id and client_id.strip() and task.get("client_id") and task.get("client_id") != client_id.strip():
        return json.dumps({"ok": False, "error": f"越权操作拒绝：任务 {task_id} 属于其他客户端"}, ensure_ascii=False)

    status = task.get("status")
    if status == "completed":
        result = task.get("result") or {}
        return json.dumps({
            "ok": True,
            "task_id": task_id,
            "status": "completed",
            "title": task.get("title", ""),
            "render_time_seconds": task.get("render_time_seconds", 0.0),
            "video_url": result.get("video_url", ""),
            "download_url": result.get("download_url", ""),
            "poster_url": result.get("poster_url", ""),
            "duration_seconds": result.get("duration_seconds", 0),
            "resolution": result.get("resolution", ""),
            "file_size_mb": result.get("file_size_mb", 0.0),
            "user_display_markdown": result.get("user_display_markdown", ""),
        }, ensure_ascii=False, indent=2)

    elif status == "failed":
        return json.dumps({
            "ok": False,
            "task_id": task_id,
            "status": "failed",
            "error": task.get("error", "Unknown error"),
        }, ensure_ascii=False, indent=2)

    elif status == "cancelled":
        return json.dumps({
            "ok": False,
            "task_id": task_id,
            "status": "cancelled",
            "error": task.get("error", "任务已被取消"),
        }, ensure_ascii=False, indent=2)

    else:
        # queued or rendering
        elapsed = task.get("elapsed_seconds", 0.0)
        est = task.get("estimated_render_seconds", 30.0)
        pct = min(95, int((elapsed / max(est, 1.0)) * 90) + 10) if status == "rendering" else 5
        return json.dumps({
            "ok": True,
            "task_id": task_id,
            "status": status,
            "title": task.get("title", ""),
            "progress_percent": pct,
            "elapsed_seconds": elapsed,
            "estimated_render_seconds": est,
            "message": (
                f"任务正在后台全速渲染中 (已耗时 {elapsed}s / 预估约 {est}s，进度约 {pct}%)。"
                f"为节约大模型 Token 消耗，请至少间隔约 300 秒（5分钟）后再调用 get_video_task_status 查询，期间切勿高频调用；"
                f"或直接向用户汇报当前进度后，等待用户下一次主动提问时再查。"
            ),
        }, ensure_ascii=False, indent=2)


@server.tool()
async def list_video_tasks(limit: int = 5, client_id: str = "") -> str:
    """获取最近提交的视频渲染任务列表及实时状态（支持严格多客户端隔离与断线重连）。

    本接口具有严格的客户端隔离机制：
    1. 自动根据 MCP 连接参数、HTTP Header 或显式 client_id 参数进行数据空间隔离；
    2. 任何客户端均只能查询到自身名下的视频任务，绝不会泄漏或看到其他客户端制作的视频。

    Args:
        limit: 返回条数（默认 5）
        client_id: 客户端唯一标识符（可选，留空时系统自动按当前连接通道/会话自动识别）

    Returns:
        JSON 格式任务列表，包含各任务的 task_id、标题、状态(queued/rendering/completed/failed/cancelled)、已耗时、成片链接
    """
    cid = resolve_client_id(client_id)
    tasks = TASKS.list_tasks(limit=limit, client_id=cid)
    res = []
    for t in tasks:
        item = {
            "task_id": t.get("task_id"),
            "client_id": t.get("client_id", ""),
            "title": t.get("title"),
            "mode": t.get("mode"),
            "status": t.get("status"),
            "created_at": t.get("created_at"),
            "elapsed_seconds": t.get("elapsed_seconds", 0.0),
            "estimated_render_seconds": t.get("estimated_render_seconds", 30.0),
        }
        if t.get("status") == "completed" and t.get("result"):
            item["video_url"] = t["result"].get("video_url")
            item["poster_url"] = t["result"].get("poster_url")
            item["duration_seconds"] = t["result"].get("duration_seconds")
        elif t.get("status") in ("failed", "cancelled"):
            item["error"] = t.get("error")
        res.append(item)

    return json.dumps({
        "ok": True,
        "total": len(res),
        "tasks": res,
    }, ensure_ascii=False, indent=2)


@server.tool()
async def create_video_from_spec(
    spec: dict[str, Any],
    name: str = "",
    wait_seconds: float = 300.0,
    client_id: str = "",
) -> str:
    """依据声明式 JSON Spec 一键构建并渲染视频（支持就地返回成片与后台长轮询，最大支持渲染 30 分钟）。

    Args:
        spec: 视频规格定义，必须包含 scenes 场景列表
        name: 可选文件名标识，留空则自动生成唯一 ID
        wait_seconds: 长轮询等待秒数（默认 300 秒，在此期间一旦渲染完成会立即就地返回成片，极大减少大模型 Token 消耗）
        client_id: 客户端唯一标识符（可选，用于多客户端环境隔离）

    Returns:
        JSON 格式渲染结果或任务状态。
    """
    return await submit_video_task_from_spec(
        spec=spec,
        name=name,
        wait_seconds=wait_seconds,
        force=False,
        client_id=client_id,
    )


@server.tool()
async def create_video_from_code(
    files: str | dict[str, str],
    title: str = "Custom Remotion Video",
    entry_file: str = "/src/Video.tsx",
    duration_in_frames: int = 150,
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    input_props: dict[str, Any] | None = None,
    wait_seconds: float = 300.0,
    client_id: str = "",
) -> str:
    """使用原生 React / Remotion 源码多文件字典构建并渲染视频（支持就地返回成片与后台长轮询，最大支持渲染 30 分钟）。

    Args:
        files: React 源码文件字典（例如 {"/src/Video.tsx": "..."}）
        title: 视频标题
        entry_file: 入口文件路径（默认 /src/Video.tsx）
        duration_in_frames: 视频总帧数（默认 150 帧）
        fps: 视频帧率（默认 30）
        width: 视频宽度像素（默认 1920）
        height: 视频高度像素（默认 1080）
        input_props: 传入组件的自定义属性字典（可选）
        wait_seconds: 长轮询等待秒数（默认 300 秒，在此期间渲染完成立即就地返回成片）
        client_id: 客户端唯一标识符（可选，用于多客户端环境隔离）

    Returns:
        JSON 格式渲染结果或任务状态。
    """
    return await submit_video_task_from_code(
        files=files,
        title=title,
        entry_file=entry_file,
        duration_in_frames=duration_in_frames,
        fps=fps,
        width=width,
        height=height,
        input_props=input_props,
        wait_seconds=wait_seconds,
        force=False,
        client_id=client_id,
    )



@server.tool()
async def get_video_guide() -> str:
    """获取视频创作设计系统总览：包含 8 大内置主题配色、全平台画幅比例、场景组件与最佳实践。"""
    return json.dumps({
        "themes": THEMES,
        "platforms": PLATFORMS,
        "sample_specs": SAMPLE_SPECS,
        "available_components": [
            {
                "type": "TitleScene",
                "desc": "片头震撼标题与副标题",
                "props": ["title", "subtitle", "badge", "variant", "animation", "duration"],
            },
            {
                "type": "BarChart",
                "desc": "平滑升起的竖向数据柱状图",
                "props": ["title", "data: [{label, value}]", "duration"],
            },
            {
                "type": "HorizontalBarChart",
                "desc": "横向排行与进度对比图（支持移动端/竖屏）",
                "props": ["title", "data: [{label, value}]", "duration"],
            },
            {
                "type": "PieChart",
                "desc": "圆环/饼图及占比总计看板",
                "props": ["title", "data: [{label, value}]", "duration"],
            },
            {
                "type": "LineChart",
                "desc": "高质感平滑折线走势图与光效节点",
                "props": ["title", "data: [{label, value}]", "duration"],
            },
            {
                "type": "CodeBlock",
                "desc": "macOS 风格代码高亮窗口与打字机效果",
                "props": ["title", "filename", "code", "language", "isTyping", "duration"],
            },
            {
                "type": "TextOverlay",
                "desc": "核心金句、观点大字报或引言",
                "props": ["headline", "subheadline", "style", "duration"],
            },
            {
                "type": "EndScreen",
                "desc": "片尾号召关注、订阅呼吸按钮与社交卡片",
                "props": ["title", "channel", "cta", "social", "duration"],
            },
            {
                "type": "ComparisonCard",
                "desc": "双栏竞品/方案对比、VS卡片与优劣势要点清单",
                "props": ["title", "subtitle", "left: {title, subtitle, badge, items, isPositive}", "right: {title, subtitle, badge, items, isPositive}", "vsBadge", "duration"],
            },
            {
                "type": "MetricCard",
                "desc": "商业经营指标与 KPI 大数字滚动卡片看板（支持增减标识与说明）",
                "props": ["title", "subtitle", "metrics: [{label, value, prefix, suffix, change, changeLabel, isPositive, helperText}]", "duration"],
            },
            {
                "type": "Timeline",
                "desc": "里程碑时间轴演进图与霓虹发光节点路线图",
                "props": ["title", "subtitle", "items: [{date, title, description, badge, active}]", "duration"],
            },
            {
                "type": "FeatureList",
                "desc": "产品核心功能矩阵卡片与矢量图标徽章展示",
                "props": ["title", "subtitle", "columns", "features: [{title, description, badge, icon}]", "duration"],
            },
            {
                "type": "QuoteCard",
                "desc": "权威引述、金句推荐与客户证言卡片",
                "props": ["quote", "author", "title", "avatar", "company", "duration"],
            },
            {
                "type": "BrandInkOpen",
                "desc": "电影感极简片头：墨线十字准星描画 + 逐字 letterpress 压印 + 打字机副标",
                "props": ["wordmark (或 title)", "kicker (或 subtitle)", "accent", "duration"],
            },
            {
                "type": "MarkerUnderlineTitle",
                "desc": "记号笔下划线涂抹大标题：动态手绘马克笔质感下划线与标题弹入",
                "props": ["title", "highlight", "subtitle", "duration"],
            },
        ],
        "workflow_rules": rules.RULE_INDEX,
    }, ensure_ascii=False, indent=2)


@server.tool()
async def get_themes_and_templates() -> str:
    """获取所有支持的主题列表与即开即用的示例视频模板 Spec。"""
    return json.dumps({
        "themes": THEMES,
        "platforms": PLATFORMS,
        "templates": SAMPLE_SPECS,
    }, ensure_ascii=False, indent=2)


@server.tool()
async def get_video_info(video_id: str) -> str:
    """根据视频唯一 ID 获取特定视频的播放与下载信息（仅支持根据明确 ID 精准查询，杜绝遍历与历史资产泄漏）。

    Args:
        video_id: 当前对话或任务中已生成的视频 ID (如 vid_spec_... 或 vid_code_...)
    """
    if not video_id:
        return json.dumps({"ok": False, "error": "video_id is required"}, ensure_ascii=False)

    rec = STORE.get(video_id)
    if not rec:
        return json.dumps({"ok": False, "error": f"Video not found: {video_id}"}, ensure_ascii=False)

    base = get_base_url()
    return json.dumps({
        "ok": True,
        "id": rec["id"],
        "title": rec.get("title", ""),
        "mode": rec.get("mode", ""),
        "video_url": f"{base}/api/video/{rec['id']}.mp4",
        "download_url": f"{base}/api/download/{rec['id']}.mp4",
        "poster_url": f"{base}/api/poster/{rec['id']}.jpg" if rec.get("poster_path") else "",
        "duration_seconds": rec.get("duration_seconds", 0),
        "duration_frames": rec.get("duration_frames", 0),
        "fps": rec.get("fps", 30),
        "resolution": f"{rec.get('width', 1920)}x{rec.get('height', 1080)}",
        "size_mb": round(rec.get("bytes", 0) / (1024 * 1024), 2),
        "render_time_seconds": rec.get("render_time_seconds", 0.0),
        "created_at": rec.get("created_at", ""),
    }, ensure_ascii=False, indent=2)


# ==================== Remotion 规则与编码指南工具 ====================

@server.tool()
async def get_coding_rules(topic: str = "all") -> str:
    """获取 Remotion 动效编写核心规范与代码指南。

    Args:
        topic: 规则主题，可选值:
               - "all": 获取全部核心规范总览
               - "react": React 多文件项目结构与代码规范
               - "animations": useCurrentFrame 纯数学帧映射核心原理
               - "timing": spring 弹簧阻尼与 interpolate 缓动时序设计
               - "sequencing": Sequence 分幕编排与局部时间轴设计
               - "transitions": Fade, Slide, Wipe 等平滑转场指南
               - "text": 打字机字效与流光字效
               - "trimming": 素材前后端裁剪技巧
    """
    topic = (topic or "").strip().lower()
    topic_map = {
        "react": rules.RULE_REACT_CODE,
        "animations": rules.RULE_REMOTION_ANIMATIONS,
        "timing": rules.RULE_REMOTION_TIMING,
        "sequencing": rules.RULE_REMOTION_SEQUENCING,
        "transitions": rules.RULE_REMOTION_TRANSITIONS,
        "text": rules.RULE_REMOTION_TEXT_ANIMATIONS,
        "trimming": rules.RULE_REMOTION_TRIMMING,
        "shotcraft": rules.RULE_SHOTCRAFT_CINEMATIC,
        "cinematic": rules.RULE_SHOTCRAFT_CINEMATIC,
    }
    if topic in topic_map:
        return topic_map[topic]

    return "\n\n---\n\n".join([
        rules.RULE_INDEX,
        rules.RULE_REACT_CODE,
        rules.RULE_REMOTION_ANIMATIONS,
        rules.RULE_REMOTION_TIMING,
        rules.RULE_REMOTION_SEQUENCING,
        rules.RULE_SHOTCRAFT_CINEMATIC,
    ])


# ==================== Video-Shotcraft 镜头工坊工具 ====================

@server.tool()
async def list_shotcraft_categories() -> str:
    """获取 Video-Shotcraft 镜头配方库的 10 大分类体系（包含每个类别的镜头卡数量与设计意图）。

    包含类别：
    1. opening: 片头与品牌开场 (11款)
    2. camera: 2.5D运镜与视角 (10款)
    3. ui-entrance: 界面与卡片入场 (28款)
    4. interaction: 核心功能交互 (15款)
    5. data: 数据看板与亮点 (13款)
    6. typography: 字体动效与金句 (26款)
    7. effects: 光效与质感氛围 (17款)
    8. rhythm: 节奏控制与慢动作 (11款)
    9. transition: 转场与镜头交接 (19款)
    10. outro: 片尾与号召行动 (7款)
    """
    cats = shotcraft_kb.SHOT_INDEX.list_categories()
    return json.dumps({
        "ok": True,
        "total_cards": sum(c.get("count", 0) for c in cats),
        "categories": cats,
    }, ensure_ascii=False, indent=2)


@server.tool()
async def search_shotcraft_shots(query: str = "", category: str = "", limit: int = 20) -> str:
    """搜索与筛选 Video-Shotcraft 镜头配方卡（157张专业卡片与214个动效组件）。

    Args:
        query: 搜索关键词（如 "brand", "open", "counter", "card", "macbook", "glitch", "typography", "code", "hover" 等）
        category: 分类筛选（如 opening, camera, ui-entrance, interaction, data, typography, effects, rhythm, transition, outro）
        limit: 返回条数上限（默认 20 条）
    """
    if category:
        shots = shotcraft_kb.SHOT_INDEX.list_shots(category=category)
        if query:
            q = query.lower().strip()
            shots = [s for s in shots if q in s["name"].lower() or q in s["one_liner"].lower() or q in s["applicable"].lower()]
        results = shots[:limit]
    else:
        results = shotcraft_kb.SHOT_INDEX.search(query=query, limit=limit)

    return json.dumps({
        "ok": True,
        "count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2)


@server.tool()
async def get_shotcraft_recipe(shot_name: str) -> str:
    """获取指定电影感镜头配方的完整设计指南与实现规范。

    包含：
    - 一句话定义与适用场景 (energy, duration)
    - 意图与视觉心理学
    - 动效核心机制与拆解
    - 缓动曲线与参数表 (spring/interpolate parameters)
    - 声音设计规范 (对应音效与卡点)
    - 已知坑 (踩坑指南与避坑技巧)
    - TSX 参考实现组件位置

    Args:
        shot_name: 镜头卡名称或代号（如 "brand-ink-open", "marker-underline-title", "clip-card-looping", "split-flap-title" 等）
    """
    shot = shotcraft_kb.SHOT_INDEX.get_shot(shot_name)
    if not shot:
        return json.dumps({
            "ok": False,
            "error": f"Shot recipe not found: {shot_name}",
            "hint": "可使用 search_shotcraft_shots 工具搜索可用镜头名称",
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "ok": True,
        "recipe": shot,
    }, ensure_ascii=False, indent=2)

