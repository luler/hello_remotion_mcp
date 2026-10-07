import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { getTheme } from "./themes";
import { TitleScene } from "./components/TitleScene";
import { BarChart } from "./components/BarChart";
import { HorizontalBarChart } from "./components/HorizontalBarChart";
import { PieChart } from "./components/PieChart";
import { LineChart } from "./components/LineChart";
import { CodeBlock } from "./components/CodeBlock";
import { TextOverlay } from "./components/TextOverlay";
import { EndScreen } from "./components/EndScreen";
import { ComparisonCard } from "./components/ComparisonCard";
import { MetricCard } from "./components/MetricCard";
import { Timeline } from "./components/Timeline";
import { FeatureList } from "./components/FeatureList";
import { QuoteCard } from "./components/QuoteCard";
import { BrandInkOpen } from "./shots/typography/brand-ink-open/BrandInkOpen";
import { MarkerUnderlineTitle } from "./shots/typography/marker-underline-title/MarkerUnderlineTitle";

export interface SceneConfig {
  type: string;
  duration?: number; // in seconds
  durationInFrames?: number;
  [key: string]: any;
}

export interface SpecData {
  title?: string;
  theme?: string | Record<string, any>;
  platform?: string;
  width?: number;
  height?: number;
  fps?: number;
  audioUrl?: string;
  bgm?: string;
  audioVolume?: number;
  scenes?: SceneConfig[];
  transition?: {
    type?: "fade" | "slide" | "none";
    durationFrames?: number;
  };
}

export interface SpecCompositionProps {
  spec?: SpecData;
}

