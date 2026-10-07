# -*- coding: utf-8 -*-
"""Remotion 最佳实践规范与设计系统规则指南。

整合 remotion-mcp-app 的 7 大编码规则与 chuk-motion 的主题设计系统。
"""

RULE_INDEX = """# Remotion Studio MCP — 视频生成与创作指南

本服务提供两种 Remotion 视频创作模式：
1. **声明式场景模式 (`create_video_from_spec`)**：输入 JSON Spec，系统自动应用设计系统、主题配色与高质感动画组件，开箱即用：
   - 基础场景：`TitleScene` (大标题片头), `TextOverlay` (金句观点), `EndScreen` (片尾订阅)
   - 数据图表：`BarChart` (竖向柱状图), `HorizontalBarChart` (横向排行榜), `PieChart` (环形占比图), `LineChart` (折线走势图)
   - 代码视窗：`CodeBlock` (macOS 风格代码打字机)
   - 商业与产品场景：`ComparisonCard` (对比/VS/优劣势分析), `MetricCard` (KPI 核心指标看板与动态滚数), `Timeline` (里程碑路线图与发光连线), `FeatureList` (特性矩阵与图标徽章), `QuoteCard` (名言引述与客户证言)
   - 背景音乐：支持 `spec.audioUrl` (或 `spec.bgm`) 与 `spec.audioVolume`，自动在结尾淡出
2. **自由式代码模式 (`create_video_from_code`)**：直接提供 React / Remotion TSX 源码多文件字典，享受 Remotion 4.0.532 最新全生态能力。
3. **长视频制作与异步任务防超时铁律 (Long Video Async Architecture)**：
   - 当视频包含多个镜头场景、时长较长（预估渲染时间可能超过网络代理 60s/120s 超时阈值时，如完整政策解读、产品演示、汇报片），**绝对不要因为担心超时而将视频生硬拆碎成 5~6 个 10 秒微型片段**！
   - 正确解法：使用**异步任务提交 + 轮询**机制：
     1. 第一步：调用 `submit_video_task_from_spec`（或 `submit_video_task_from_code`），毫秒级立即返回 `task_id`，规避一切 HTTP 请求超时；
     2. 第二步：告知用户后台正在全力渲染，并间隔 30~60 秒调用 `get_video_task_status(task_id)` 查询任务状态；
     3. 第三步：当查询到 `status: completed` 时，直接输出视频结果卡片 `user_display_markdown`。

## 可用规则工具 (Rule Tools)
可按需调用以下规则获取具体知识：
- `rule_react_code`: 多文件 React 代码规范、导出约定与支持的导入包
- `rule_remotion_animations`: useCurrentFrame 与基于帧的动画核心原理
- `rule_remotion_timing`: interpolate, spring, Easing 缓动曲线参数设计
- `rule_remotion_sequencing`: Sequence, TransitionSeries 多场景时序与嵌套编排
- `rule_remotion_transitions`: 转场效果（Fade, Slide, Wipe, Flip）与时长计算
- `rule_remotion_text_animations`: 打字机文字、高亮滚动与字词动效
- `rule_remotion_trimming`: 利用负 Sequence from 实现片段裁剪
- `rule_shotcraft_cinematic`: 157 张电影感镜头卡配方体系与音效设计美学
- `get_video_guide`: 全面设计指引（包含 8 大内置主题配色、全平台画幅比例与场景库）

4. **镜头工坊配方库 (Video-Shotcraft Tools)**：
   - `list_shotcraft_categories`: 查看 10 大镜头分类概览与镜头数量
   - `search_shotcraft_shots`: 按关键词或分类检索 157 张电影感镜头卡
   - `get_shotcraft_recipe`: 深入获取特定镜头的动效核心、缓动参数表、声音规范与已知坑

## 输出规范铁律
无论使用哪种方式生成视频，大模型在最终回复用户时，**必须原样输出返回结构中的 `user_display_markdown`**，直接展示高清封面图与可点击播放/下载的链接卡片，严禁折叠或简化！
"""

