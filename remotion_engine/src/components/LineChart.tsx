import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ThemeColors } from "../themes";

export interface LineChartProps {
  title?: string;
  data: Array<{ label: string; value: number }>;
  theme: ThemeColors;
}

export const LineChart: React.FC<LineChartProps> = ({ title, data = [], theme }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const values = data.map((d) => d.value);
  const maxValue = Math.max(...values, 1);
  const minValue = Math.min(...values, 0);

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 90 },
  });

  const chartW = Math.min(width * 0.75, 960);
  const chartH = 340;
  const paddingX = 60;
  const paddingY = 40;

  const points = data.map((item, idx) => {
    const x = paddingX + (idx / Math.max(data.length - 1, 1)) * (chartW - 2 * paddingX);
    const range = maxValue - minValue || 1;
    const y = chartH - paddingY - ((item.value - minValue) / range) * (chartH - 2 * paddingY);
    return { x, y, ...item };
  });

  const pathD = points.reduce((acc, p, idx) => {
    return idx === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
  }, "");

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
          padding: "36px 48px",
          background: theme.card_bg,
          border: `1px solid ${theme.border}`,
          borderRadius: 24,
          backdropFilter: "blur(16px)",
          boxShadow: `0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px ${theme.glow}`,
        }}
      >
        <svg width={chartW} height={chartH} viewBox={`0 0 ${chartW} ${chartH}`}>
          <defs>
            <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={theme.primary} />
              <stop offset="100%" stopColor={theme.secondary} />
            </linearGradient>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.primary} stopOpacity="0.4" />
              <stop offset="100%" stopColor={theme.primary} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Area fill */}
          {points.length > 0 && (
            <path
              d={`${pathD} L ${points[points.length - 1].x} ${chartH - paddingY} L ${points[0].x} ${chartH - paddingY} Z`}
              fill="url(#areaGrad)"
              opacity={entrance}
            />
          )}

          {/* Line */}
          <path
            d={pathD}
            fill="none"
            stroke="url(#lineGrad)"
            strokeWidth="6"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="2000"
            strokeDashoffset={interpolate(entrance, [0, 1], [2000, 0])}
            style={{ filter: `drop-shadow(0 0 12px ${theme.primary}aa)` }}
          />

          {/* Point nodes */}
          {points.map((p, idx) => {
            const pSpring = spring({
              frame: Math.max(0, frame - 10 - idx * 3),
              fps,
              config: { damping: 10, mass: 0.4 },
            });
            return (
              <g key={idx} opacity={pSpring} transform={`scale(${pSpring})`} transform-origin={`${p.x}px ${p.y}px`}>
                <circle cx={p.x} cy={p.y} r={9} fill={theme.bg} stroke={theme.primary} strokeWidth="4" />
                <text
                  x={p.x}
                  y={p.y - 18}
                  fill={theme.text}
                  fontSize="20"
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {p.value}
                </text>
                <text
                  x={p.x}
                  y={chartH - 8}
                  fill={theme.text_muted}
                  fontSize="18"
                  fontWeight="500"
                  textAnchor="middle"
                >
                  {p.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </AbsoluteFill>
  );
};
