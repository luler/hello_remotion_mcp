import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export default function Video(props: any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(entrance, [0, 1], [0.85, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#090d16",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div
        style={{
          fontSize: 72,
          fontWeight: 900,
          color: "#38bdf8",
          opacity,
          transform: `scale(${scale})`,
          textShadow: "0 0 50px rgba(56, 189, 248, 0.4)",
        }}
      >
        {props?.title || "Hello Remotion MCP"}
      </div>
      <div
        style={{
          marginTop: 24,
          fontSize: 28,
          color: "#94a3b8",
          opacity: interpolate(frame, [15, 35], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Custom React Video Component
      </div>
    </AbsoluteFill>
  );
}
