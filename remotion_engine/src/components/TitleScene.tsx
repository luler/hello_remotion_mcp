import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface TitleSceneProps {
  title: string;
  subtitle?: string;
  badge?: string;
  variant?: "centered" | "left" | "bold" | "gradient" | "minimal";
  animation?: "fade_zoom" | "slide_up" | "typewriter" | "blur_in";
  theme: ThemeColors;
}

export const TitleScene: React.FC<TitleSceneProps> = ({
  title,
  subtitle,
  badge,
  variant = "gradient",
  animation = "fade_zoom",
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const progress = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 100 },
  });

  let opacity = 1;
  let transform = "none";
  let filter = "none";
  let displayTitle = title;

  if (animation === "fade_zoom") {
    opacity = interpolate(progress, [0, 1], [0, 1]);
    const scale = interpolate(progress, [0, 1], [0.85, 1]);
    transform = `scale(${scale})`;
  } else if (animation === "slide_up") {
    opacity = interpolate(progress, [0, 1], [0, 1]);
    const translateY = interpolate(progress, [0, 1], [80, 0]);
    transform = `translateY(${translateY}px)`;
  } else if (animation === "typewriter") {
    const chars = Math.floor(
      interpolate(frame, [0, 45], [0, title.length], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    );
    displayTitle = title.slice(0, chars);
  } else if (animation === "blur_in") {
    opacity = interpolate(progress, [0, 1], [0, 1]);
    const blur = interpolate(progress, [0, 1], [24, 0]);
    filter = `blur(${blur}px)`;
  }

  // Subtitle delayed entrance
  const subProgress = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 90 },
  });
  const subOpacity = interpolate(subProgress, [0, 1], [0, 1]);
  const subTranslateY = interpolate(subProgress, [0, 1], [30, 0]);

  const isLeft = variant === "left";

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: isLeft ? "flex-start" : "center",
        padding: isLeft ? "0 140px" : "0 80px",
        textAlign: isLeft ? "left" : "center",
        fontFamily: "'PingFang SC', 'Microsoft YaHei', -apple-system, system-ui, sans-serif",
      }}
    >
      {/* Badge */}
      {badge && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "8px 20px",
            borderRadius: "9999px",
            background: theme.card_bg,
            border: `1px solid ${theme.border}`,
            color: theme.primary,
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: 32,
            boxShadow: `0 0 25px ${theme.glow}`,
            opacity: subOpacity,
          }}
        >
          {badge}
        </div>
      )}

      {/* Main Title */}
      <h1
        style={{
          margin: 0,
          fontSize: 84,
          fontWeight: 900,
          lineHeight: 1.15,
          letterSpacing: "-0.03em",
          color: theme.text,
          opacity,
          transform,
          filter,
          ...(variant === "gradient"
            ? {
                background: `linear-gradient(135deg, ${theme.text} 30%, ${theme.primary} 70%, ${theme.secondary} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }
            : {}),
          textShadow: variant !== "gradient" ? `0 0 60px ${theme.glow}` : "none",
        }}
      >
        {displayTitle}
      </h1>

      {/* Subtitle */}
      {subtitle && (
        <p
          style={{
            margin: "28px 0 0 0",
            fontSize: 34,
            fontWeight: 400,
            lineHeight: 1.4,
            color: theme.text_muted,
            maxWidth: 1200,
            opacity: subOpacity,
            transform: `translateY(${subTranslateY}px)`,
          }}
        >
          {subtitle}
        </p>
      )}
    </AbsoluteFill>
  );
};
