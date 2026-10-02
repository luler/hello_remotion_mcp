import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThemeConfig } from "../themes";

export interface ComparisonCardItem {
  text: string;
  positive?: boolean;
}

export interface ComparisonSide {
  title: string;
  badge?: string;
  subtitle?: string;
  highlight?: boolean;
  items: (string | ComparisonCardItem)[];
}

export interface ComparisonCardProps {
  title?: string;
  subtitle?: string;
  left?: ComparisonSide;
  right?: ComparisonSide;
  theme: ThemeConfig;
}

export const ComparisonCard: React.FC<ComparisonCardProps> = ({
  title = "方案对比",
  subtitle = "Comparison & Highlights",
  left = {
    title: "传统方案",
    badge: "BEFORE",
    items: ["人工逐帧制作", "耗时数天至数周", "修改成本极高", "难以自动化扩展"],
  },
  right = {
    title: "AI + Remotion",
    badge: "AFTER · 10X 提效",
    highlight: true,
    items: ["代码即视频，精准到帧", "秒级自动化云端渲染", "配置驱动，一键换肤", "支持无限规模批量生成"],
  },
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });
  const titleY = interpolate(titleProgress, [0, 1], [-40, 0]);
  const titleOpacity = interpolate(titleProgress, [0, 1], [0, 1]);

  const cardProgress = spring({
    frame: frame - 6,
    fps,
    config: { damping: 15, stiffness: 100 },
  });
  const cardScale = interpolate(cardProgress, [0, 1], [0.92, 1]);
  const cardOpacity = interpolate(cardProgress, [0, 1], [0, 1]);

  const isWide = width >= 1200;

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
      {/* 标题区 */}
      <div
        style={{
          textAlign: "center",
          marginBottom: isWide ? "3rem" : "2rem",
          transform: `translateY(${titleY}px)`,
          opacity: titleOpacity,
        }}
      >
        <h1
          style={{
            fontSize: isWide ? "3.2rem" : "2.2rem",
            fontWeight: 800,
            color: theme.text,
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            style={{
              fontSize: isWide ? "1.35rem" : "1.05rem",
              color: theme.muted,
              marginTop: "0.6rem",
              margin: "0.6rem 0 0 0",
            }}
          >
            {subtitle}
          </p>
        )}
      </div>

      {/* 对比双卡片 */}
      <div
        style={{
          display: "flex",
          flexDirection: isWide ? "row" : "column",
          gap: isWide ? "3rem" : "1.5rem",
          width: "100%",
          maxWidth: isWide ? "1280px" : "720px",
          transform: `scale(${cardScale})`,
          opacity: cardOpacity,
        }}
      >
        <SideCard
          side={left}
          theme={theme}
          isLeft={true}
          delay={10}
          fps={fps}
          frame={frame}
        />
        <SideCard
          side={right}
          theme={theme}
          isLeft={false}
          delay={16}
          fps={fps}
          frame={frame}
        />
      </div>
    </AbsoluteFill>
  );
};

const SideCard: React.FC<{
  side: ComparisonSide;
  theme: ThemeConfig;
  isLeft: boolean;
  delay: number;
  fps: number;
  frame: number;
}> = ({ side, theme, isLeft, delay, fps, frame }) => {
  const isHighlight = Boolean(side.highlight);

  const bg = isHighlight
    ? `linear-gradient(145deg, ${theme.surface}f5, ${theme.primary}22)`
    : theme.surface;
  const borderColor = isHighlight ? theme.primary : theme.border;
  const glow = isHighlight ? `0 12px 40px ${theme.primary}33` : "none";

  return (
    <div
      style={{
        flex: 1,
        background: bg,
        border: `2px solid ${borderColor}`,
        borderRadius: "20px",
        padding: "2.2rem 2.4rem",
        boxShadow: glow,
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
    >
      {/* 顶部标签 */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.2rem" }}>
        <h3 style={{ fontSize: "1.7rem", fontWeight: 700, color: theme.text, margin: 0 }}>
          {side.title}
        </h3>
        {side.badge && (
          <span
            style={{
              fontSize: "0.85rem",
              fontWeight: 700,
              padding: "0.35rem 0.85rem",
              borderRadius: "999px",
              background: isHighlight ? theme.primary : `${theme.text}18`,
              color: isHighlight ? "#ffffff" : theme.muted,
              letterSpacing: "0.04em",
            }}
          >
            {side.badge}
          </span>
        )}
      </div>

      {side.subtitle && (
        <p style={{ fontSize: "0.95rem", color: theme.muted, margin: "0 0 1.5rem 0" }}>
          {side.subtitle}
        </p>
      )}

      {/* 列表项 */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {side.items.map((item, idx) => {
          const text = typeof item === "string" ? item : item.text;
          const positive = typeof item === "string" ? !isLeft : (item.positive !== false);

          const itemProg = spring({
            frame: frame - delay - idx * 4,
            fps,
            config: { damping: 14 },
          });
          const itemX = interpolate(itemProg, [0, 1], [-20, 0]);
          const itemOp = interpolate(itemProg, [0, 1], [0, 1]);

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.9rem",
                transform: `translateX(${itemX}px)`,
                opacity: itemOp,
              }}
            >
              <div
                style={{
                  width: "1.8rem",
                  height: "1.8rem",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "1rem",
                  fontWeight: "bold",
                  background: positive ? `${theme.accent}26` : `${theme.muted}1a`,
                  color: positive ? theme.accent : theme.muted,
                  flexShrink: 0,
                }}
              >
                {positive ? "✓" : "•"}
              </div>
              <span
                style={{
                  fontSize: "1.1rem",
                  color: positive ? theme.text : theme.muted,
                  fontWeight: positive ? 500 : 400,
                }}
              >
                {text}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
