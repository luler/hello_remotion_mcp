import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface PieChartProps {
  title?: string;
  data: Array<{ label: string; value: number; color?: string }>;
  theme: ThemeColors;
}

export const PieChart: React.FC<PieChartProps> = ({ title, data = [], theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const total = data.reduce((acc, cur) => acc + cur.value, 0) || 1;

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 90 },
  });

  const radius = 130;
  const circumference = 2 * Math.PI * radius;
  const strokeWidth = 38;

  // Palette
  const colors = [
    theme.primary,
    theme.secondary,
    theme.accent,
    "#f59e0b",
    "#ec4899",
    "#10b981",
  ];

  let cumulativeOffset = 0;

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
          alignItems: "center",
          justifyContent: "center",
          gap: 60,
          padding: "40px 60px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 24,
          backdropFilter: "blur(16px)",
          boxShadow: `0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px ${theme.glow}`,
        }}
      >
        {/* SVG Donut */}
        <div style={{ position: "relative", width: 340, height: 340 }}>
          <svg
            width="340"
            height="340"
            viewBox="0 0 340 340"
            style={{ transform: "rotate(-90deg)" }}
          >
            {data.map((item, idx) => {
              const segPct = item.value / total;
              const segLength = segPct * circumference * entrance;
              const segColor = item.color || colors[idx % colors.length];
              const dashOffset = -cumulativeOffset;
              cumulativeOffset += segPct * circumference * entrance;

              return (
                <circle
                  key={idx}
                  cx="170"
                  cy="170"
                  r={radius}
                  fill="transparent"
                  stroke={segColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={`${segLength} ${circumference}`}
                  strokeDashoffset={dashOffset}
                  strokeLinecap="round"
                  style={{
                    filter: `drop-shadow(0 0 8px ${segColor}88)`,
                  }}
                />
              );
            })}
          </svg>

          {/* Center text */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              opacity: entrance,
            }}
          >
            <span style={{ fontSize: 20, color: theme.text_muted, fontWeight: 600 }}>TOTAL</span>
            <span style={{ fontSize: 44, fontWeight: 900, color: theme.text }}>
              {Math.round(total)}
            </span>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          {data.map((item, idx) => {
            const segColor = item.color || colors[idx % colors.length];
            const pct = Math.round((item.value / total) * 100);

            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  fontSize: 22,
                  color: theme.text,
                  opacity: entrance,
                }}
              >
                <div
                  style={{
                    width: 18,
                    height: 18,
                    borderRadius: 6,
                    background: segColor,
                    boxShadow: `0 0 10px ${segColor}`,
                  }}
                />
                <span style={{ minWidth: 120, fontWeight: 500 }}>{item.label}</span>
                <span style={{ fontWeight: 700, color: segColor }}>{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
