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
from remotion_engine.renderer import render_code_to_video, render_spec_to_video
from store import VideoStore
from themes import PLATFORMS, SAMPLE_SPECS, THEMES

# 初始化存储
STORE = VideoStore(config.STORE_DIR)
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
        "系统整合了两种基于 Remotion 4.x 的视频生成模式：\n"
        "1. 声明式 Spec 模式 (`create_video_from_spec`，推荐首选)：\n"
        "   - 输入 JSON 结构定义即可直接生成高水准商业级动画视频；\n"
        "   - 支持 8 大专业主题色彩（tech, cyberpunk, finance, minimal, business, education, lifestyle, gaming）；\n"
        "   - 支持全平台自适应画幅预设：youtube(16:9), tiktok/shorts(9:16), instagram_square(1:1)；\n"
        "   - 内置高质量动画组件：TitleScene(片头/标题)、BarChart(柱状图)、HorizontalBarChart(水平排行榜)、"
        "PieChart(饼图/圆环图)、LineChart(折线趋势图)、CodeBlock(代码高亮视窗与打字机)、"
        "TextOverlay(核心观点金句)、EndScreen(片尾关注与号召行动)；\n"
        "   - 内置丝滑转场过渡（Fade, Slide）。\n"
        "2. 自由式 React 代码模式 (`create_video_from_code`)：\n"
        "   - 允许大模型直接提供多文件 React/Remotion 源码（以字典形式传入 files）；\n"
        "   - 支持导入 remotion 核心 API（AbsoluteFill, spring, interpolate, Sequence, useCurrentFrame 等）；\n"
        "   - 自动编译渲染为高帧率 MP4 视频。\n\n"
        "【生成工作流与输出强制铁律】\n"
        "1. 当用户需要制作视频时，优先使用 `create_video_from_spec` 构建结构清晰的视频；如用户要求特定自定义动画或复杂组件，使用 `create_video_from_code`。\n"
        "2. 视频渲染完成后，接口将返回完整的 `video_url`（可直接在线播放）、`download_url`（下载地址）、`poster_url`（高清封面图）与精心排版的 `user_display_markdown`。\n"
        "3. **输出强制铁律**：在最终给用户的回复中，你【必须直接原样输出 user_display_markdown】！"
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
async def create_video_from_spec(
    spec: dict[str, Any],
    name: str = "",
    timeout: int | None = None,
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
        timeout: 可选渲染超时秒数（留空则默认使用全局环境变量 RENDER_TIMEOUT，默认为 120 秒）

    Returns:
        JSON 格式渲染结果，包含视频 URL、封面图 URL 与 Markdown 展示排版
    """
    item_id = STORE.new_id("vid_spec")
    title = str(spec.get("title") or name or "Remotion Video").strip()

    render_res = await render_spec_to_video(
        spec=spec,
        item_id=item_id,
        output_dir=OUTPUT_DIR,
        timeout=timeout,
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
    timeout: int | None = None,
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
        timeout: 可选渲染超时秒数（留空则默认使用全局环境变量 RENDER_TIMEOUT，默认为 120 秒）

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
        timeout=timeout,
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
    }
    if topic in topic_map:
        return topic_map[topic]

    return "\n\n---\n\n".join([
        rules.RULE_INDEX,
        rules.RULE_REACT_CODE,
        rules.RULE_REMOTION_ANIMATIONS,
        rules.RULE_REMOTION_TIMING,
        rules.RULE_REMOTION_SEQUENCING,
    ])
