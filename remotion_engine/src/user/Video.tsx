import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export default function Video() {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  const opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0b0f19",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div
        style={{
          fontSize: 72,
          fontWeight: 800,
          color: "#38bdf8",
          opacity,
          transform: `scale(${scale})`,
          textShadow: "0 0 40px rgba(56, 189, 248, 0.4)",
        }}
      >
        Next-Gen Video
      </div>
      <div
        style={{
          marginTop: 20,
          fontSize: 28,
          color: "#94a3b8",
          opacity: interpolate(frame, [15, 35], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Powered by Remotion 4.x & MCP
      </div>
    </AbsoluteFill>
  );
}