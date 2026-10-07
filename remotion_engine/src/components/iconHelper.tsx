import React from "react";
import { icons as lucideIcons } from "lucide-react";

const ICON_SYNONYMS: Record<string, string> = {
  "check-circle": "CircleCheck",
  "checkcircle": "CircleCheck",
  "check": "Check",
  "cross": "X",
  "close": "X",
  "warning": "AlertTriangle",
  "alert": "CircleAlert",
  "info": "Info",
  "star": "Star",
  "bolt": "Zap",
  "lightning": "Zap",
  "speed": "Gauge",
  "ai": "Bot",
  "robot": "Bot",
  "fire": "Flame",
  "money": "DollarSign",
  "doc": "FileText",
  "document": "FileText",
  "book": "BookOpen",
};

/**
 * 将 "trending-up" / "trendingUp" / "TrendingUp" / "check-circle" 等名称自适应解析为 lucide 图标组件
 */
export const resolveLucideIcon = (name?: string): React.ComponentType<any> | undefined => {
  if (!name || typeof name !== "string") return undefined;
  const raw = name.trim().toLowerCase();

  if (ICON_SYNONYMS[raw]) {
    const syn = ICON_SYNONYMS[raw];
    if ((lucideIcons as any)[syn]) return (lucideIcons as any)[syn];
  }

  const pascal = name
    .trim()
    .split(/[-_\s]+/)
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase())
    .join("");

  const direct = (lucideIcons as Record<string, React.ComponentType<any>>)[pascal];
  if (direct) return direct;

  // 针对 Lucide 4.x 命名更新（CheckCircle -> CircleCheck）容错
  if (pascal.includes("CheckCircle")) return (lucideIcons as any)["CircleCheck"] || (lucideIcons as any)["Check"];
  if (pascal.includes("AlertCircle")) return (lucideIcons as any)["CircleAlert"] || (lucideIcons as any)["AlertTriangle"];
  if (pascal.includes("HelpCircle")) return (lucideIcons as any)["CircleHelp"] || (lucideIcons as any)["HelpCircle"];

  return undefined;
};
