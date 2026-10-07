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


def get_base_url() -> str:
    """获取当前服务外部可访问的 Base URL（自适应 Host 头、环境变量或端口兜底）。"""
    if config.BASE_URL:
        return config.BASE_URL.rstrip("/")
    ctx_base = current_request_base_url.get()
    if ctx_base:
        return ctx_base.rstrip("/")
    return f"http://127.0.0.1:{config.PORT}"


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
        "   - 提交后每隔 30~60 秒调用 `get_video_task_status(task_id)` 查询一次；\n"
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
        "   - 提供片头(opening)、2.5D运镜(camera)、UI动效(ui-entrance)、交互演示(interaction)、数据高亮(data)、高级字效(typography)、光效质感(effects)、节奏停顿(rhythm)、转场(transition)、片尾(outro)等10大分类；\n"
        "   - 可随时调用 `list_shotcraft_categories`, `search_shotcraft_shots`, `get_shotcraft_recipe` 检索电影感参数与动效拆解。\n\n"
        "【长视频制作与输出强制铁律】\n"
        "1. 严禁碎剪：遇到篇幅较长的科普、汇报、政策解读或商业方案，必须作为一个完整视频合成（包含 5~10 个连续场景），通过异步任务 `submit_video_task_from_spec` 提交后轮询，绝不可拆成碎片！\n"
        "2. 最终回复强制铁律：在最终给用户的回复中，你【必须直接原样输出 user_display_markdown】！"
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


# ==================== 核心视频制作工具 ====================

@server.tool()
async def submit_video_task_from_spec(
    spec: dict[str, Any],
    name: str = "",
    timeout: int | None = None,
) -> str:
    """【长视频/多镜头首选】异步提交声明式 Spec 视频渲染任务，毫秒级返回 task_id，彻底规避 HTTP 超时。

    适合时长较长（>15秒）或包含多个场景镜头的视频生成。提交后每隔 30-60 秒调用 `get_video_task_status(task_id)` 查询进度即可。

    Args:
        spec: 视频规格定义，必须包含 scenes 场景列表。可选字段与 create_video_from_spec 一致。
        name: 可选文件名标识，留空则自动生成唯一 ID
        timeout: 可选超时时间（秒）

    Returns:
        JSON 格式的任务提交确认，包含 task_id、预估时间与轮询建议
    """
    task = TASKS.create_spec_task(
        spec=spec,
        name=name,
        timeout=timeout,
        output_dir=OUTPUT_DIR,
        render_fn=render_spec_to_video,
        register_fn=STORE.register,
        get_base_url_fn=get_base_url,
    )

    return json.dumps({
        "ok": True,
        "task_id": task["task_id"],
        "title": task["title"],
        "status": task["status"],
        "scenes_count": task["scenes_count"],
        "estimated_duration_seconds": task["estimated_duration_seconds"],
        "estimated_render_seconds": task["estimated_render_seconds"],
        "message": (
            f"视频任务已成功加入后台队列（Task ID: {task['task_id']}）。"
            f"本视频包含 {task['scenes_count']} 个场景镜头，预计成片时长 {task['estimated_duration_seconds']} 秒，预估渲染耗时约 {task['estimated_render_seconds']} 秒。"
            f"请告知用户正在后台渲染，并每隔 30~60 秒调用 get_video_task_status 查询任务进度。渲染完成后将直接获取完整视频卡片。"
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
    timeout: int | None = None,
) -> str:
    """【长视频/复杂组件首选】异步提交原生 React / Remotion 源码视频渲染任务，毫秒级返回 task_id。

    适合长时长源码或复杂 3D/粒子运算动画。提交后每隔 30-60 秒调用 `get_video_task_status(task_id)` 查询进度。

    Args:
        files: 源码文件映射字典或 JSON 字符串
        title: 视频标题
        entry_file: 入口文件路径，默认为 /src/Video.tsx
        duration_in_frames: 总时长帧数
        fps: 帧率，默认 30
        width: 视频宽度像素，默认 1920
        height: 视频高度像素，默认 1080
        input_props: 可选传递给入口组件的 React props 字典
        timeout: 可选超时时间（秒）
    """
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
        output_dir=OUTPUT_DIR,
        render_fn=render_code_to_video,
        register_fn=STORE.register,
        get_base_url_fn=get_base_url,
    )

    return json.dumps({
        "ok": True,
        "task_id": task["task_id"],
        "title": task["title"],
        "status": task["status"],
        "estimated_duration_seconds": task["estimated_duration_seconds"],
        "estimated_render_seconds": task["estimated_render_seconds"],
        "message": (
            f"React 源码视频任务已成功加入后台队列（Task ID: {task['task_id']}），预估渲染时间约 {task['estimated_render_seconds']} 秒。"
            f"请告知用户正在后台渲染，并每隔 30~60 秒调用 get_video_task_status 查询任务进度。"
        ),
    }, ensure_ascii=False, indent=2)


@server.tool()
async def get_video_task_status(task_id: str) -> str:
    """根据任务 ID 查询视频渲染进度与最终生成结果。

    Args:
        task_id: 提交任务时返回的 task_id (如 task_spec_...)

    Returns:
        JSON 格式任务状态。当 status 为 'completed' 时，包含完整视频 URL、封面图 URL 与 user_display_markdown。
    """
    if not task_id:
        return json.dumps({"ok": False, "error": "task_id is required"}, ensure_ascii=False)

    task = TASKS.get_task(task_id)
    if not task:
        return json.dumps({"ok": False, "error": f"Task not found: {task_id}"}, ensure_ascii=False)

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
            "message": f"任务正在渲染中 (已耗时 {elapsed}s / 预估约 {est}s，进度约 {pct}%)。请稍等 30~60 秒后再次调用 get_video_task_status 查询。",
        }, ensure_ascii=False, indent=2)


