import React from "react";
import { Composition } from "remotion";
import { SpecComposition, SpecCompositionProps } from "./SpecComposition";
import { CodeWrapper, CodeWrapperProps } from "./CodeWrapper";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 声明式 Spec 场景视频 */}
      <Composition
        id="SpecVideo"
        component={SpecComposition}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          spec: {
            title: "Remotion Studio",
            theme: "tech",
            platform: "youtube",
            fps: 30,
            scenes: [
              {
                type: "TitleScene",
                duration: 4,
                title: "Remotion Studio MCP",
                subtitle: "High-Performance Video Generation",
                badge: "SYSTEM READY",
              },
            ],
          },
        } as SpecCompositionProps}
        calculateMetadata={({ props }) => {
          const spec = (props?.spec || {}) as Record<string, any>;
          const fps = Number(spec.fps) || 30;
          const platform = String(spec.platform || "").toLowerCase();

          let width = 1920;
          let height = 1080;

          if (platform === "tiktok" || platform === "portrait" || platform === "shorts") {
            width = 1080;
            height = 1920;
          } else if (platform === "square" || platform === "instagram_square") {
            width = 1080;
            height = 1080;
          } else if (platform === "instagram_portrait" || platform === "post_4_5") {
            width = 1080;
            height = 1350;
          } else if (platform === "ultrawide" || platform === "21:9") {
            width = 2560;
            height = 1080;
          } else if (platform === "classic_4_3" || platform === "4:3") {
            width = 1440;
            height = 1080;
          }

          // 用户显式指定的任意自定义像素画幅（最高优先级）
          if (spec.width) width = Number(spec.width);
          if (spec.height) height = Number(spec.height);

          let totalFrames = 0;
          if (spec.scenes && Array.isArray(spec.scenes) && spec.scenes.length > 0) {
            for (const s of spec.scenes) {
              totalFrames += Number(s.durationInFrames) || Math.round((Number(s.duration) || 3.5) * fps);
            }
          } else {
            totalFrames = 150;
          }

          return {
            durationInFrames: Math.max(totalFrames, 30),
            fps,
            width,
            height,
          };
        }}
      />

      {/* 自由式 React 代码组件视频 */}
      <Composition
        id="CodeVideo"
        component={CodeWrapper}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          inputProps: {},
        } as CodeWrapperProps}
        calculateMetadata={({ props }) => {
          const p = (props?.inputProps || {}) as Record<string, any>;
          return {
            durationInFrames: Number(p.durationInFrames) || 150,
            fps: Number(p.fps) || 30,
            width: Number(p.width) || 1920,
            height: Number(p.height) || 1080,
          };
        }}
      />
    </>
  );
};
