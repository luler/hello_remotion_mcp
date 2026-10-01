import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface EndScreenProps {
  title?: string;
  channel?: string;
  cta?: string;
  social?: string[];
  theme: ThemeColors;
}

export const EndScreen: React.FC<EndScreenProps> = ({
  title = "Thanks for Watching",
  channel = "@RemotionStudio",
  cta = "Subscribe for More",
  social = [],
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

  // Subtle breathing pulse for CTA button
  const pulse = Math.sin(frame * 0.12) * 0.04 + 1.0;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 80px",
        textAlign: "center",
        fontFamily: "'PingFang SC', 'Microsoft YaHei', -apple-system, system-ui, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          maxWidth: 1000,
          padding: "50px 70px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 32,
          backdropFilter: "blur(20px)",
          boxShadow: `0 25px 60px rgba(0, 0, 0, 0.5), 0 0 50px ${theme.glow}`,
          opacity,
          transform: `scale(${scale})`,
        }}
      >
        {/* Channel Avatar badge */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 12,
            padding: "10px 24px",
            borderRadius: 9999,
            background: "rgba(255, 255, 255, 0.08)",
            border: `1px solid ${theme.border}`,
            fontSize: 22,
            fontWeight: 700,
            color: theme.primary,
            marginBottom: 28,
          }}
        >
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              background: theme.primary,
              boxShadow: `0 0 10px ${theme.primary}`,
            }}
          />
          {channel}
        </div>

        {/* Title */}
        <h2
          style={{
            margin: 0,
            fontSize: 60,
            fontWeight: 900,
            lineHeight: 1.2,
            color: theme.text,
            background: `linear-gradient(135deg, ${theme.text} 40%, ${theme.primary} 100%)`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          {title}
        </h2>

        {/* Pulse CTA Button */}
        {cta && (
          <div
            style={{
              marginTop: 40,
              padding: "18px 48px",
              borderRadius: 9999,
              background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`,
              color: "#ffffff",
              fontSize: 26,
              fontWeight: 800,
              letterSpacing: "0.05em",
              boxShadow: `0 10px 30px ${theme.glow}`,
              transform: `scale(${pulse})`,
              cursor: "pointer",
            }}
          >
            {cta}
          </div>
        )}

        {/* Social list */}
        {social.length > 0 && (
          <div
            style={{
              display: "flex",
              gap: 20,
              marginTop: 40,
              flexWrap: "wrap",
              justifyContent: "center",
            }}
          >
            {social.map((s, idx) => (
              <div
                key={idx}
                style={{
                  padding: "8px 20px",
                  borderRadius: 12,
                  background: "rgba(255, 255, 255, 0.05)",
                  color: theme.text_muted,
                  fontSize: 18,
                  fontWeight: 600,
                }}
              >
                {s}
              </div>
            ))}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
