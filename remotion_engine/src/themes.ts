export interface ThemeColors {
  name: string;
  label: string;
  bg: string;
  card_bg: string;
  surface: string;
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  text_muted: string;
  muted: string;
  border: string;
  glow: string;
}

export type ThemeConfig = ThemeColors;

const RAW_THEMES = {
  tech: {
    name: "tech",
    label: "前沿科技 (Tech Slate)",
    bg: "#090d16",
    card_bg: "rgba(22, 30, 46, 0.8)",
    primary: "#38bdf8",
    secondary: "#818cf8",
    accent: "#06b6d4",
    text: "#f8fafc",
    text_muted: "#94a3b8",
    border: "rgba(56, 189, 248, 0.25)",
    glow: "rgba(56, 189, 248, 0.35)",
  },
  cyberpunk: {
    name: "cyberpunk",
    label: "赛博霓虹 (Cyberpunk)",
    bg: "#080312",
    card_bg: "rgba(30, 10, 50, 0.75)",
    primary: "#f43f5e",
    secondary: "#a855f7",
    accent: "#06b6d4",
    text: "#ffffff",
    text_muted: "#c084fc",
    border: "rgba(244, 63, 94, 0.4)",
    glow: "rgba(244, 63, 94, 0.5)",
  },
  finance: {
    name: "finance",
    label: "金融商业 (Finance Navy)",
    bg: "#06101e",
    card_bg: "rgba(15, 29, 53, 0.8)",
    primary: "#10b981",
    secondary: "#f59e0b",
    accent: "#3b82f6",
    text: "#f1f5f9",
    text_muted: "#94a3b8",
    border: "rgba(16, 185, 129, 0.3)",
    glow: "rgba(16, 185, 129, 0.35)",
  },
  minimal: {
    name: "minimal",
    label: "极简高级黑 (Minimal Dark)",
    bg: "#121214",
    card_bg: "rgba(28, 28, 32, 0.85)",
    primary: "#f4f4f5",
    secondary: "#a1a1aa",
    accent: "#71717a",
    text: "#ffffff",
    text_muted: "#a1a1aa",
    border: "rgba(255, 255, 255, 0.15)",
    glow: "rgba(255, 255, 255, 0.15)",
  },
  business: {
    name: "business",
    label: "商务深蓝 (Corporate Blue)",
    bg: "#0b192c",
    card_bg: "rgba(30, 62, 98, 0.75)",
    primary: "#2563eb",
    secondary: "#60a5fa",
    accent: "#38bdf8",
    text: "#ffffff",
    text_muted: "#cbd5e1",
    border: "rgba(37, 99, 235, 0.3)",
    glow: "rgba(37, 99, 235, 0.4)",
  },
  education: {
    name: "education",
    label: "知识学院 (Teal Mint)",
    bg: "#042023",
    card_bg: "rgba(8, 48, 52, 0.8)",
    primary: "#2dd4bf",
    secondary: "#fbbf24",
    accent: "#14b8a6",
    text: "#f0fdfa",
    text_muted: "#99f6e4",
    border: "rgba(45, 212, 191, 0.3)",
    glow: "rgba(45, 212, 191, 0.35)",
  },
  lifestyle: {
    name: "lifestyle",
    label: "活力潮流 (Sunset Coral)",
    bg: "#1c0d12",
    card_bg: "rgba(48, 20, 30, 0.8)",
    primary: "#fb7185",
    secondary: "#fb923c",
    accent: "#f43f5e",
    text: "#fff1f2",
    text_muted: "#fecdd3",
    border: "rgba(251, 113, 133, 0.35)",
    glow: "rgba(251, 113, 133, 0.4)",
  },
  gaming: {
    name: "gaming",
    label: "电竞先锋 (Gaming Emerald)",
    bg: "#050b06",
    card_bg: "rgba(10, 26, 12, 0.8)",
    primary: "#22c55e",
    secondary: "#eab308",
    accent: "#ef4444",
    text: "#f0fdf4",
    text_muted: "#86efac",
    border: "rgba(34, 197, 94, 0.35)",
    glow: "rgba(34, 197, 94, 0.45)",
  },
};

export const THEMES: Record<string, ThemeColors> = Object.fromEntries(
  Object.entries(RAW_THEMES).map(([k, v]) => [
    k,
    {
      ...v,
      surface: v.card_bg,
      muted: v.text_muted,
    },
  ])
);

export function getTheme(themeName?: string): ThemeColors {
  if (themeName && THEMES[themeName.toLowerCase()]) {
    return THEMES[themeName.toLowerCase()];
  }
  return THEMES.tech;
}
