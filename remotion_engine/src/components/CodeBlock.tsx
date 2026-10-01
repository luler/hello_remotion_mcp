import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface CodeBlockProps {
  title?: string;
  filename?: string;
  code: string;
  language?: string;
  isTyping?: boolean;
  theme: ThemeColors;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  title,
  filename = "index.ts",
  code = "",
  language = "typescript",
  isTyping = true,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 90 },
  });

  const scale = interpolate(entrance, [0, 1], [0.9, 1]);
  const opacity = interpolate(entrance, [0, 0.4], [0, 1]);

  let displayCode = code;
  if (isTyping) {
    const charsToShow = Math.floor(
      interpolate(frame, [10, 60], [0, code.length], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    );
    displayCode = code.slice(0, charsToShow);
  }

  const lines = displayCode.split("\n");

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "60px 80px",
        fontFamily: "'PingFang SC', 'Microsoft YaHei', -apple-system, system-ui, sans-serif",
      }}
    >
      {title && (
        <h2
          style={{
            fontSize: 48,
            fontWeight: 800,
            color: theme.text,
            marginBottom: 36,
            textAlign: "center",
            opacity,
          }}
        >
          {title}
        </h2>
      )}

      {/* Terminal Window */}
      <div
        style={{
          width: "100%",
          maxWidth: Math.min(width * 0.82, 1080),
          background: "rgba(13, 17, 23, 0.95)",
          border: `1px solid ${theme.border}`,
          borderRadius: 20,
          boxShadow: `0 25px 60px rgba(0, 0, 0, 0.6), 0 0 35px ${theme.glow}`,
          overflow: "hidden",
          opacity,
          transform: `scale(${scale})`,
        }}
      >
        {/* Terminal Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "16px 24px",
            background: "rgba(22, 27, 34, 0.9)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          {/* Mac window dots */}
          <div style={{ display: "flex", gap: 10 }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#ff5f56" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#ffbd2e" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#27c93f" }} />
          </div>

          {/* Filename */}
          <div
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: theme.text_muted,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            }}
          >
            {filename}
          </div>

          <div style={{ width: 44, fontSize: 13, color: theme.primary, textAlign: "right" }}>
            {language}
          </div>
        </div>

        {/* Code Content */}
        <div
          style={{
            padding: "28px 32px",
            fontFamily: "'Fira Code', ui-monospace, Menlo, Consolas, monospace",
            fontSize: 22,
            lineHeight: 1.6,
            color: "#e6edf3",
            overflow: "hidden",
          }}
        >
          {lines.map((line, idx) => (
            <div key={idx} style={{ display: "flex", gap: 24 }}>
              <span
                style={{
                  userSelect: "none",
                  width: 32,
                  textAlign: "right",
                  color: "#484f58",
                  fontSize: 18,
                }}
              >
                {idx + 1}
              </span>
              <span style={{ flex: 1, whiteSpace: "pre-wrap" }}>
                {line}
                {isTyping && idx === lines.length - 1 && (
                  <span
                    style={{
                      display: "inline-block",
                      width: 10,
                      height: 22,
                      background: theme.primary,
                      marginLeft: 4,
                      verticalAlign: "middle",
                      opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
                    }}
                  />
                )}
              </span>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
