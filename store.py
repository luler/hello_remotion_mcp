# -*- coding: utf-8 -*-
"""视频资产仓库：登记、查询、列表、删除与元数据持久化。"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading
import time
from typing import Any

_lock = threading.Lock()


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class VideoStore:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)
        self._index_path = os.path.join(self.root, "index.json")
        self._items: list[dict[str, Any]] = []
        self._load()

    @staticmethod
    def _infer_render_time(it: dict[str, Any]) -> float:
        """从视频 ID 的发起时间戳与完成登记时间戳自动推算历史视频的渲染耗时"""
        vid = str(it.get("id") or "")
        created_at = str(it.get("created_at") or "")
        parts = vid.split("_")
        if len(parts) >= 4 and len(parts[2]) == 8 and len(parts[3]) == 6 and created_at:
            try:
                import datetime
                start_dt = datetime.datetime.strptime(f"{parts[2]}_{parts[3]}", "%Y%m%d_%H%M%S")
                finish_dt = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                diff = (finish_dt - start_dt).total_seconds()
                if 0 < diff < 86400:
                    return round(diff, 2)
            except Exception:
                pass
        return 0.0

    def _load(self):
        if os.path.exists(self._index_path):
            try:
                with open(self._index_path, encoding="utf-8") as f:
                    self._items = json.load(f)
            except Exception:
                self._items = []
        # 清理在磁盘上已被删除的视频文件索引
        def _check_exists(p: str) -> bool:
            if not p:
                return False
            if os.path.exists(p):
                return True
            if p.startswith("/app/data/"):
                rel = p[len("/app/data/"):]
                local_cand = os.path.normpath(os.path.join(self.root, "..", rel))
                if os.path.exists(local_cand):
                    return True
            return False

        self._items = [it for it in self._items if _check_exists(it.get("path", ""))]

        # 兼容旧数据：若历史记录缺少 render_time_seconds，自动通过起始与完成时间推算补齐
        updated = False
        for it in self._items:
            if not it.get("render_time_seconds"):
                inferred = self._infer_render_time(it)
                if inferred > 0:
                    it["render_time_seconds"] = inferred
                    updated = True
        if updated:
            self._flush()

    def _flush(self):
        tmp = self._index_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self._index_path)

    @staticmethod
    def new_id(prefix: str = "vid") -> str:
        return f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

    def register(
        self,
        name: str,
        path: str,
        title: str = "",
        mode: str = "spec",  # "spec" or "code"
        poster_path: str = "",
        spec: dict | None = None,
        files: dict | None = None,
        item_id: str | None = None,
        duration_seconds: float = 0.0,
        duration_frames: int = 0,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        render_time_seconds: float = 0.0,
    ) -> dict[str, Any]:
        path = os.path.abspath(path)
        bytes_size = os.path.getsize(path) if os.path.exists(path) else 0
        poster_abs = os.path.abspath(poster_path) if poster_path and os.path.exists(poster_path) else ""

        rec: dict[str, Any] = {
            "id": item_id or self.new_id("vid"),
            "name": name,
            "title": title or name,
            "mode": mode,
            "path": path,
            "poster_path": poster_abs,
            "bytes": bytes_size,
            "duration_seconds": round(duration_seconds, 2),
            "duration_frames": duration_frames,
            "fps": fps,
            "width": width,
            "height": height,
            "render_time_seconds": round(render_time_seconds, 2),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at_ts": time.time(),
            "spec": spec,
            "files": files,
        }

        with _lock:
            self._items = [it for it in self._items if it["id"] != rec["id"]]
            self._items.insert(0, rec)
            self._flush()
        return rec

    def get(self, item_id: str) -> dict[str, Any] | None:
        if not item_id:
            return None
        with _lock:
            for it in self._items:
                if it["id"] == item_id or it["name"] == item_id or os.path.basename(it["path"]) == item_id:
                    return it
        return None

    def list(
        self,
        search: str = "",
        mode: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        with _lock:
            items = list(self._items)

        if search:
            s = search.lower()
            items = [
                it for it in items
                if s in it.get("title", "").lower() or s in it.get("name", "").lower() or s in it.get("id", "").lower()
            ]

        if mode:
            items = [it for it in items if it.get("mode") == mode]

        # 保证时间倒序
        items.sort(key=lambda x: x.get("created_at_ts", 0), reverse=True)
        total = len(items)
        paged = items[offset : offset + limit] if limit > 0 else items
        return paged, total

    def total_bytes(self) -> int:
        with _lock:
            return sum(it.get("bytes", 0) for it in self._items)

    def list_ids(self, search: str = "", mode: str = "") -> list[str]:
        items, _ = self.list(search=search, mode=mode, limit=0, offset=0)
        return [it["id"] for it in items]

    def delete(self, item_id: str) -> bool:
        with _lock:
            before_len = len(self._items)
            self._items = [it for it in self._items if it["id"] != item_id and it["name"] != item_id]
            if len(self._items) < before_len:
                self._flush()
                return True
        return False
