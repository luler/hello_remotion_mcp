import React from "react";
import { AbsoluteFill } from "remotion";
import UserVideo from "./user/Video";

export interface CodeWrapperProps {
  inputProps?: Record<string, any>;
}

export const CodeWrapper: React.FC<CodeWrapperProps> = ({ inputProps = {} }) => {
  return (
    <AbsoluteFill>
      <UserVideo {...inputProps} />
    </AbsoluteFill>
  );
};
