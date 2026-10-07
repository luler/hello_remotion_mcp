# -*- coding: utf-8 -*-
"""Video-Shotcraft 镜头配方卡知识库：索引、检索与动效指南。

收录 157 张电影感镜头配方卡、214 个 Remotion 动效样式、音效卡点与美学规范。
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
SHOTS_DIR = BASE_DIR / "shotcraft" / "references" / "shots"
RULES_DIR = BASE_DIR / "shotcraft" / "references"
PUBLIC_DIR = BASE_DIR / "data" / "public"

CATEGORIES = [
    {"id": "opening", "name": "片头与品牌开场 (Opening)", "desc": "品牌立号、十字准星描画、Logo压印、视窗起步"},
    {"id": "camera", "name": "2.5D运镜与视角 (Camera)", "desc": "空间漫游、俯冲降落、微距特写、景深层次移动"},
    {"id": "ui-entrance", "name": "界面与卡片入场 (UI Entrance)", "desc": "级联飞入、扑克牌切发、聚光灯悬浮、折叠展开"},
    {"id": "interaction", "name": "核心功能交互 (Interaction)", "desc": "打字过滤、搜索点击、切换选择、滑块调节"},
    {"id": "data", "name": "数据看板与亮点 (Data)", "desc": "动态滚动计数、脉冲流变、极速增长、多维指标"},
    {"id": "typography", "name": "字体动效与金句 (Typography)", "desc": "字标逐字压印、流光扫掠、巨幕大词、字幕卡点"},
    {"id": "effects", "name": "光效与质感氛围 (Effects)", "desc": "毛玻璃景深、霓虹边缘、粒子氛围、流光漫射"},
    {"id": "rhythm", "name": "节奏控制与慢动作 (Rhythm)", "desc": "变速定格(Speed Ramp)、极速冲击、心跳呼吸律动"},
    {"id": "transition", "name": "转场与镜头交接 (Transition)", "desc": "鞭抽(Whip Pan)、隐形硬切、遮挡穿透、推镜过渡"},
    {"id": "outro", "name": "片尾与号召行动 (Outro)", "desc": "合照定格、Logo脉冲升华、号召订阅与转化"},
]


class ShotcraftIndex:
    """镜头卡索引库"""
    def __init__(self, shots_dir: Path | None = None):
        self.shots_dir = shots_dir or SHOTS_DIR
        self._cards: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if not self.shots_dir.exists():
            return

        for category_dir in self.shots_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue
            cat_name = category_dir.name
            for file_path in category_dir.glob("*.md"):
                if file_path.name == "ATTRIBUTION.md":
                    continue
                try:
                    card = self._parse_card(file_path, cat_name)
                    if card and card.get("name"):
                        self._cards[card["name"].lower()] = card
                except Exception:
                    continue
        self._loaded = True

    def _parse_card(self, file_path: Path, category: str) -> dict[str, Any]:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        meta: dict[str, str] = {}
        body = text

        # 解析 YAML Frontmatter
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1]
                body = parts[2]
                for line in fm.strip().splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip()

        name = meta.get("name") or file_path.stem
        one_liner = meta.get("一句话") or meta.get("summary") or ""
        applicable = meta.get("适用") or meta.get("use_case") or ""
        duration = meta.get("时长") or meta.get("duration") or ""
        energy = meta.get("能量") or meta.get("energy") or ""
        tags = meta.get("标签") or meta.get("tags") or category

        # 提取关键 Markdown 小节
        sections: dict[str, str] = {}
        curr_sec = "content"
        curr_lines: list[str] = []
        for line in body.splitlines():
            if line.startswith("## "):
                if curr_lines:
                    sections[curr_sec] = "\n".join(curr_lines).strip()
                    curr_lines = []
                curr_sec = line[3:].strip()
            else:
                curr_lines.append(line)
        if curr_lines:
            sections[curr_sec] = "\n".join(curr_lines).strip()

        # 解析参考 demo 路径
        ref_impl = sections.get("参考实现", "")
        demo_rel_path = ""
        m = re.search(r"demos/([\w\-_/]+\.tsx)", ref_impl)
        if m:
            demo_rel_path = m.group(1)

        return {
            "name": name,
            "filename": file_path.name,
            "category": category,
            "one_liner": one_liner,
            "applicable": applicable,
            "duration": duration,
            "energy": energy,
            "tags": tags,
            "intent": sections.get("意图", ""),
            "core_motion": sections.get("动效核心", ""),
            "params_table": sections.get("参数表", ""),
            "sound_design": sections.get("声音", ""),
            "pitfalls": sections.get("已知坑", ""),
            "reference_impl": ref_impl,
            "demo_rel_path": demo_rel_path,
            "full_content": text,
        }

    def list_categories(self) -> list[dict[str, Any]]:
        self.load()
        counts = {}
        for c in self._cards.values():
            cat = c["category"]
            counts[cat] = counts.get(cat, 0) + 1
        return [
            {**cat, "count": counts.get(cat["id"], 0)}
            for cat in CATEGORIES
        ]

    def list_shots(self, category: str | None = None) -> list[dict[str, Any]]:
        self.load()
        res = []
        for c in self._cards.values():
            if category and c["category"].lower() != category.lower().strip():
                continue
            res.append({
                "name": c["name"],
                "category": c["category"],
                "one_liner": c["one_liner"],
                "duration": c["duration"],
                "applicable": c["applicable"],
                "energy": c["energy"],
                "demo_component": c["demo_rel_path"],
            })
        return sorted(res, key=lambda x: (x["category"], x["name"]))

    def get_shot(self, name: str) -> dict[str, Any] | None:
        self.load()
        k = name.strip().lower()
        if k in self._cards:
            return self._cards[k]
        # 模糊匹配
        for key, val in self._cards.items():
            if k in key or key in k:
                return val
        return None

    def search(self, query: str, limit: int = 15) -> list[dict[str, Any]]:
        self.load()
        q = query.strip().lower()
        if not q:
            return self.list_shots()[:limit]

        scored: list[tuple[int, dict[str, Any]]] = []
        for c in self._cards.values():
            score = 0
            if q == c["name"].lower():
                score += 100
            elif q in c["name"].lower():
                score += 50
            if q in c["category"].lower():
                score += 30
            if q in c["one_liner"].lower():
                score += 25
            if q in c["applicable"].lower():
                score += 20
            if q in c["core_motion"].lower():
                score += 15
            if q in c["intent"].lower():
                score += 10

            if score > 0:
                scored.append((score, {
                    "name": c["name"],
                    "category": c["category"],
                    "one_liner": c["one_liner"],
                    "duration": c["duration"],
                    "applicable": c["applicable"],
                    "energy": c["energy"],
                    "demo_component": c["demo_rel_path"],
                }))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]


SHOT_INDEX = ShotcraftIndex()
