import React from "react";
import { AbsoluteFill } from "remotion";
import * as UserModule from "./user/Video";

export interface CodeWrapperProps {
  inputProps?: Record<string, any>;
}

export const CodeWrapper: React.FC<CodeWrapperProps> = ({ inputProps = {} }) => {
  const mod: any = UserModule;
  const Component: any =
    mod.default ||
    mod.Video ||
    mod.App ||
    mod.Main ||
    Object.values(mod).find((v) => typeof v === "function") ||
    (() => null);

  return (
    <AbsoluteFill>
      <Component {...inputProps} />
    </AbsoluteFill>
  );
};