RULE_SHOTCRAFT_CINEMATIC = """# Video-Shotcraft 电影感运镜与动效配方体系

本系统整合了 157 张专业电影感镜头配方卡与 214 个真实 TSX 动效组件（位于 `/remotion_engine/src/shots/`），分为 10 大分类：
1. **片头与品牌开场 (Opening)**：十字准星描画、Logo压印、视窗起步、景深起飞（如 `brand-ink-open`, `orbit-ring-title-open`）
2. **2.5D运镜与视角 (Camera)**：俯冲降落、微距特写、景深漫游（如 `depth-stage-orbit`, `ortho-isometric-flip`）
3. **界面与卡片入场 (UI Entrance)**：扑克牌切发、聚光灯悬浮、折叠展开、级联飞入（如 `clip-card-looping`, `spotlight-hero-card`）
4. **核心功能交互 (Interaction)**：打字过滤、搜索点击、切换选择、滑块调节（如 `type-and-filter`, `cursor-click-ripple`）
5. **数据看板与亮点 (Data)**：动态滚动计数、脉冲流变、极速增长、多维指标（如 `countup-ticker`, `ring-gauge-sweep`）
6. **字体动效与金句 (Typography)**：字标逐字压印、流光扫掠、巨幕大词、字幕卡点（如 `marker-underline-title`, `split-flap-title`）
7. **光效与质感氛围 (Effects)**：毛玻璃景深、霓虹边缘、粒子氛围、流光漫射（如 `glass-refract`, `aurora-glow-drift`）
8. **节奏控制与慢动作 (Rhythm)**：变速定格(Speed Ramp)、极速冲击、心跳呼吸律动
9. **转场与镜头交接 (Transition)**：鞭抽(Whip Pan)、隐形硬切、遮挡穿透、推镜过渡
10. **片尾与号召行动 (Outro)**：合照定格、Logo脉冲升华、号召订阅与转化

## 声音设计与卡点原则
- 每一个动效的关键定格点（如字标压印的第 12 帧）应匹配轻微的机械/撞击音效（`public/audio/sfx/impact-heavy.mp3` 或 `click-*.mp3`）。
- 运镜加速使用 `sfx/whoosh-*.mp3`，光效扫掠使用 `sfx/shimmer.mp3`。
- 背景音乐（BGM）在 `public/audio/bgm/` 中提供 5 首精品无版权 BGM。
"""

RULE_REACT_CODE = """# Remotion React 代码编写规范

## 核心约定
1. 入口文件默认为 `/src/Video.tsx`（若为其他文件名，系统会自动生成桥接代理），支持 `export default function Video(props)` 或 `export const Video = ...` 命名导出。
2. 完整预装并支持导入 Remotion 4.x 核心生态与常用库：
   - `remotion` (例如 `AbsoluteFill`, `useCurrentFrame`, `useVideoConfig`, `spring`, `interpolate`, `Sequence`, `Audio`, `staticFile`)
   - `@remotion/transitions` 与 `@remotion/transitions/fade`, `slide`, `wipe`, `flip`
   - `@remotion/shapes` (`Circle`, `Rect`, `Triangle`, `Star`, `Pie` 矢量几何图形)
   - `@remotion/paths` (SVG 路径形变与演变动效)
   - `@remotion/media-utils` (音频分析与元数据解析)
   - `@remotion/google-fonts` (动态字体按需引入)
   - `react`, `react/jsx-runtime`
   - `lucide-react` (全部矢量图标组件库)
3. 严禁使用 CSS keyframe 动画或 CSS transitions 控制视频动效！所有动画必须基于 `useCurrentFrame()` 与 `spring` / `interpolate` 计算。
4. 建议使用绝对定位与 `AbsoluteFill` 布局，保证在不同分辨率下比例稳定。

## 代码示例

```tsx
import React from "react";
import { AbsoluteFill, useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";

export default function Video() {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(entrance, [0, 1], [0.85, 1]);

  return (
    <AbsoluteFill style={{
      backgroundColor: "#0b0f19",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      fontFamily: "system-ui, sans-serif"
    }}>
      <div style={{
        fontSize: 72,
        fontWeight: 800,
        color: "#38bdf8",
        opacity,
        transform: `scale(${scale})`,
        textShadow: "0 0 40px rgba(56, 189, 248, 0.4)"
      }}>
        Next-Gen Video
      </div>
      <div style={{
        marginTop: 20,
        fontSize: 28,
        color: "#94a3b8",
        opacity: interpolate(frame, [15, 35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
      }}>
        Powered by Remotion & MCP
      </div>
    </AbsoluteFill>
  );
}
```
"""

