import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThemeConfig } from "../themes";
import { resolveLucideIcon } from "./iconHelper";

export interface TimelineItem {
  date?: string;
  tag?: string;
  badge?: string;
  icon?: string;
  title: string;
  description?: string;
  active?: boolean;
}

export interface TimelineProps {
  title?: string;
  subtitle?: string;
  items?: TimelineItem[];
  theme: ThemeConfig;
}

export const Timeline: React.FC<TimelineProps> = ({
  title = "发展演进历程与路线图",
  subtitle = "Milestones & Future Roadmap",
  items = [
    { date: "Phase 1 · 2024", tag: "FOUNDATION", title: "核心算法与原型研发", description: "完成首代自适应时间轴与排版引擎" },
    { date: "Phase 2 · 2025", tag: "ACCELERATION", title: "云端 GPU 渲染集群上线", description: "实现毫秒级帧提取与百倍吞吐扩容" },
    { date: "Phase 3 · 2026", tag: "AI INTEGRATION", title: "原生 MCP 与 Agent 协同", description: "打通多模态 AI 智能体自主编排与无感渲染", active: true },
    { date: "Phase 4 · 展望", tag: "NEXT GEN", title: "全自研实时超清神经渲染", description: "迈向 4K 120FPS 零延迟影视级生成" },
  ],
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const titleProg = spring({ frame, fps, config: { damping: 14 } });
  const titleY = interpolate(titleProg, [0, 1], [-30, 0]);
  const titleOp = interpolate(titleProg, [0, 1], [0, 1]);

  const isWide = width >= 1200;

  // 连线展开动画
  const lineProg = spring({
    frame: frame - 6,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: isWide ? "3rem 6rem" : "3rem 2rem",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* 标题 */}
      <div
        style={{
          textAlign: "center",
          marginBottom: isWide ? "4rem" : "2.5rem",
          transform: `translateY(${titleY}px)`,
          opacity: titleOp,
        }}
      >
        <h1 style={{ fontSize: isWide ? "3.2rem" : "2.2rem", fontWeight: 800, color: theme.text, margin: 0 }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{ fontSize: isWide ? "1.35rem" : "1.05rem", color: theme.muted, marginTop: "0.6rem", margin: "0.6rem 0 0 0" }}>
            {subtitle}
          </p>
        )}
      </div>

      {/* 时间轴水平/垂直网格 */}
      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: isWide ? "1300px" : "680px",
          display: "flex",
          flexDirection: isWide ? "row" : "column",
          gap: isWide ? "1.8rem" : "1.8rem",
          alignItems: isWide ? "flex-start" : "stretch",
        }}
      >
        {/* 背景主连线 (水平方向) */}
        {isWide && (
          <div
            style={{
              position: "absolute",
              top: "1.2rem",
              left: "40px",
              right: "40px",
              height: "4px",
              background: theme.border,
              zIndex: 1,
            }}
          >
            <div
              style={{
                width: `${lineProg * 100}%`,
                height: "100%",
                background: `linear-gradient(90deg, ${theme.primary}, ${theme.accent})`,
                boxShadow: `0 0 12px ${theme.primary}`,
              }}
            />
          </div>
        )}

        {/* 节点渲染 */}
        {items.map((it, idx) => {
          const nodeProg = spring({
            frame: frame - 10 - idx * 6,
            fps,
            config: { damping: 14, stiffness: 100 },
          });
          const scale = interpolate(nodeProg, [0, 1], [0.85, 1]);
          const opacity = interpolate(nodeProg, [0, 1], [0, 1]);

          const isActive = Boolean(it.active);

          return (
            <div
              key={idx}
              style={{
                flex: 1,
                position: "relative",
                zIndex: 2,
                transform: `scale(${scale})`,
                opacity,
                display: "flex",
                flexDirection: "column",
              }}
            >
              {/* 圆形节点光标 */}
              <div
                style={{
                  width: "2.4rem",
                  height: "2.4rem",
                  borderRadius: "50%",
                  background: isActive ? theme.accent : theme.surface,
                  border: `3px solid ${isActive ? theme.primary : theme.border}`,
                  boxShadow: isActive ? `0 0 20px ${theme.accent}aa` : "none",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: isActive ? "#000" : theme.muted,
                  fontWeight: 800,
                  fontSize: "0.9rem",
                  marginBottom: "1.2rem",
                  alignSelf: isWide ? "center" : "flex-start",
                }}
              >
                {(() => {
                  if (it.icon) {
                    const Icon = resolveLucideIcon(it.icon);
                    return Icon ? (
                      <Icon size={18} color={isActive ? "#000" : theme.muted} strokeWidth={2.5} />
                    ) : (
                      it.icon
                    );
                  }
                  return idx + 1;
                })()}
              </div>

              {/* 内容卡片 */}
              <div
                style={{
                  background: isActive ? `${theme.primary}18` : theme.surface,
                  border: `1px solid ${isActive ? theme.primary : theme.border}`,
                  borderRadius: "16px",
                  padding: "1.6rem 1.4rem",
                  boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.6rem" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: theme.primary }}>
                    {it.date}
                  </span>
                  {(it.badge || it.tag) && (
                    <span
                      style={{
                        fontSize: "0.75rem",
                        padding: "0.2rem 0.55rem",
                        borderRadius: "4px",
                        background: `${theme.accent}22`,
                        color: theme.accent,
                        fontWeight: 700,
                      }}
                    >
                      {it.badge || it.tag}
                    </span>
                  )}
                </div>
                <h4 style={{ fontSize: "1.3rem", fontWeight: 700, color: theme.text, margin: "0 0 0.5rem 0" }}>
                  {it.title}
                </h4>
                {it.description && (
                  <p style={{ fontSize: "0.95rem", color: theme.muted, margin: 0, lineHeight: 1.45 }}>
                    {it.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
