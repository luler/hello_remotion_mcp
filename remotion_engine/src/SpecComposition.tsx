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

export interface SceneConfig {
  type: string;
  duration?: number; // in seconds
  durationInFrames?: number;
  [key: string]: any;
}

export interface SpecData {
  title?: string;
  theme?: string;
  platform?: string;
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

      {/* Dynamic Ambient Aura Lighting */}
      <div
        style={{
          position: "absolute",
          left: auraX1 - 350,
          top: auraY1 - 350,
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.primary}22 0%, transparent 70%)`,
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
          background: `radial-gradient(circle, ${theme.secondary}18 0%, transparent 70%)`,
          filter: "blur(80px)",
          pointerEvents: "none",
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

  // Entrance & exit transition opacity
  let opacity = 1;
  let transform = "none";

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
      const x = interpolate(frame, [0, transDuration], [60, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      transform = `translateX(${x}px)`;
      opacity = interpolate(frame, [0, transDuration], [0, 1]);
    }
    if (!isLast && frame > durationInFrames - transDuration) {
      const x = interpolate(
        frame,
        [durationInFrames - transDuration, durationInFrames],
        [0, -60],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
      transform = `translateX(${x}px)`;
      opacity = interpolate(
        frame,
        [durationInFrames - transDuration, durationInFrames],
        [1, 0]
      );
    }
  }

  const type = (scene.type || "").toLowerCase();

  return (
    <AbsoluteFill style={{ opacity, transform }}>
      {type === "titlescene" && (
        <TitleScene
          title={scene.title || "Remotion Video"}
          subtitle={scene.subtitle}
          badge={scene.badge}
          variant={scene.variant}
          animation={scene.animation}
          theme={theme}
        />
      )}
      {type === "barchart" && (
        <BarChart title={scene.title} data={scene.data || []} theme={theme} />
      )}
      {type === "horizontalbarchart" && (
        <HorizontalBarChart title={scene.title} data={scene.data || []} theme={theme} />
      )}
      {(type === "piechart" || type === "donutchart") && (
        <PieChart title={scene.title} data={scene.data || []} theme={theme} />
      )}
      {type === "linechart" && (
        <LineChart title={scene.title} data={scene.data || []} theme={theme} />
      )}
      {type === "codeblock" && (
        <CodeBlock
          title={scene.title}
          filename={scene.filename}
          code={scene.code || ""}
          language={scene.language}
          isTyping={scene.isTyping !== false}
          theme={theme}
        />
      )}
      {type === "textoverlay" && (
        <TextOverlay
          headline={scene.headline || scene.title || ""}
          subheadline={scene.subheadline || scene.subtitle}
          style={scene.style}
          theme={theme}
        />
      )}
      {type === "endscreen" && (
        <EndScreen
          title={scene.title}
          channel={scene.channel}
          cta={scene.cta}
          social={scene.social}
          theme={theme}
        />
      )}
      {(type === "comparisoncard" || type === "comparison") && (
        <ComparisonCard
          title={scene.title}
          subtitle={scene.subtitle}
          left={scene.left}
          right={scene.right}
          theme={theme}
        />
      )}
      {(type === "metriccard" || type === "counter" || type === "metrics") && (
        <MetricCard
          title={scene.title}
          subtitle={scene.subtitle}
          metrics={scene.metrics || scene.data}
          theme={theme}
        />
      )}
      {(type === "timeline" || type === "roadmap") && (
        <Timeline
          title={scene.title}
          subtitle={scene.subtitle}
          items={scene.items || scene.milestones}
          theme={theme}
        />
      )}
      {(type === "featurelist" || type === "features") && (
        <FeatureList
          title={scene.title}
          subtitle={scene.subtitle}
          features={scene.features || scene.items}
          columns={scene.columns}
          theme={theme}
        />
      )}
      {(type === "quotecard" || type === "quote") && (
        <QuoteCard
          quote={scene.quote || scene.title}
          author={scene.author}
          role={scene.role}
          company={scene.company}
          badge={scene.badge}
          theme={theme}
        />
      )}
    </AbsoluteFill>
  );
};
