import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface HorizontalBarChartProps {
  title?: string;
  data: Array<{ label: string; value: number; color?: string }>;
  theme: ThemeColors;
}

export const HorizontalBarChart: React.FC<HorizontalBarChartProps> = ({
  title,
  data = [],
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const values = data.map((d) => d.value);
  const maxValue = Math.max(...values, 1);

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 90 },
  });

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
            marginBottom: 44,
            textAlign: "center",
            opacity: interpolate(entrance, [0, 0.5], [0, 1]),
          }}
        >
          {title}
        </h2>
      )}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 24,
          width: "100%",
          maxWidth: Math.min(width * 0.85, 1100),
          padding: "36px 44px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 24,
          backdropFilter: "blur(16px)",
          boxShadow: `0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px ${theme.glow}`,
        }}
      >
        {data.map((item, idx) => {
          const barSpring = spring({
            frame: Math.max(0, frame - 6 - idx * 5),
            fps,
            config: { damping: 14, mass: 0.5, stiffness: 100 },
          });

          const pct = (item.value / maxValue) * 100 * barSpring;
          const barColor = item.color || (idx === 0 ? theme.primary : idx === 1 ? theme.secondary : theme.accent);

          return (
            <div key={idx} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: 24,
                  fontWeight: 600,
                  color: theme.text,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span
                    style={{
                      display: "inline-flex",
                      justifyContent: "center",
                      alignItems: "center",
                      width: 32,
                      height: 32,
                      borderRadius: 8,
                      fontSize: 18,
                      fontWeight: 800,
                      background: idx === 0 ? theme.primary : "rgba(255,255,255,0.1)",
                      color: idx === 0 ? theme.bg : theme.text,
                    }}
                  >
                    {idx + 1}
                  </span>
                  <span>{item.label}</span>
                </div>
                <span style={{ fontWeight: 700, color: barColor }}>
                  {Math.round(item.value * barSpring * 10) / 10}
                </span>
              </div>

              {/* Progress track */}
              <div
                style={{
                  width: "100%",
                  height: 20,
                  background: "rgba(255, 255, 255, 0.08)",
                  borderRadius: 9999,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${Math.max(pct, 0)}%`,
                    height: "100%",
                    background: `linear-gradient(90deg, ${barColor}, ${theme.secondary})`,
                    borderRadius: 9999,
                    boxShadow: `0 0 16px ${barColor}88`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
