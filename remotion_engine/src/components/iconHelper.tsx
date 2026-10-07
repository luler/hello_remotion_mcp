import React from "react";
import { icons as lucideIcons } from "lucide-react";

/**
 * 将 "trending-up" / "trendingUp" / "TrendingUp" / "trending_up" 等名称解析为 lucide 图标组件
 */
export const resolveLucideIcon = (name?: string): React.ComponentType<any> | undefined => {
  if (!name || typeof name !== "string") return undefined;
  const pascal = name
    .trim()
    .split(/[-_\s]+/)
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join("");
  return (lucideIcons as Record<string, React.ComponentType<any>>)[pascal];
};