RULE_REMOTION_ANIMATIONS = """# Remotion 动画原理：帧驱动动画

Remotion 没有实时运行的浏览器事件循环概念，而是**逐帧渲染**（Frame-driven rendering）：
1. 每一帧调用 `const frame = useCurrentFrame()`。
2. 使用 `useVideoConfig()` 获取 `{ fps, durationInFrames, width, height }`。
3. 严禁使用 `setTimeout`, `setInterval`, `requestAnimationFrame` 或第三方不可控的 JS 计时器。
4. 所有的状态必须是当前 `frame` 的纯数学函数映射。
"""

RULE_REMOTION_TIMING = """# Remotion 时序控制：interpolate 与 spring

## 1. interpolate(frame, inputRange, outputRange, options)
将时间帧线性或平滑映射为数值、百分比或透明度：
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.25, 0.1, 0.25, 1),
});
```

## 2. spring({ frame, fps, config })
物理弹簧动画，带来真实自然的物理回弹质感：
```tsx
const progress = spring({
  frame,
  fps,
  config: {
    damping: 12,    // 阻尼：越小弹性越强（默认 10）
    mass: 0.5,      // 质量：越大惯性越大（默认 1）
    stiffness: 100, // 刚度：越大运动越快（默认 100）
  },
});
```
"""

RULE_REMOTION_SEQUENCING = """# Remotion 场景编排：Sequence 与时序管理

## Sequence 组件
`<Sequence from={startFrame} durationInFrames={length}>` 会为子组件创建独立的局部时间坐标系（子组件内部的 `useCurrentFrame()` 从 0 开始计算）：
```tsx
<AbsoluteFill>
  {/* 场景 1：0 到 90 帧 */}
  <Sequence from={0} durationInFrames={90}>
    <IntroScene />
  </Sequence>
  {/* 场景 2：90 到 180 帧 */}
  <Sequence from={90} durationInFrames={90}>
    <MainContentScene />
  </Sequence>
</AbsoluteFill>
```
"""

RULE_REMOTION_TRANSITIONS = """# Remotion 转场效果

可使用 `@remotion/transitions` 中的 `TransitionSeries` 或手动 `interpolate` 实现：
- **Fade (淡入淡出)**: 结合透明度 `opacity`
- **Slide (推镜/滑入)**: `transform: translateX(...)` 或 `translateY(...)`
- **Wipe (擦除)**: `clipPath: inset(0 ... 0 0)`
- **Scale / Zoom (缩放转场)**: `transform: scale(...)`
"""

RULE_REMOTION_TEXT_ANIMATIONS = """# Remotion 文字动效

## 1. Typewriter (打字机效果)
```tsx
const charsToShow = Math.floor(
  interpolate(frame, [0, 45], [0, text.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  })
);
const visibleText = text.slice(0, charsToShow);
```

## 2. Gradient Shimmer (渐变流光动效)
利用 background-clip 与变化的 background-position 制造流光溢彩的高级科技感。
"""

RULE_REMOTION_TRIMMING = """# Remotion 片段裁剪

若需要延迟某个组件的动画起点，或者只截取其中的一段，可以在 `<Sequence>` 中使用负的 `from` 偏移值或者调整 `startFrame` 参数。
"""
