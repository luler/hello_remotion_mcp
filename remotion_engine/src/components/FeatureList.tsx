import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThemeConfig } from "../themes";

export interface FeatureItem {
  icon?: string;
  badge?: string;
  title: string;
  description: string;
}

export interface FeatureListProps {
  title?: string;
  subtitle?: string;
  features?: FeatureItem[];
  columns?: 2 | 3;
  theme: ThemeConfig;
}

export const FeatureList: React.FC<FeatureListProps> = ({
  title = "核心产品特性与技术亮点",
  subtitle = "Key Features & Highlights",
  features = [
    { icon: "⚡", badge: "HIGH PERFORMANCE", title: "毫秒级渲染响应", description: "基于独立轻量 Chromium 与软光栅多路复用，生成效率提升 300%。" },
    { icon: "🎨", badge: "THEME ENGINE", title: "8 款顶级主题预设", description: "内置科技、赛博朋克、金融、极简等全套主流商业调色方案。" },
    { icon: "📐", badge: "MULTI PLATFORM", title: "全画幅画质适配", description: "原生支持横屏 16:9、竖屏 9:16、正方形 1:1，自动规避平台安全区。" },
    { icon: "🤖", badge: "NATIVE MCP", title: "无缝大模型 Agent 集成", description: "基于标准 Streamable HTTP 协议，与 Cherry Studio、Cursor 零门槛连接。" },
  ],
  columns = 2,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const titleProg = spring({ frame, fps, config: { damping: 14 } });
  const titleY = interpolate(titleProg, [0, 1], [-30, 0]);
  const titleOp = interpolate(titleProg, [0, 1], [0, 1]);

  const isWide = width >= 1200;
  const colCount = isWide ? columns : 1;

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
          marginBottom: isWide ? "3.5rem" : "2rem",
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

      {/* 特性卡片网格 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${colCount}, 1fr)`,
          gap: isWide ? "2.2rem" : "1.2rem",
          width: "100%",
          maxWidth: isWide ? "1280px" : "680px",
        }}
      >
        {features.map((f, idx) => {
          const itemProg = spring({
            frame: frame - 8 - idx * 5,
            fps,
            config: { damping: 14, stiffness: 100 },
          });
          const scale = interpolate(itemProg, [0, 1], [0.92, 1]);
          const opacity = interpolate(itemProg, [0, 1], [0, 1]);

          return (
            <div
              key={idx}
              style={{
                background: theme.surface,
                border: `1px solid ${theme.border}`,
                borderRadius: "18px",
                padding: "2rem 2.2rem",
                display: "flex",
                gap: "1.4rem",
                boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
                transform: `scale(${scale})`,
                opacity,
              }}
            >
              {f.icon && (
                <div
                  style={{
                    width: "3.2rem",
                    height: "3.2rem",
                    borderRadius: "14px",
                    background: `${theme.primary}22`,
                    border: `1px solid ${theme.primary}44`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.6rem",
                    flexShrink: 0,
                  }}
                >
                  {f.icon}
                </div>
              )}
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <h3 style={{ fontSize: "1.45rem", fontWeight: 700, color: theme.text, margin: 0 }}>
                    {f.title}
                  </h3>
                  {f.badge && (
                    <span
                      style={{
                        fontSize: "0.75rem",
                        fontWeight: 700,
                        padding: "0.2rem 0.6rem",
                        borderRadius: "4px",
                        background: `${theme.accent}1a`,
                        color: theme.accent,
                      }}
                    >
                      {f.badge}
                    </span>
                  )}
                </div>
                <p style={{ fontSize: "1.05rem", color: theme.muted, margin: 0, lineHeight: 1.5 }}>
                  {f.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