export const SpecComposition: React.FC<SpecCompositionProps> = ({ spec = {} }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const theme = getTheme(spec.theme);
  const scenes = spec.scenes && spec.scenes.length > 0 ? spec.scenes : [
    {
      type: "TitleScene",
      title: spec.title || "Remotion Studio",
      subtitle: "AI Video Creation via MCP",
      duration: 4,
    },
  ];

  const transType = spec.transition?.type || "fade";
  const transDuration = spec.transition?.durationFrames || 12;

  // Background subtle ambient light movement
  const auraX1 = Math.sin(frame * 0.02) * 150 + width * 0.3;
  const auraY1 = Math.cos(frame * 0.02) * 100 + height * 0.4;
  const auraX2 = Math.cos(frame * 0.015) * 150 + width * 0.7;
  const auraY2 = Math.sin(frame * 0.015) * 100 + height * 0.6;

  const totalFrames = scenes.reduce(
    (acc, s) => acc + (s.durationInFrames || Math.round((s.duration || 3.5) * fps)),
    0
  );

  let currentStartFrame = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg, overflow: "hidden" }}>
      {/* Background Audio / BGM */}
      {(spec.audioUrl || spec.bgm) && (
        <Audio
          src={spec.audioUrl || spec.bgm || ""}
          volume={(f) => {
            const vol = spec.audioVolume ?? 0.6;
            return interpolate(
              f,
              [Math.max(0, totalFrames - 30), totalFrames],
              [vol, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
          }}
        />
      )}

      {/* Dynamic Ambient Aura Lighting (Subtle in light mode, glowing in dark mode) */}
      <div
        style={{
          position: "absolute",
          left: auraX1 - 350,
          top: auraY1 - 350,
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.primary}${theme.isDark ? "22" : "12"} 0%, transparent 70%)`,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: auraX2 - 400,
          top: auraY2 - 400,
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.secondary}${theme.isDark ? "18" : "0d"} 0%, transparent 70%)`,
          filter: "blur(80px)",
          pointerEvents: "none",
        }}
      />

      {/* Cinematic Vignette Overlay: Dark mode gets edge focus, light mode gets ultra-subtle edge */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: theme.isDark
            ? "radial-gradient(ellipse at center, transparent 60%, rgba(0, 0, 0, 0.42) 100%)"
            : "radial-gradient(ellipse at center, transparent 75%, rgba(0, 0, 0, 0.04) 100%)",
          pointerEvents: "none",
          zIndex: 80,
        }}
      />

      {/* Render each scene in sequence */}
      {scenes.map((scene, idx) => {
        const sceneDurationFrames =
          scene.durationInFrames || Math.round((scene.duration || 3.5) * fps);
        const start = currentStartFrame;
        currentStartFrame += sceneDurationFrames;

        return (
          <Sequence
            key={idx}
            from={start}
            durationInFrames={sceneDurationFrames}
            name={`Scene_${idx + 1}_${scene.type}`}
          >
            <SceneWrapper
              scene={scene}
              theme={theme}
              durationInFrames={sceneDurationFrames}
              transType={transType}
              transDuration={transDuration}
              isFirst={idx === 0}
              isLast={idx === scenes.length - 1}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const SceneWrapper: React.FC<{
  scene: SceneConfig;
  theme: any;
  durationInFrames: number;
  transType: string;
  transDuration: number;
  isFirst: boolean;
  isLast: boolean;
}> = ({
  scene,
  theme,
  durationInFrames,
  transType,
  transDuration,
  isFirst,
  isLast,
}) => {
  const frame = useCurrentFrame();

  // Entrance & exit transition opacity & offset
  let opacity = 1;
  let transX = 0;

  if (transType === "fade") {
    if (!isFirst && frame < transDuration) {
      opacity = interpolate(frame, [0, transDuration], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }
    if (!isLast && frame > durationInFrames - transDuration) {
      opacity = interpolate(
        frame,
        [durationInFrames - transDuration, durationInFrames],
        [1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
    }
  } else if (transType === "slide") {
    if (!isFirst && frame < transDuration) {
      transX = interpolate(frame, [0, transDuration], [60, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      opacity = interpolate(frame, [0, transDuration], [0, 1]);
    }
    if (!isLast && frame > durationInFrames - transDuration) {
      transX = interpolate(
        frame,
        [durationInFrames - transDuration, durationInFrames],
        [0, -60],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
      opacity = interpolate(
        frame,
        [durationInFrames - transDuration, durationInFrames],
        [1, 0]
      );
    }
  }

  // --- Cinematic Camera Motion (Continuous Push / Drift to eliminate PPT stiffness) ---
  const cameraMotion = scene.cameraMotion || scene.camera || "push_in";
  let cameraScale = 1.0;
  let cameraDriftX = 0;

  if (cameraMotion === "push_in") {
    // 1.00 -> 1.035 over the entire scene duration
    cameraScale = interpolate(frame, [0, durationInFrames], [1.0, 1.035], {
      extrapolateRight: "clamp",
    });
  } else if (cameraMotion === "pull_out") {
    cameraScale = interpolate(frame, [0, durationInFrames], [1.035, 1.0], {
      extrapolateRight: "clamp",
    });
  } else if (cameraMotion === "drift_right") {
    cameraScale = 1.02;
    cameraDriftX = interpolate(frame, [0, durationInFrames], [-15, 15], {
      extrapolateRight: "clamp",
    });
  } else if (cameraMotion === "drift_left") {
    cameraScale = 1.02;
    cameraDriftX = interpolate(frame, [0, durationInFrames], [15, -15], {
      extrapolateRight: "clamp",
    });
  } else if (cameraMotion === "none" || cameraMotion === "static") {
    cameraScale = 1.0;
  }

  const finalTransform = `translate3d(${transX + cameraDriftX}px, 0, 0) scale(${cameraScale})`;

  // --- Relaxed Synonyms Normalization ---
  const title = (scene.title || scene.headline || scene.wordmark || scene.name || "").trim();
  const subtitle = (scene.subtitle || scene.subheadline || scene.kicker || scene.desc || scene.description || "").trim();
  const badge = (scene.badge || scene.tag || scene.category || "").trim();
  const rawList = scene.features || scene.metrics || scene.data || scene.items || scene.milestones || [];

  // Normalized list for feature list
  const normalizedFeatures = (scene.features || rawList || []).map((f: any) => ({
    title: f.title || f.name || f.label || "",
    description: f.description || f.desc || f.text || "",
    badge: f.badge || f.tag,
    icon: f.icon,
  }));

  // Normalized list for charts
  const normalizedChartData = (scene.data || rawList || []).map((d: any) => ({
    label: d.label || d.name || d.title || "",
    value: Number(d.value ?? d.val ?? d.count ?? 0),
  }));

  // Normalized list for metrics
  const normalizedMetrics = (scene.metrics || rawList || []).map((m: any) => ({
    label: m.label || m.title || m.name || "",
    value: m.value ?? m.val ?? 0,
    prefix: m.prefix,
    suffix: m.suffix,
    change: m.change,
    changeLabel: m.changeLabel || m.trend,
    isPositive: m.isPositive !== false,
    helperText: m.helperText || m.desc || m.description,
  }));

  // Normalized list for timeline
  const normalizedTimeline = (scene.items || scene.milestones || rawList || []).map((t: any) => ({
    date: t.date || t.time || t.year || "",
    title: t.title || t.name || "",
    description: t.description || t.desc || "",
    badge: t.badge || t.tag,
    active: t.active ?? false,
  }));

  // --- Scene-level Theme & Color Overrides (Allows fine-grained text, title, and brand customization) ---
  const effectiveTheme = React.useMemo(() => {
    let base = theme;
    if (scene.theme) {
      base = typeof scene.theme === "string" ? getTheme(scene.theme) : getTheme({ ...theme, ...scene.theme });
    }
    const overrides: any = {};
    if (scene.textColor || scene.titleColor || scene.color) {
      overrides.text = scene.titleColor || scene.textColor || scene.color;
    }
    if (scene.subtitleColor || scene.descColor || scene.mutedColor) {
      overrides.text_muted = scene.subtitleColor || scene.descColor || scene.mutedColor;
      overrides.muted = overrides.text_muted;
    }
    if (scene.primary || scene.primaryColor || scene.highlightColor) {
      overrides.primary = scene.primaryColor || scene.primary || scene.highlightColor;
    }
    if (scene.secondary || scene.secondaryColor) {
      overrides.secondary = scene.secondaryColor || scene.secondary;
    }
    if (scene.accent || scene.accentColor) {
      overrides.accent = scene.accentColor || scene.accent;
    }
    if (scene.bg || scene.backgroundColor) {
      overrides.bg = scene.bg || scene.backgroundColor;
    }
    if (scene.card_bg || scene.cardBg || scene.surface) {
      overrides.card_bg = scene.card_bg || scene.cardBg || scene.surface;
      overrides.surface = overrides.card_bg;
    }
    if (Object.keys(overrides).length > 0) {
      return getTheme({ ...base, ...overrides });
    }
    return base;
  }, [theme, scene]);

  const type = (scene.type || "").toLowerCase().replace(/[-_\s]+/g, "");
  const hasCustomBg = Boolean(scene.bg || scene.backgroundColor || scene.theme);

  return (
    <AbsoluteFill style={{ opacity, transform: finalTransform, backgroundColor: hasCustomBg ? effectiveTheme.bg : undefined }}>
      {(type === "titlescene" || type === "title" || type === "intro") && (
        <TitleScene
          title={title || "Remotion Video"}
          subtitle={subtitle}
          badge={badge}
          variant={scene.variant}
          animation={scene.animation}
          theme={effectiveTheme}
        />
      )}
      {(type === "barchart" || type === "bar") && (
        <BarChart title={title} data={normalizedChartData} theme={effectiveTheme} />
      )}
      {(type === "horizontalbarchart" || type === "hbar" || type === "ranking" || type === "rank") && (
        <HorizontalBarChart title={title} data={normalizedChartData} theme={effectiveTheme} />
      )}
      {(type === "piechart" || type === "donutchart" || type === "pie" || type === "donut") && (
        <PieChart title={title} data={normalizedChartData} theme={effectiveTheme} />
      )}
      {(type === "linechart" || type === "line" || type === "trend") && (
        <LineChart title={title} data={normalizedChartData} theme={effectiveTheme} />
      )}
      {(type === "codeblock" || type === "code") && (
        <CodeBlock
          title={title}
          filename={scene.filename}
          code={scene.code || ""}
          language={scene.language}
          isTyping={scene.isTyping !== false}
          theme={effectiveTheme}
        />
      )}
      {(type === "textoverlay" || type === "text") && (
        <TextOverlay
          headline={title}
          subheadline={subtitle}
          style={scene.style}
          theme={effectiveTheme}
        />
      )}
      {(type === "endscreen" || type === "end" || type === "outro") && (
        <EndScreen
          title={title}
          channel={scene.channel}
          cta={scene.cta}
          social={scene.social}
          theme={effectiveTheme}
        />
      )}
      {(type === "comparisoncard" || type === "comparison" || type === "vs") && (
        <ComparisonCard
          title={title}
          subtitle={subtitle}
          left={scene.left}
          right={scene.right}
          vsBadge={scene.vsBadge}
          theme={effectiveTheme}
        />
      )}
      {(type === "metriccard" || type === "metrics" || type === "metric" || type === "counter") && (
        <MetricCard
          title={title}
          subtitle={subtitle}
          metrics={normalizedMetrics}
          theme={effectiveTheme}
        />
      )}
      {(type === "timeline" || type === "roadmap") && (
        <Timeline
          title={title}
          subtitle={subtitle}
          items={normalizedTimeline}
          theme={effectiveTheme}
        />
      )}
      {(type === "featurelist" || type === "features" || type === "feature") && (
        <FeatureList
          title={title}
          subtitle={subtitle}
          features={normalizedFeatures}
          columns={scene.columns}
          theme={effectiveTheme}
        />
      )}
      {(type === "quotecard" || type === "quote") && (
        <QuoteCard
          quote={scene.quote || title}
          author={scene.author}
          role={scene.role || title}
          company={scene.company}
          badge={badge}
          avatar={scene.avatar}
          theme={effectiveTheme}
        />
      )}
      {(type === "brandinkopen" || type === "brandink" || (type === "shot" && (scene.shot === "brand-ink-open" || scene.id === "brand-ink-open"))) && (
        <BrandInkOpen
          wordmark={scene.wordmark || title}
          kicker={scene.kicker || subtitle || badge}
          accent={scene.accent || effectiveTheme.primary}
          theme={effectiveTheme}
        />
      )}
      {(type === "markerunderlinetitle" || type === "markerunderline" || (type === "shot" && (scene.shot === "marker-underline-title" || scene.id === "marker-underline-title"))) && (
        <MarkerUnderlineTitle
          title={title}
          highlight={scene.highlight}
          subtitle={subtitle}
          theme={effectiveTheme}
        />
      )}
    </AbsoluteFill>
  );
};
