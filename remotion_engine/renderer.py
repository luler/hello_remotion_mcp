# -*- coding: utf-8 -*-
"""Remotion 渲染执行器：支持 Spec 声明式渲染与 React 源码渲染，自动生成视频与高清封面图。"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ENGINE_DIR = Path(__file__).resolve().parent
SRC_INDEX = ENGINE_DIR / "src" / "index.ts"
USER_SRC_DIR = ENGINE_DIR / "src" / "user"

DEFAULT_USER_VIDEO = '''import React from "react";
import { AbsoluteFill } from "remotion";

export const Video: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f172a",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        color: "#94a3b8",
        fontSize: 32,
        fontFamily: "sans-serif",
      }}
    >
      Remotion Studio Ready
    </AbsoluteFill>
  );
};

export default Video;
'''


def ensure_user_video_template() -> None:
    """确保运行时代码目录与默认入口组件存在，防止全新 clone 或缺失文件时 Webpack 编译失败。"""
    USER_SRC_DIR.mkdir(parents=True, exist_ok=True)
    video_file = USER_SRC_DIR / "Video.tsx"
    if not video_file.exists():
        video_file.write_text(DEFAULT_USER_VIDEO, encoding="utf-8")


ensure_user_video_template()



def get_npx_cmd() -> str:
    """自适应操作系统平台返回 npx 执行路径。"""
    if sys.platform == "win32":
        cmd = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
    else:
        cmd = shutil.which("npx") or "npx"
    return cmd


def get_ffmpeg_cmd() -> str:
    """自适应操作系统平台返回 ffmpeg 执行路径。"""
    if sys.platform == "win32":
        cmd = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg") or "ffmpeg"
    else:
        cmd = shutil.which("ffmpeg") or "ffmpeg"
    return cmd


_RENDER_SEMAPHORE: asyncio.Semaphore | None = None
_CODE_RENDER_LOCK: asyncio.Lock | None = None


def get_render_semaphore() -> asyncio.Semaphore:
    """获取并发渲染信号量（默认最大 2 个并发任务，防止多客户端并发导致 CPU/内存挤占）。"""
    global _RENDER_SEMAPHORE
    if _RENDER_SEMAPHORE is None:
        max_concurrent = int(os.environ.get("MAX_CONCURRENT_RENDERS", "2"))
        _RENDER_SEMAPHORE = asyncio.Semaphore(max_concurrent)
    return _RENDER_SEMAPHORE


def get_code_render_lock() -> asyncio.Lock:
    """获取源码模式编译运行互斥锁（保护 src/user 代码隔离）。"""
    global _CODE_RENDER_LOCK
    if _CODE_RENDER_LOCK is None:
        _CODE_RENDER_LOCK = asyncio.Lock()
    return _CODE_RENDER_LOCK


async def extract_poster(video_path: str, poster_path: str, time_offset: float = 1.0) -> bool:
    """使用 ffmpeg 极速截取视频的一帧作为高清封面图（纯异步非阻塞子进程）。"""
    if not os.path.exists(video_path):
        return False
    ffmpeg = get_ffmpeg_cmd()
    cmd = [
        ffmpeg,
        "-y",
        "-ss",
        str(max(0.2, time_offset)),
        "-i",
        video_path,
        "-vframes",
        "1",
        "-q:v",
        "2",
        poster_path,
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=20)
        return proc.returncode == 0 and os.path.exists(poster_path) and os.path.getsize(poster_path) > 0
    except Exception as e:
        logger.warning(f"Failed to extract poster with ffmpeg: {e}")
        return False


def get_render_timeout() -> int:
    """获取单个渲染任务超时秒数（优先读取环境变量 RENDER_TIMEOUT，默认 1800 秒/30分钟）。"""
    return int(os.environ.get("RENDER_TIMEOUT", "1800"))


def clean_partial_outputs(*paths: str | Path | None) -> None:
    """清理因渲染中断、超时或失败留下的残缺临时视频/封面文件。"""
    for p in paths:
        if not p:
            continue
        try:
            p_obj = Path(p)
            if p_obj.exists() and p_obj.is_file():
                p_obj.unlink()
        except OSError:
            pass


def clean_system_temp_cache(max_age_seconds: int = 1800) -> int:
    """清理系统 /tmp 下残留的旧 Remotion Webpack 缓存与 Chromium 临时目录。"""
    if sys.platform == "win32":
        return 0
    cleaned_count = 0
    tmp_dir = Path("/tmp")
    if not tmp_dir.exists():
        return 0
    now = time.time()
    patterns = ["remotion-webpack-bundle-*", "org.chromium.Chromium.*"]
    for pat in patterns:
        for p in tmp_dir.glob(pat):
            try:
                mtime = p.stat().st_mtime
                if now - mtime > max_age_seconds:
                    if p.is_dir():
                        shutil.rmtree(p, ignore_errors=True)
                    else:
                        p.unlink(missing_ok=True)
                    cleaned_count += 1
            except Exception:
                pass
    return cleaned_count


def _kill_proc_tree(proc: asyncio.subprocess.Process | None) -> None:
    """彻底终止进程树及其派生的所有 Chromium/FFmpeg/Node 子进程。"""
    if not proc or proc.returncode is not None:
        return
    try:
        if sys.platform != "win32":
            import signal
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                proc.kill()
        else:
            proc.kill()
    except Exception:
        pass


async def render_spec_to_video(
    spec: dict[str, Any],
    item_id: str,
    output_dir: str,
    timeout: int | None = None,
) -> dict[str, Any]:
    """依据声明式 JSON Spec 渲染 MP4 视频（受并发信号量平滑调控）。"""
    # 统一使用后台配置的最大渲染超时秒数（默认 1800 秒/30分钟），防止前端或 LLM 误传入过小数值导致频繁渲染中断
    effective_timeout = get_render_timeout()
    os.makedirs(output_dir, exist_ok=True)
    out_video = os.path.join(output_dir, f"{item_id}.mp4")
    out_poster = os.path.join(output_dir, f"{item_id}.jpg")

    # 计算预估尺寸与帧数
    fps = int(spec.get("fps") or 30)
    platform = str(spec.get("platform") or "youtube").lower()
    width = 1920
    height = 1080
    if platform in ("tiktok", "portrait", "shorts"):
        width, height = 1080, 1920
    elif platform in ("square", "instagram_square"):
        width, height = 1080, 1080
    elif platform in ("instagram_portrait", "post_4_5"):
        width, height = 1080, 1350
    elif platform in ("ultrawide", "21:9"):
        width, height = 2560, 1080
    elif platform in ("classic_4_3", "4:3"):
        width, height = 1440, 1080

    # 优先使用用户显式声明的自定义宽高像素
    if spec.get("width"):
        width = int(spec["width"])
    if spec.get("height"):
        height = int(spec["height"])

    scenes = spec.get("scenes") or []
    total_frames = 0
    if scenes:
        for s in scenes:
            dur = s.get("durationInFrames") or round((float(s.get("duration") or 3.5)) * fps)
            total_frames += int(dur)
    else:
        total_frames = 150

    total_frames = max(total_frames, 30)
    duration_seconds = round(total_frames / fps, 2)

    # 写入 props 临时文件
    props_data = {"spec": spec}
    temp_props_path = ENGINE_DIR / f"temp_props_{item_id}.json"
    with open(temp_props_path, "w", encoding="utf-8") as f:
        json.dump(props_data, f, ensure_ascii=False)

    npx = get_npx_cmd()
    gl_flag = "--gl=swangle" if sys.platform != "win32" else "--gl=angle"
    config_file = ENGINE_DIR / "remotion.config.ts"
    concurrency = os.environ.get("REMOTION_CONCURRENCY", "50%").strip() or "50%"
    x264_preset = os.environ.get("X264_PRESET", "superfast").strip() or "superfast"

    cmd = [
        npx,
        "remotion",
        "render",
        str(SRC_INDEX),
        "SpecVideo",
        out_video,
        f"--props={str(temp_props_path)}",
        f"--config={str(config_file)}",
        "--image-format=jpeg",
        "--jpeg-quality=85",
        "--bundle-cache",
        f"--x264-preset={x264_preset}",
        gl_flag,
        f"--concurrency={concurrency}",
    ]

    if sys.platform != "win32":
        cmd.append("--enable-multiprocess-on-linux")

    public_dir = os.environ.get("REMOTION_PUBLIC_DIR") or str(ENGINE_DIR / "public")
    if os.path.exists(public_dir):
        cmd.append(f"--public-dir={public_dir}")

    chromium_path = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if chromium_path and os.path.exists(chromium_path):
        cmd.append(f"--browser-executable={chromium_path}")

    start_time = time.time()
    sem = get_render_semaphore()
    proc: asyncio.subprocess.Process | None = None
    extra_kwargs: dict[str, Any] = {}
    if sys.platform != "win32":
        extra_kwargs["start_new_session"] = True

    try:
        async with sem:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(ENGINE_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **extra_kwargs,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
            elapsed = round(time.time() - start_time, 2)

            if proc.returncode != 0:
                clean_partial_outputs(out_video, out_poster)
                err_msg = stderr.decode("utf-8", errors="replace") or stdout.decode("utf-8", errors="replace")
                logger.error(f"Remotion render failed ({proc.returncode}): {err_msg}")
                return {
                    "success": False,
                    "error": f"Remotion render failed: {err_msg}",
                }

            # 异步提取封面图
            await extract_poster(out_video, out_poster, time_offset=min(1.0, duration_seconds * 0.2))

        file_size = os.path.getsize(out_video) if os.path.exists(out_video) else 0

        return {
            "success": True,
            "item_id": item_id,
            "output_path": out_video,
            "poster_path": out_poster if os.path.exists(out_poster) else "",
            "duration_seconds": duration_seconds,
            "duration_frames": total_frames,
            "fps": fps,
            "width": width,
            "height": height,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "render_time_seconds": elapsed,
        }
    except asyncio.TimeoutError:
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        return {"success": False, "error": f"Render timed out after {effective_timeout} seconds"}
    except (asyncio.CancelledError, KeyboardInterrupt):
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        raise
    except Exception as e:
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_props_path):
            try:
                os.remove(temp_props_path)
            except OSError:
                pass



async def render_code_to_video(
    files: dict[str, str],
    item_id: str,
    output_dir: str,
    entry_file: str = "/src/Video.tsx",
    title: str = "Custom Video",
    duration_in_frames: int = 150,
    fps: int = 30,
    width: int = 1920,
    height: int = 1080,
    input_props: dict[str, Any] | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    """依据用户提供的 React / Remotion 源码多文件字典渲染 MP4 视频（受并发信号量与代码隔离锁调控）。"""
    # 统一使用后台配置的最大渲染超时秒数（默认 600 秒），防止前端或 LLM 误传入过小数值导致频繁渲染中断
    effective_timeout = get_render_timeout()
    os.makedirs(output_dir, exist_ok=True)
    out_video = os.path.join(output_dir, f"{item_id}.mp4")
    out_poster = os.path.join(output_dir, f"{item_id}.jpg")

    duration_in_frames = max(int(duration_in_frames), 30)
    fps = max(int(fps), 1)
    duration_seconds = round(duration_in_frames / fps, 2)

    props_data = {
        "inputProps": {
            **(input_props or {}),
            "title": title,
            "durationInFrames": duration_in_frames,
            "fps": fps,
            "width": width,
            "height": height,
        }
    }
    temp_props_path = ENGINE_DIR / f"temp_props_{item_id}.json"
    with open(temp_props_path, "w", encoding="utf-8") as f:
        json.dump(props_data, f, ensure_ascii=False)

    npx = get_npx_cmd()
    gl_flag = "--gl=swangle" if sys.platform != "win32" else "--gl=angle"
    config_file = ENGINE_DIR / "remotion.config.ts"
    concurrency = os.environ.get("REMOTION_CONCURRENCY", "50%").strip() or "50%"
    x264_preset = os.environ.get("X264_PRESET", "superfast").strip() or "superfast"

    cmd = [
        npx,
        "remotion",
        "render",
        str(SRC_INDEX),
        "CodeVideo",
        out_video,
        f"--props={str(temp_props_path)}",
        f"--config={str(config_file)}",
        f"--frames=0-{duration_in_frames - 1}",
        "--image-format=jpeg",
        "--jpeg-quality=85",
        "--bundle-cache",
        f"--x264-preset={x264_preset}",
        gl_flag,
        f"--concurrency={concurrency}",
    ]

    if sys.platform != "win32":
        cmd.append("--enable-multiprocess-on-linux")

    public_dir = os.environ.get("REMOTION_PUBLIC_DIR") or str(ENGINE_DIR / "public")
    if os.path.exists(public_dir):
        cmd.append(f"--public-dir={public_dir}")

    chromium_path = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if chromium_path and os.path.exists(chromium_path):
        cmd.append(f"--browser-executable={chromium_path}")

    start_time = time.time()
    sem = get_render_semaphore()
    code_lock = get_code_render_lock()
    proc: asyncio.subprocess.Process | None = None

    try:
        async with sem:
            async with code_lock:
                USER_SRC_DIR.mkdir(parents=True, exist_ok=True)
                # 清除历史遗留文件以防模块冲突
                for old_item in USER_SRC_DIR.glob("*"):
                    if old_item.is_file():
                        try:
                            old_item.unlink()
                        except OSError:
                            pass

                # 规范化并写入用户代码文件到 src/user 目录下
                for rel_path, code in files.items():
                    clean_path = rel_path.lstrip("/\\")
                    if clean_path.startswith("src/"):
                        clean_path = clean_path[4:]
                    if clean_path.startswith("user/"):
                        clean_path = clean_path[5:]
                    target_file = USER_SRC_DIR / clean_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(code)

                # 智能入口桥接：确保 CodeWrapper 能稳定引入 Video.tsx
                video_exists = any((USER_SRC_DIR / f"Video{ext}").exists() for ext in [".tsx", ".jsx", ".ts", ".js"])
                if not video_exists:
                    entry_clean = entry_file.lstrip("/\\")
                    if entry_clean.startswith("src/"):
                        entry_clean = entry_clean[4:]
                    if entry_clean.startswith("user/"):
                        entry_clean = entry_clean[5:]

                    entry_path = USER_SRC_DIR / entry_clean
                    if not entry_path.exists():
                        for cand_name in files.keys():
                            cand = cand_name.lstrip("/\\")
                            if cand.startswith("src/"):
                                cand = cand[4:]
                            if cand.startswith("user/"):
                                cand = cand[5:]
                            if (USER_SRC_DIR / cand).exists():
                                entry_clean = cand
                                entry_path = USER_SRC_DIR / cand
                                break

                    if entry_path.exists():
                        stem = entry_clean.rsplit(".", 1)[0].replace("\\", "/")
                        bridge_code = (
                            f'import EntryComponent from "./{stem}";\n'
                            f'export * from "./{stem}";\n'
                            f'export default EntryComponent;\n'
                        )
                        with open(USER_SRC_DIR / "Video.tsx", "w", encoding="utf-8") as f:
                            f.write(bridge_code)

                extra_kwargs: dict[str, Any] = {}
                if sys.platform != "win32":
                    extra_kwargs["start_new_session"] = True

                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(ENGINE_DIR),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    **extra_kwargs,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
                elapsed = round(time.time() - start_time, 2)

                if proc.returncode != 0:
                    clean_partial_outputs(out_video, out_poster)
                    err_msg = stderr.decode("utf-8", errors="replace") or stdout.decode("utf-8", errors="replace")
                    logger.error(f"Remotion render failed ({proc.returncode}): {err_msg}")
                    return {
                        "success": False,
                        "error": f"Remotion render failed: {err_msg}",
                    }

                # 异步提取封面图
                await extract_poster(out_video, out_poster, time_offset=min(1.0, duration_seconds * 0.2))

        file_size = os.path.getsize(out_video) if os.path.exists(out_video) else 0

        return {
            "success": True,
            "item_id": item_id,
            "output_path": out_video,
            "poster_path": out_poster if os.path.exists(out_poster) else "",
            "duration_seconds": duration_seconds,
            "duration_frames": duration_in_frames,
            "fps": fps,
            "width": width,
            "height": height,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "render_time_seconds": elapsed,
        }
    except asyncio.TimeoutError:
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        return {"success": False, "error": f"Render timed out after {effective_timeout} seconds"}
    except (asyncio.CancelledError, KeyboardInterrupt):
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        raise
    except Exception as e:
        _kill_proc_tree(proc)
        clean_partial_outputs(out_video, out_poster)
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_props_path):
            try:
                os.remove(temp_props_path)
            except OSError:
                pass

