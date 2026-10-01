import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface BarChartProps {
  title?: string;
  data: DataPoint[];
  theme: ThemeColors;
}

export const BarChart: React.FC<BarChartProps> = ({ title, data = [], theme }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const values = data.map((d) => d.value);
  const maxValue = Math.max(...values, 1);

  // Entrance spring
  const progress = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 90 },
  });

  const chartMaxHeight = height * 0.42;

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
      {/* Title */}
      {title && (
        <h2
          style={{
            fontSize: 48,
            fontWeight: 800,
            color: theme.text,
            marginBottom: 48,
            textAlign: "center",
            opacity: interpolate(progress, [0, 0.5], [0, 1]),
            transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
          }}
        >
          {title}
        </h2>
      )}

      {/* Chart Container */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "center",
          gap: 48,
          height: chartMaxHeight + 100,
          width: "100%",
          maxWidth: Math.min(width * 0.85, 1200),
          padding: "30px 50px 20px 50px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 24,
          backdropFilter: "blur(16px)",
          boxShadow: `0 20px 50px rgba(0, 0, 0, 0.5), 0 0 40px ${theme.glow}`,
        }}
      >
        {data.map((item, idx) => {
          // Staggered spring for each bar
          const barSpring = spring({
            frame: Math.max(0, frame - 8 - idx * 4),
            fps,
            config: { damping: 12, mass: 0.6, stiffness: 100 },
          });

          const currentBarHeight = (item.value / maxValue) * chartMaxHeight * barSpring;
          const displayVal = Math.round(item.value * barSpring * 10) / 10;
          const barColor = item.color || (idx % 2 === 0 ? theme.primary : theme.secondary);

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                flex: 1,
                maxWidth: 160,
              }}
            >
              {/* Value text above bar */}
              <div
                style={{
                  fontSize: 28,
                  fontWeight: 700,
                  color: theme.text,
                  marginBottom: 12,
                  opacity: barSpring,
                  transform: `translateY(${interpolate(barSpring, [0, 1], [10, 0])}px)`,
                }}
              >
                {displayVal}
              </div>

              {/* Bar */}
              <div
                style={{
                  width: "100%",
                  height: Math.max(currentBarHeight, 6),
                  background: `linear-gradient(180deg, ${barColor}, ${theme.accent})`,
                  borderRadius: "14px 14px 4px 4px",
                  boxShadow: `0 0 25px ${barColor}66`,
                }}
              />

              {/* Label below bar */}
              <div
                style={{
                  marginTop: 18,
                  fontSize: 24,
                  fontWeight: 600,
                  color: theme.text_muted,
                  textAlign: "center",
                  whiteSpace: "nowrap",
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  width: "100%",
                }}
              >
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
