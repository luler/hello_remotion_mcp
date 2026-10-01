import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface TextOverlayProps {
  headline: string;
  subheadline?: string;
  style?: "minimal" | "badge" | "quote";
  theme: ThemeColors;
}

export const TextOverlay: React.FC<TextOverlayProps> = ({
  headline,
  subheadline,
  style = "badge",
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 13, mass: 0.6, stiffness: 95 },
  });

  const scale = interpolate(entrance, [0, 1], [0.85, 1]);
  const opacity = interpolate(entrance, [0, 0.4], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 100px",
        textAlign: "center",
        fontFamily: "'PingFang SC', 'Microsoft YaHei', -apple-system, system-ui, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          maxWidth: 1200,
          padding: "60px 80px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 32,
          backdropFilter: "blur(20px)",
          boxShadow: `0 25px 60px rgba(0, 0, 0, 0.5), 0 0 50px ${theme.glow}`,
          opacity,
          transform: `scale(${scale})`,
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: 64,
            fontWeight: 900,
            lineHeight: 1.25,
            letterSpacing: "-0.02em",
            color: theme.text,
            background: `linear-gradient(135deg, ${theme.text} 40%, ${theme.primary} 100%)`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          {style === "quote" ? `“${headline}”` : headline}
        </h2>

        {subheadline && (
          <p
            style={{
              margin: "28px 0 0 0",
              fontSize: 30,
              fontWeight: 400,
              lineHeight: 1.5,
              color: theme.text_muted,
            }}
          >
            {subheadline}
          </p>
        )}
      </div>
    </AbsoluteFill>
  );
};
