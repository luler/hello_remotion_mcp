# -*- coding: utf-8 -*-
"""Remotion 最佳实践规范与设计系统规则指南。

整合 remotion-mcp-app 的 7 大编码规则与 chuk-motion 的主题设计系统。
"""

RULE_INDEX = """# Remotion Studio MCP — 视频生成与创作指南

本服务提供两种 Remotion 视频创作模式：
1. **声明式场景模式 (`create_video_from_spec`)**：输入 JSON Spec，系统自动应用设计系统、主题配色与高质感动画组件（TitleScene, BarChart, CodeBlock, EndScreen等），开箱即用。
2. **自由式代码模式 (`create_video_from_code`)**：直接提供 React / Remotion TSX 源码多文件字典，享受 Remotion 4.x 的完整能力。

## 可用规则工具 (Rule Tools)
可按需调用以下规则获取具体知识：
- `rule_react_code`: 多文件 React 代码规范、导出约定与支持的导入包
- `rule_remotion_animations`: useCurrentFrame 与基于帧的动画核心原理
- `rule_remotion_timing`: interpolate, spring, Easing 缓动曲线参数设计
- `rule_remotion_sequencing`: Sequence, TransitionSeries 多场景时序与嵌套编排
- `rule_remotion_transitions`: 转场效果（Fade, Slide, Wipe, Flip）与时长计算
- `rule_remotion_text_animations`: 打字机文字、高亮滚动与字词动效
- `rule_remotion_trimming`: 利用负 Sequence from 实现片段裁剪
- `get_video_guide`: 全面设计指引（包含 8 大内置主题配色、全平台画幅比例与场景库）

## 输出规范铁律
无论使用哪种方式生成视频，大模型在最终回复用户时，**必须原样输出返回结构中的 `user_display_markdown`**，直接展示高清封面图与可点击播放/下载的链接卡片，严禁折叠或简化！
"""

RULE_REACT_CODE = """# Remotion React 代码编写规范

## 核心约定
1. 入口文件默认为 `/src/Video.tsx`，必须 `export default function Video(props)`。
2. 支持导入标准依赖：
   - `remotion` (例如 `AbsoluteFill`, `useCurrentFrame`, `useVideoConfig`, `spring`, `interpolate`, `Sequence`)
   - `@remotion/transitions` 与 `@remotion/transitions/fade`, `slide`, `wipe`
   - `react`, `react/jsx-runtime`
   - `lucide-react` 图标库
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
