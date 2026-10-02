import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThemeConfig } from "../themes";

export interface QuoteCardProps {
  quote?: string;
  author?: string;
  role?: string;
  company?: string;
  badge?: string;
  theme: ThemeConfig;
}

export const QuoteCard: React.FC<QuoteCardProps> = ({
  quote = "“技术的最高境界是让人感受不到技术的存在，代码即视频正在重塑每一个人的视觉创作边界。”",
  author = "工程架构团队",
  role = "首席技术专家 · Principal Engineer",
  company = "Antigravity Lab",
  badge = "VISION & MISSION",
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const isWide = width >= 1200;

  const cardProg = spring({ frame, fps, config: { damping: 14, stiffness: 100 } });
  const cardScale = interpolate(cardProg, [0, 1], [0.9, 1]);
  const cardOp = interpolate(cardProg, [0, 1], [0, 1]);

  const quoteProg = spring({ frame: frame - 6, fps, config: { damping: 16 } });
  const quoteY = interpolate(quoteProg, [0, 1], [30, 0]);
  const quoteOp = interpolate(quoteProg, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: isWide ? "3rem 8rem" : "3rem 2rem",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: isWide ? "1100px" : "720px",
          background: `linear-gradient(145deg, ${theme.surface}fa, ${theme.primary}15)`,
          border: `1px solid ${theme.border}`,
          borderRadius: "28px",
          padding: isWide ? "4rem 4.5rem" : "2.5rem 2rem",
          boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
          transform: `scale(${cardScale})`,
          opacity: cardOp,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* 装饰性大引号图标 */}
        <div
          style={{
            position: "absolute",
            top: "1.5rem",
            right: "2.5rem",
            fontSize: "9rem",
            lineHeight: 1,
            fontWeight: 900,
            color: `${theme.primary}1f`,
            fontFamily: "Georgia, serif",
            userSelect: "none",
            pointerEvents: "none",
          }}
        >
          “
        </div>

        {badge && (
          <div style={{ marginBottom: "1.8rem" }}>
            <span
              style={{
                fontSize: "0.85rem",
                fontWeight: 800,
                letterSpacing: "0.08em",
                padding: "0.35rem 0.9rem",
                borderRadius: "999px",
                background: `${theme.primary}26`,
                color: theme.primary,
                border: `1px solid ${theme.primary}55`,
              }}
            >
              {badge}
            </span>
          </div>
        )}

        <div
          style={{
            transform: `translateY(${quoteY}px)`,
            opacity: quoteOp,
          }}
        >
          <blockquote
            style={{
              fontSize: isWide ? "2.3rem" : "1.6rem",
              lineHeight: 1.5,
              fontWeight: 600,
              color: theme.text,
              margin: "0 0 2.5rem 0",
              letterSpacing: "-0.01em",
            }}
          >
            {quote}
          </blockquote>

          <div style={{ display: "flex", alignItems: "center", gap: "1.2rem" }}>
            <div
              style={{
                width: "3.4rem",
                height: "3.4rem",
                borderRadius: "50%",
                background: `linear-gradient(135deg, ${theme.primary}, ${theme.accent})`,
                color: "#fff",
                fontWeight: 800,
                fontSize: "1.3rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: `0 0 16px ${theme.primary}88`,
                flexShrink: 0,
              }}
            >
              {author.slice(0, 1)}
            </div>
            <div>
              <div style={{ fontSize: "1.35rem", fontWeight: 700, color: theme.text }}>
                {author}
              </div>
              <div style={{ fontSize: "1.05rem", color: theme.muted, marginTop: "0.2rem" }}>
                {role} {company ? `· ${company}` : ""}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
