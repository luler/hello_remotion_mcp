import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThemeConfig } from "../themes";
import { resolveLucideIcon } from "./iconHelper";

export interface MetricItem {
  label: string;
  value: number | string;
  prefix?: string;
  suffix?: string;
  change?: string;
  changeLabel?: string;
  changeType?: "up" | "down" | "neutral";
  isPositive?: boolean;
  description?: string;
  helperText?: string;
  icon?: string;
}

export interface MetricCardProps {
  title?: string;
  subtitle?: string;
  metrics?: MetricItem[];
  theme: ThemeConfig;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title = "核心数据与业务指标",
  subtitle = "Key Metrics & Performance Overview",
  metrics = [
    { label: "月活跃用户", value: 1250000, suffix: "+", change: "+148% YoY", changeType: "up", description: "覆盖全球 120+ 国家与地区" },
    { label: "视频渲染耗时", value: 1.8, suffix: "s", prefix: "< ", change: "-65% 降时", changeType: "up", description: "全异步并发调度引擎加速" },
    { label: "系统可用性", value: 99.99, suffix: "%", change: "SLA 保障", changeType: "neutral", description: "分布式弹性高可用集群" },
  ],
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const titleProg = spring({ frame, fps, config: { damping: 14 } });
  const titleY = interpolate(titleProg, [0, 1], [-30, 0]);
  const titleOp = interpolate(titleProg, [0, 1], [0, 1]);

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
      {/* 标题 */}
      <div
        style={{
          textAlign: "center",
          marginBottom: isWide ? "3.5rem" : "2rem",
          transform: `translateY(${titleY}px)`,
          opacity: titleOp,
        }}
      >
        <h1 style={{ fontSize: isWide ? "3.2rem" : "2.2rem", fontWeight: 800, color: theme.text, margin: 0 }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{ fontSize: isWide ? "1.35rem" : "1.05rem", color: theme.muted, marginTop: "0.6rem", margin: "0.6rem 0 0 0" }}>
            {subtitle}
          </p>
        )}
      </div>

      {/* 指标卡片网格 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: isWide ? `repeat(${Math.min(metrics.length, 3)}, 1fr)` : "1fr",
          gap: isWide ? "2.5rem" : "1.2rem",
          width: "100%",
          maxWidth: isWide ? "1300px" : "680px",
        }}
      >
        {metrics.map((m, idx) => (
          <SingleMetric
            key={idx}
            metric={m}
            idx={idx}
            theme={theme}
            frame={frame}
            fps={fps}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};

const SingleMetric: React.FC<{
  metric: MetricItem;
  idx: number;
  theme: ThemeConfig;
  frame: number;
  fps: number;
}> = ({ metric, idx, theme, frame, fps }) => {
  const prog = spring({
    frame: frame - 8 - idx * 5,
    fps,
    config: { damping: 14, stiffness: 100 },
  });
  const scale = interpolate(prog, [0, 1], [0.9, 1]);
  const opacity = interpolate(prog, [0, 1], [0, 1]);

  // 数字滚动动画
  let displayValue: string | number = metric.value;
  if (typeof metric.value === "number") {
    const isInt = Number.isInteger(metric.value);
    const countProg = spring({
      frame: frame - 12 - idx * 5,
      fps,
      config: { damping: 18, stiffness: 80 },
    });
    const curr = interpolate(countProg, [0, 1], [0, metric.value]);
    if (isInt) {
      displayValue = Math.round(curr).toLocaleString("en-US");
    } else {
      displayValue = curr.toFixed(2);
    }
  }

  const changeVal = metric.change || metric.changeLabel;
  const descVal = metric.description || metric.helperText;
  const computedChangeType =
    metric.changeType ||
    (metric.isPositive === true ? "up" : metric.isPositive === false ? "down" : "neutral");

  const changeColor =
    computedChangeType === "down" ? "#ef4444" : computedChangeType === "up" ? theme.accent : theme.muted;

  return (
    <div
      style={{
        background: theme.surface,
        border: `1px solid ${theme.border}`,
        borderRadius: "20px",
        padding: "2.4rem 2rem",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxShadow: `0 10px 30px rgba(0,0,0,0.35)`,
        transform: `scale(${scale})`,
        opacity,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "4px",
          background: `linear-gradient(90deg, ${theme.primary}, ${theme.accent})`,
        }}
      />

      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
          <span style={{ fontSize: "1.15rem", color: theme.muted, fontWeight: 500 }}>
            {metric.label}
          </span>
          {metric.icon && (
            <div style={{ color: theme.primary, display: "flex", alignItems: "center" }}>
              {(() => {
                const Icon = resolveLucideIcon(metric.icon);
                return Icon ? <Icon size={20} color={theme.primary} strokeWidth={2} /> : metric.icon;
              })()}
            </div>
          )}
        </div>
        <div
          style={{
            fontSize: "3.6rem",
            fontWeight: 800,
            color: theme.text,
            letterSpacing: "-0.03em",
            lineHeight: 1.1,
            display: "flex",
            alignItems: "baseline",
            gap: "0.2rem",
          }}
        >
          {metric.prefix && (
            <span style={{ fontSize: "2.2rem", color: theme.primary, fontWeight: 700 }}>
              {metric.prefix}
            </span>
          )}
          <span>{displayValue}</span>
          {metric.suffix && (
            <span style={{ fontSize: "2rem", color: theme.accent, fontWeight: 700 }}>
              {metric.suffix}
            </span>
          )}
        </div>
      </div>

      <div style={{ marginTop: "1.6rem" }}>
        {changeVal && (
          <span
            style={{
              display: "inline-block",
              padding: "0.3rem 0.75rem",
              borderRadius: "6px",
              background: `${changeColor}1a`,
              color: changeColor,
              fontSize: "0.95rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            {changeVal}
          </span>
        )}
        {descVal && (
          <p style={{ fontSize: "0.95rem", color: theme.muted, margin: "0.4rem 0 0 0", lineHeight: 1.4 }}>
            {descVal}
          </p>
        )}
      </div>
    </div>
  );
};
