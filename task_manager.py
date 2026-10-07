# -*- coding: utf-8 -*-
"""异步渲染任务管理器：支持后台任务队列、实时进度查询、冲突互斥拦截、任务主动取消与长视频无超时渲染。"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, store_dir: str):
        self.store_dir = os.path.abspath(store_dir)
        os.makedirs(self.store_dir, exist_ok=True)
        self.tasks_file = os.path.join(self.store_dir, "tasks.json")
        self._lock = threading.Lock()
        self._tasks: dict[str, dict[str, Any]] = {}
        self._async_tasks: dict[str, asyncio.Task] = {}
        self._load()

    def _load(self) -> None:
        with self._lock:
            if os.path.exists(self.tasks_file):
                try:
                    with open(self.tasks_file, "r", encoding="utf-8") as f:
                        self._tasks = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load tasks.json: {e}")
                    self._tasks = {}

    def _save(self) -> None:
        with self._lock:
            tmp = self.tasks_file + ".tmp"
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(self._tasks, f, ensure_ascii=False, indent=2)
                os.replace(tmp, self.tasks_file)
            except Exception as e:
                logger.warning(f"Failed to persist tasks.json: {e}")

    @staticmethod
    def new_task_id(prefix: str = "task") -> str:
        return f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            res = dict(task)

        now = time.time()
        status = res.get("status")
        if status in ("queued", "rendering"):
            started_at_ts = res.get("started_at_ts") or res.get("created_at_ts", now)
            res["elapsed_seconds"] = round(now - started_at_ts, 1)
        return res

    def get_active_task(self) -> dict[str, Any] | None:
        """获取当前正在排队或渲染中的唯一活跃任务（用于并发冲突拦截）。"""
        with self._lock:
            for task in self._tasks.values():
                if task.get("status") in ("queued", "rendering"):
                    res = dict(task)
                    now = time.time()
                    started_at_ts = res.get("started_at_ts") or res.get("created_at_ts", now)
                    res["elapsed_seconds"] = round(now - started_at_ts, 1)
                    return res
        return None

    def list_tasks(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._lock:
            items = [dict(t) for t in self._tasks.values()]
        items.sort(key=lambda x: x.get("created_at_ts", 0), reverse=True)
        now = time.time()
        for res in items:
            status = res.get("status")
            if status in ("queued", "rendering"):
                started_at_ts = res.get("started_at_ts") or res.get("created_at_ts", now)
                res["elapsed_seconds"] = round(now - started_at_ts, 1)
        return items[:limit]

    def cancel_task(self, task_id: str = "", reason: str = "") -> dict[str, Any]:
        """终止并取消指定的渲染任务，或者取消当前正在运行的活跃任务，释放算力资源。"""
        target_id = (task_id or "").strip()
        if not target_id:
            active = self.get_active_task()
            if not active:
                return {"ok": False, "error": "当前没有正在进行中的视频任务需要取消"}
            target_id = active["task_id"]

        with self._lock:
            task = self._tasks.get(target_id)
            if not task:
                return {"ok": False, "error": f"Task not found: {target_id}"}

            cur_status = task.get("status")
            if cur_status not in ("queued", "rendering"):
                return {
                    "ok": False,
                    "task_id": target_id,
                    "status": cur_status,
                    "error": f"任务当前处于 {cur_status} 状态，无需取消",
                }

            task["status"] = "cancelled"
            task["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            task["completed_at_ts"] = time.time()
            task["error"] = reason or "任务被用户主动取消"
        self._save()

        # 取消对应的 asyncio 协程并终止底层子进程
        async_task = self._async_tasks.get(target_id)
        if async_task and not async_task.done():
            async_task.cancel()

        title = task.get("title", "")
        return {
            "ok": True,
            "task_id": target_id,
            "title": title,
            "status": "cancelled",
            "message": f"视频任务【{title}】（ID: {target_id}）已成功终止并释放渲染算力资源。",
        }

    async def wait_for_task(self, task_id: str, timeout: float = 30.0) -> dict[str, Any]:
        """自适应等待任务完成（最高等待 timeout 秒），超时未完则返回当前状态。"""
        start = time.time()
        while time.time() - start < timeout:
            task = self.get_task(task_id)
            if not task or task.get("status") in ("completed", "failed", "cancelled"):
                return task or {}
            await asyncio.sleep(0.5)
        return self.get_task(task_id) or {}

    def create_spec_task(
        self,
        spec: dict[str, Any],
        name: str = "",
        timeout: int | None = None,
        force: bool = False,
        output_dir: str = "",
        render_fn: Any = None,
        register_fn: Any = None,
        get_base_url_fn: Any = None,
    ) -> dict[str, Any]:
        # 1. 检查当前是否已有正在渲染或排队的任务
        active = self.get_active_task()
        if active and not force:
            return {
                "ok": False,
                "conflict": True,
                "task_id": active["task_id"],
                "title": active.get("title", ""),
                "status": active.get("status", ""),
                "elapsed_seconds": active.get("elapsed_seconds", 0.0),
                "message": (
                    f"⚠️ 当前已有视频制作任务【{active.get('title')}】正在进行中 (Task ID: {active.get('task_id')}，已运行 {active.get('elapsed_seconds', 0)}s)。\n"
                    f"为了保证渲染性能与资源利用，请选择：\n"
                    f"1. 若需继续等待该视频完成，请调用 get_video_task_status 查询该任务进度；\n"
                    f"2. 若您不想做这个了，请先调用 cancel_video_task 结束上一个任务（或重新提交时指定 force=True 强制覆盖），然后方可开启新视频制作。"
                ),
            }
        elif active and force:
            self.cancel_task(active["task_id"], reason="被新视频制作任务强制替换取消")

        task_id = self.new_task_id("task_spec")
        item_id = self.new_task_id("vid_spec")
        title = spec.get("title") or name or "Remotion Video"

        scenes = spec.get("scenes") or []
        fps = int(spec.get("fps") or 30)
        total_duration = sum(s.get("duration", 3.5) for s in scenes) if scenes else 4.0

        task_record = {
            "task_id": task_id,
            "item_id": item_id,
            "mode": "spec",
            "title": title,
            "status": "queued",  # queued -> rendering -> completed / failed / cancelled
            "progress": 0,
            "scenes_count": len(scenes),
            "estimated_duration_seconds": round(total_duration, 1),
            "estimated_render_seconds": round(max(20.0, total_duration * 2.8), 1),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at_ts": time.time(),
            "started_at": None,
            "started_at_ts": None,
            "completed_at": None,
            "completed_at_ts": None,
            "render_time_seconds": 0.0,
            "error": None,
            "result": None,
        }

        with self._lock:
            self._tasks[task_id] = task_record
        self._save()

        # 启动后台非阻塞执行并跟踪句柄
        coro = self._run_spec_worker(
            task_id=task_id,
            item_id=item_id,
            title=title,
            spec=spec,
            timeout=timeout,
            output_dir=output_dir,
            render_fn=render_fn,
            register_fn=register_fn,
            get_base_url_fn=get_base_url_fn,
        )
        task_handle = asyncio.create_task(coro)
        self._async_tasks[task_id] = task_handle

        return task_record

    async def _run_spec_worker(
        self,
        task_id: str,
        item_id: str,
        title: str,
        spec: dict[str, Any],
        timeout: int | None,
        output_dir: str,
        render_fn: Any,
        register_fn: Any,
        get_base_url_fn: Any,
    ) -> None:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "rendering"
                self._tasks[task_id]["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._tasks[task_id]["started_at_ts"] = time.time()
                self._tasks[task_id]["progress"] = 15
        self._save()

        try:
            res = await render_fn(
                spec=spec,
                item_id=item_id,
                output_dir=output_dir,
                timeout=timeout,
            )

            if not res.get("success"):
                err = res.get("error") or "Unknown render error"
                with self._lock:
                    if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                        self._tasks[task_id]["status"] = "failed"
                        self._tasks[task_id]["error"] = err
                        self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        self._tasks[task_id]["completed_at_ts"] = time.time()
                self._save()
                return

            if register_fn:
                register_fn(
                    name=f"{item_id}.mp4",
                    path=res["output_path"],
                    title=title,
                    mode="spec",
                    poster_path=res.get("poster_path", ""),
                    spec=spec,
                    item_id=item_id,
                    duration_seconds=res["duration_seconds"],
                    duration_frames=res["duration_frames"],
                    fps=res["fps"],
                    width=res["width"],
                    height=res["height"],
                    render_time_seconds=res.get("render_time_seconds", 0.0),
                )

            base = get_base_url_fn() if get_base_url_fn else ""
            video_url = f"{base}/api/video/{item_id}.mp4"
            download_url = f"{base}/api/download/{item_id}.mp4"
            poster_url = f"{base}/api/poster/{item_id}.jpg" if res.get("poster_path") else ""

            theme_name = spec.get("theme", "tech")
            if isinstance(theme_name, dict):
                theme_name = theme_name.get("name", "custom")

            display_md = (
                f"### 🎬 视频已成功生成：{title}\n\n"
                f"![{title} 封面预览]({poster_url})\n\n"
                f"- 📺 **在线播放视频**：[{title}]({video_url})\n"
                f"- 📥 **下载高清 MP4**：[点击下载视频文件]({download_url})\n"
                f"- ⏱️ **规格参数**：{res['duration_seconds']} 秒 | {res['width']}x{res['height']} | {res['fps']} FPS | {res['file_size_mb']} MB\n"
                f"- ⏳ **渲染总耗时**：{res.get('render_time_seconds', 0.0)} 秒\n"
                f"- 🎨 **制作模式**：声明式 Spec 模式 (主题: `{theme_name}`)\n"
            )

            result_data = {
                "ok": True,
                "video_id": item_id,
                "title": title,
                "video_url": video_url,
                "download_url": download_url,
                "poster_url": poster_url,
                "duration_seconds": res["duration_seconds"],
                "duration_frames": res["duration_frames"],
                "fps": res["fps"],
                "resolution": f"{res['width']}x{res['height']}",
                "file_size_mb": res["file_size_mb"],
                "render_time_seconds": res.get("render_time_seconds", 0.0),
                "user_display_markdown": display_md,
            }

            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "completed"
                    self._tasks[task_id]["progress"] = 100
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
                    self._tasks[task_id]["render_time_seconds"] = res.get("render_time_seconds", 0.0)
                    self._tasks[task_id]["result"] = result_data
            self._save()

        except asyncio.CancelledError:
            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "cancelled"
                    self._tasks[task_id]["error"] = "任务被用户主动取消"
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
            self._save()
        except Exception as e:
            logger.exception(f"Unexpected error in spec worker {task_id}: {e}")
            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "failed"
                    self._tasks[task_id]["error"] = str(e)
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
            self._save()
        finally:
            self._async_tasks.pop(task_id, None)

    def create_code_task(
        self,
        files: dict[str, str],
        entry_file: str = "/src/Video.tsx",
        title: str = "Custom Video",
        duration_in_frames: int = 150,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        input_props: dict | None = None,
        timeout: int | None = None,
        force: bool = False,
        output_dir: str = "",
        render_fn: Any = None,
        register_fn: Any = None,
        get_base_url_fn: Any = None,
    ) -> dict[str, Any]:
        active = self.get_active_task()
        if active and not force:
            return {
                "ok": False,
                "conflict": True,
                "task_id": active["task_id"],
                "title": active.get("title", ""),
                "status": active.get("status", ""),
                "elapsed_seconds": active.get("elapsed_seconds", 0.0),
                "message": (
                    f"⚠️ 当前已有视频制作任务【{active.get('title')}】正在进行中 (Task ID: {active.get('task_id')}，已运行 {active.get('elapsed_seconds', 0)}s)。\n"
                    f"为了保证渲染性能与资源利用，请选择：\n"
                    f"1. 若需继续等待该视频完成，请调用 get_video_task_status 查询该任务进度；\n"
                    f"2. 若您不想做这个了，请先调用 cancel_video_task 结束上一个任务（或重新提交时指定 force=True 强制覆盖），然后方可开启新视频制作。"
                ),
            }
        elif active and force:
            self.cancel_task(active["task_id"], reason="被新视频制作任务强制替换取消")

        task_id = self.new_task_id("task_code")
        item_id = self.new_task_id("vid_code")
        total_duration = round(duration_in_frames / fps, 1)

        task_record = {
            "task_id": task_id,
            "item_id": item_id,
            "mode": "code",
            "title": title,
            "status": "queued",
            "progress": 0,
            "estimated_duration_seconds": total_duration,
            "estimated_render_seconds": round(max(20.0, total_duration * 2.8), 1),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at_ts": time.time(),
            "started_at": None,
            "started_at_ts": None,
            "completed_at": None,
            "completed_at_ts": None,
            "render_time_seconds": 0.0,
            "error": None,
            "result": None,
        }

        with self._lock:
            self._tasks[task_id] = task_record
        self._save()

        coro = self._run_code_worker(
            task_id=task_id,
            item_id=item_id,
            title=title,
            files=files,
            entry_file=entry_file,
            duration_in_frames=duration_in_frames,
            fps=fps,
            width=width,
            height=height,
            input_props=input_props,
            timeout=timeout,
            output_dir=output_dir,
            render_fn=render_fn,
            register_fn=register_fn,
            get_base_url_fn=get_base_url_fn,
        )
        task_handle = asyncio.create_task(coro)
        self._async_tasks[task_id] = task_handle

        return task_record

    async def _run_code_worker(
        self,
        task_id: str,
        item_id: str,
        title: str,
        files: dict[str, str],
        entry_file: str,
        duration_in_frames: int,
        fps: int,
        width: int,
        height: int,
        input_props: dict | None,
        timeout: int | None,
        output_dir: str,
        render_fn: Any,
        register_fn: Any,
        get_base_url_fn: Any,
    ) -> None:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "rendering"
                self._tasks[task_id]["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self._tasks[task_id]["started_at_ts"] = time.time()
                self._tasks[task_id]["progress"] = 15
        self._save()

        try:
            res = await render_fn(
                files=files,
                item_id=item_id,
                output_dir=output_dir,
                entry_file=entry_file,
                title=title,
                duration_in_frames=duration_in_frames,
                fps=fps,
                width=width,
                height=height,
                input_props=input_props,
                timeout=timeout,
            )

            if not res.get("success"):
                err = res.get("error") or "Unknown render error"
                with self._lock:
                    if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                        self._tasks[task_id]["status"] = "failed"
                        self._tasks[task_id]["error"] = err
                        self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        self._tasks[task_id]["completed_at_ts"] = time.time()
                self._save()
                return

            if register_fn:
                register_fn(
                    name=f"{item_id}.mp4",
                    path=res["output_path"],
                    title=title,
                    mode="code",
                    poster_path=res.get("poster_path", ""),
                    files=files,
                    item_id=item_id,
                    duration_seconds=res["duration_seconds"],
                    duration_frames=res["duration_frames"],
                    fps=res["fps"],
                    width=res["width"],
                    height=res["height"],
                    render_time_seconds=res.get("render_time_seconds", 0.0),
                )

            base = get_base_url_fn() if get_base_url_fn else ""
            video_url = f"{base}/api/video/{item_id}.mp4"
            download_url = f"{base}/api/download/{item_id}.mp4"
            poster_url = f"{base}/api/poster/{item_id}.jpg" if res.get("poster_path") else ""

            display_md = (
                f"### 🎬 视频已成功生成：{title}\n\n"
                f"![{title} 封面预览]({poster_url})\n\n"
                f"- 📺 **在线播放视频**：[{title}]({video_url})\n"
                f"- 📥 **下载高清 MP4**：[点击下载视频文件]({download_url})\n"
                f"- ⏱️ **规格参数**：{res['duration_seconds']} 秒 | {res['width']}x{res['height']} | {res['fps']} FPS | {res['file_size_mb']} MB\n"
                f"- ⏳ **渲染总耗时**：{res.get('render_time_seconds', 0.0)} 秒\n"
                f"- 🎨 **制作模式**：React 源码自由模式\n"
            )

            result_data = {
                "ok": True,
                "video_id": item_id,
                "title": title,
                "video_url": video_url,
                "download_url": download_url,
                "poster_url": poster_url,
                "duration_seconds": res["duration_seconds"],
                "duration_frames": res["duration_frames"],
                "fps": res["fps"],
                "resolution": f"{res['width']}x{res['height']}",
                "file_size_mb": res["file_size_mb"],
                "render_time_seconds": res.get("render_time_seconds", 0.0),
                "user_display_markdown": display_md,
            }

            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "completed"
                    self._tasks[task_id]["progress"] = 100
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
                    self._tasks[task_id]["render_time_seconds"] = res.get("render_time_seconds", 0.0)
                    self._tasks[task_id]["result"] = result_data
            self._save()

        except asyncio.CancelledError:
            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "cancelled"
                    self._tasks[task_id]["error"] = "任务被用户主动取消"
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
            self._save()
        except Exception as e:
            logger.exception(f"Unexpected error in code worker {task_id}: {e}")
            with self._lock:
                if task_id in self._tasks and self._tasks[task_id].get("status") != "cancelled":
                    self._tasks[task_id]["status"] = "failed"
                    self._tasks[task_id]["error"] = str(e)
                    self._tasks[task_id]["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._tasks[task_id]["completed_at_ts"] = time.time()
            self._save()
        finally:
            self._async_tasks.pop(task_id, None)