@server.tool()
async def create_video_from_spec(
    spec: dict[str, Any],
    name: str = "",
) -> str:
    """依据声明式 JSON Spec 一键构建并渲染专业级 Remotion 动画视频，自动返回视频播放链接与封面截图。

    Args:
        spec: 视频规格定义，必须包含 scenes 场景列表。可选字段：
              - title: 视频主标题
              - theme: 色彩主题 (tech, cyberpunk, finance, minimal, business, education, lifestyle, gaming)
              - platform: 平台画幅 (youtube: 1920x1080, tiktok: 1080x1920, instagram_square: 1080x1080)
              - fps: 帧率，默认 30
              - scenes: 场景数组，每个场景包含 type 与 duration (秒)，如：
                * TitleScene: title, subtitle, badge, variant(gradient/centered/left/bold), animation(fade_zoom/slide_up/typewriter/blur_in)
                * BarChart: title, data: [{"label": "...", "value": 12.5}]
                * HorizontalBarChart: title, data: [{"label": "...", "value": 85}]
                * PieChart / DonutChart: title, data: [{"label": "...", "value": 40}]
                * LineChart: title, data: [{"label": "...", "value": 100}]
                * CodeBlock: title, filename, code, language, isTyping(bool)
                * TextOverlay: headline, subheadline, style(badge/quote/minimal)
                * EndScreen: title, channel, cta, social: ["..."]
                * ComparisonCard: title, subtitle, left, right, vsBadge
                * MetricCard: title, subtitle, metrics
                * Timeline: title, subtitle, items
                * FeatureList: title, subtitle, columns, features
                * QuoteCard: quote, author, title, avatar
              - audioUrl / bgm: 可选背景音乐链接或路径
              - audioVolume: 背景音乐音量 (0.0 - 1.0, 默认 0.3)
              - transition: {"type": "fade" | "slide" | "none", "durationFrames": 12}
        name: 可选文件名标识，留空则自动生成唯一 ID

    Returns:
        JSON 格式渲染结果，包含视频 URL、封面图 URL 与 Markdown 展示排版
    """
    item_id = STORE.new_id("vid_spec")
    title = str(spec.get("title") or name or "Remotion Video").strip()

    render_res = await render_spec_to_video(
        spec=spec,
        item_id=item_id,
        output_dir=OUTPUT_DIR,
    )


    if not render_res.get("success"):
        return json.dumps({
            "ok": False,
            "error": render_res.get("error", "Unknown render error"),
        }, ensure_ascii=False)

    # 登记到资产仓库
    rec = STORE.register(
        name=f"{item_id}.mp4",
        path=render_res["output_path"],
        title=title,
        mode="spec",
        poster_path=render_res.get("poster_path", ""),
        spec=spec,
        item_id=item_id,
        duration_seconds=render_res["duration_seconds"],
        duration_frames=render_res["duration_frames"],
        fps=render_res["fps"],
        width=render_res["width"],
        height=render_res["height"],
        render_time_seconds=render_res.get("render_time_seconds", 0.0),
    )

    base = get_base_url()
    video_url = f"{base}/api/video/{item_id}.mp4"
    download_url = f"{base}/api/download/{item_id}.mp4"
    now_ts = int(time.time())
    poster_url = f"{base}/api/poster/{item_id}.jpg?t={now_ts}" if render_res.get("poster_path") else ""
    theme_name = spec.get("theme", "tech")

    poster_md = f"![{title} 封面预览]({poster_url})\n\n" if poster_url else ""
    markdown = (
        f"### 🎬 视频已成功生成：{title}\n\n"
        f"{poster_md}"
        f"- 📺 **在线播放视频**：[{title}]({video_url})\n"
        f"- 📥 **下载高清 MP4**：[点击下载视频文件]({download_url})\n"
        f"- ⏱️ **规格参数**：{render_res['duration_seconds']} 秒 | {render_res['width']}x{render_res['height']} | {render_res['fps']} FPS | {render_res['file_size_mb']} MB\n"
        f"- ⏳ **渲染总耗时**：{render_res.get('render_time_seconds', 0.0)} 秒\n"
        f"- 🎨 **制作模式**：声明式 Spec 模式 (主题: `{theme_name}`)\n"
    )

    return json.dumps({
        "ok": True,
        "video_id": item_id,
        "title": title,
        "video_url": video_url,
        "download_url": download_url,
        "poster_url": poster_url,
        "duration_seconds": render_res["duration_seconds"],
        "duration_frames": render_res["duration_frames"],
        "fps": render_res["fps"],
        "resolution": f"{render_res['width']}x{render_res['height']}",
        "file_size_mb": render_res["file_size_mb"],
        "render_time_seconds": render_res["render_time_seconds"],
        "user_display_markdown": markdown,
    }, ensure_ascii=False, indent=2)


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
) -> str:
    """使用原生 React / Remotion 源码多文件字典构建并渲染视频。

    Args:
        files: 源码文件映射字典或 JSON 字符串，例如：
               {"/src/Video.tsx": "import {AbsoluteFill} from 'remotion';\\nexport default function Video(){return <AbsoluteFill>Hello</AbsoluteFill>;}"}
        title: 视频标题
        entry_file: 入口文件路径，默认为 /src/Video.tsx
        duration_in_frames: 总时长帧数，默认 150 帧 (30fps 下为 5 秒)
        fps: 帧率，默认 30
        width: 视频宽度像素，默认 1920
        height: 视频高度像素，默认 1080
        input_props: 可选传递给入口组件的 React props 字典

    Returns:
        JSON 格式渲染结果，包含视频 URL、封面图 URL 与 Markdown 展示排版
    """
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

    item_id = STORE.new_id("vid_code")

    render_res = await render_code_to_video(
        files=file_map,
        item_id=item_id,
        output_dir=OUTPUT_DIR,
        entry_file=entry_file,
        title=title,
        duration_in_frames=duration_in_frames,
        fps=fps,
        width=width,
        height=height,
        input_props=input_props,
    )


    if not render_res.get("success"):
        return json.dumps({
            "ok": False,
            "error": render_res.get("error", "Unknown render error"),
        }, ensure_ascii=False)

    rec = STORE.register(
        name=f"{item_id}.mp4",
        path=render_res["output_path"],
        title=title,
        mode="code",
        poster_path=render_res.get("poster_path", ""),
        files=file_map,
        item_id=item_id,
        duration_seconds=render_res["duration_seconds"],
        duration_frames=render_res["duration_frames"],
        fps=render_res["fps"],
        width=render_res["width"],
        height=render_res["height"],
        render_time_seconds=render_res.get("render_time_seconds", 0.0),
    )

    base = get_base_url()
    video_url = f"{base}/api/video/{item_id}.mp4"
    download_url = f"{base}/api/download/{item_id}.mp4"
    now_ts = int(time.time())
    poster_url = f"{base}/api/poster/{item_id}.jpg?t={now_ts}" if render_res.get("poster_path") else ""

    poster_md = f"![{title} 封面预览]({poster_url})\n\n" if poster_url else ""
    markdown = (
        f"### 🎬 视频已成功生成：{title}\n\n"
        f"{poster_md}"
        f"- 📺 **在线播放视频**：[{title}]({video_url})\n"
        f"- 📥 **下载高清 MP4**：[点击下载视频文件]({download_url})\n"
        f"- ⏱️ **规格参数**：{render_res['duration_seconds']} 秒 | {render_res['width']}x{render_res['height']} | {render_res['fps']} FPS | {render_res['file_size_mb']} MB\n"
        f"- ⏳ **渲染总耗时**：{render_res.get('render_time_seconds', 0.0)} 秒\n"
        f"- 💻 **制作模式**：自由式 React 源码模式 ({len(file_map)} 个文件)\n"
    )

    return json.dumps({
        "ok": True,
        "video_id": item_id,
        "title": title,
        "video_url": video_url,
        "download_url": download_url,
        "poster_url": poster_url,
        "duration_seconds": render_res["duration_seconds"],
        "duration_frames": render_res["duration_frames"],
        "fps": render_res["fps"],
        "resolution": f"{render_res['width']}x{render_res['height']}",
        "file_size_mb": render_res["file_size_mb"],
        "render_time_seconds": render_res["render_time_seconds"],
        "user_display_markdown": markdown,
    }, ensure_ascii=False, indent=2)


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

