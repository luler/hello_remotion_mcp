export interface ThemeColors {
  name: string;
  label: string;
  isDark: boolean;
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
  card_shadow: string;
}

export type ThemeConfig = ThemeColors;

const RAW_THEMES: Record<string, Omit<ThemeColors, "surface" | "muted">> = {
  // ==================== 8 款主流沉浸暗色系 (Dark Themes) ====================
  tech: {
    name: "tech",
    label: "前沿科技 (Tech Slate)",
    isDark: true,
    bg: "#090d16",
    card_bg: "rgba(22, 30, 46, 0.85)",
    primary: "#38bdf8",
    secondary: "#818cf8",
    accent: "#06b6d4",
    text: "#f8fafc",
    text_muted: "#94a3b8",
    border: "rgba(56, 189, 248, 0.25)",
    glow: "rgba(56, 189, 248, 0.35)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(56, 189, 248, 0.2)",
  },
  cyberpunk: {
    name: "cyberpunk",
    label: "赛博霓虹 (Cyberpunk)",
    isDark: true,
    bg: "#080312",
    card_bg: "rgba(30, 10, 50, 0.8)",
    primary: "#f43f5e",
    secondary: "#a855f7",
    accent: "#06b6d4",
    text: "#ffffff",
    text_muted: "#c084fc",
    border: "rgba(244, 63, 94, 0.4)",
    glow: "rgba(244, 63, 94, 0.5)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px rgba(244, 63, 94, 0.3)",
  },
  finance: {
    name: "finance",
    label: "金融商业 (Finance Navy)",
    isDark: true,
    bg: "#06101e",
    card_bg: "rgba(15, 29, 53, 0.85)",
    primary: "#10b981",
    secondary: "#f59e0b",
    accent: "#3b82f6",
    text: "#f1f5f9",
    text_muted: "#94a3b8",
    border: "rgba(16, 185, 129, 0.3)",
    glow: "rgba(16, 185, 129, 0.35)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.55), 0 0 35px rgba(16, 185, 129, 0.2)",
  },
  minimal: {
    name: "minimal",
    label: "极简高级黑 (Minimal Dark)",
    isDark: true,
    bg: "#121214",
    card_bg: "rgba(28, 28, 32, 0.9)",
    primary: "#f4f4f5",
    secondary: "#a1a1aa",
    accent: "#71717a",
    text: "#ffffff",
    text_muted: "#a1a1aa",
    border: "rgba(255, 255, 255, 0.15)",
    glow: "rgba(255, 255, 255, 0.15)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.6)",
  },
  business: {
    name: "business",
    label: "商务深蓝 (Corporate Blue)",
    isDark: true,
    bg: "#0b192c",
    card_bg: "rgba(30, 62, 98, 0.8)",
    primary: "#2563eb",
    secondary: "#60a5fa",
    accent: "#38bdf8",
    text: "#ffffff",
    text_muted: "#cbd5e1",
    border: "rgba(37, 99, 235, 0.3)",
    glow: "rgba(37, 99, 235, 0.4)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(37, 99, 235, 0.25)",
  },
  education: {
    name: "education",
    label: "深翠学院 (Teal Mint)",
    isDark: true,
    bg: "#042023",
    card_bg: "rgba(8, 48, 52, 0.85)",
    primary: "#2dd4bf",
    secondary: "#fbbf24",
    accent: "#14b8a6",
    text: "#f0fdfa",
    text_muted: "#99f6e4",
    border: "rgba(45, 212, 191, 0.3)",
    glow: "rgba(45, 212, 191, 0.35)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(45, 212, 191, 0.2)",
  },
  lifestyle: {
    name: "lifestyle",
    label: "活力潮流 (Sunset Coral)",
    isDark: true,
    bg: "#1c0d12",
    card_bg: "rgba(48, 20, 30, 0.85)",
    primary: "#fb7185",
    secondary: "#fb923c",
    accent: "#f43f5e",
    text: "#fff1f2",
    text_muted: "#fecdd3",
    border: "rgba(251, 113, 133, 0.35)",
    glow: "rgba(251, 113, 133, 0.4)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(251, 113, 133, 0.25)",
  },
  gaming: {
    name: "gaming",
    label: "电竞先锋 (Gaming Emerald)",
    isDark: true,
    bg: "#050b06",
    card_bg: "rgba(10, 26, 12, 0.85)",
    primary: "#22c55e",
    secondary: "#eab308",
    accent: "#ef4444",
    text: "#f0fdf4",
    text_muted: "#86efac",
    border: "rgba(34, 197, 94, 0.35)",
    glow: "rgba(34, 197, 94, 0.45)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px rgba(34, 197, 94, 0.3)",
  },

  // ==================== 8 款主流清新明亮浅色系 (Light Themes) ====================
  clean_white: {
    name: "clean_white",
    label: "苹果极简白 (Clean White)",
    isDark: false,
    bg: "#f8fafc",
    card_bg: "#ffffff",
    primary: "#0284c7",
    secondary: "#6366f1",
    accent: "#0ea5e9",
    text: "#0f172a",
    text_muted: "#64748b",
    border: "rgba(203, 213, 225, 0.8)",
    glow: "rgba(2, 132, 199, 0.12)",
    card_shadow: "0 15px 40px rgba(15, 23, 42, 0.07), 0 2px 8px rgba(15, 23, 42, 0.04)",
  },
  notion_light: {
    name: "notion_light",
    label: "Notion 纸墨暖白 (Notion Paper)",
    isDark: false,
    bg: "#faf7f2",
    card_bg: "#ffffff",
    primary: "#d97706",
    secondary: "#b45309",
    accent: "#ea580c",
    text: "#1c1917",
    text_muted: "#78716c",
    border: "rgba(214, 211, 209, 0.8)",
    glow: "rgba(217, 119, 6, 0.12)",
    card_shadow: "0 15px 40px rgba(41, 37, 36, 0.06), 0 2px 8px rgba(41, 37, 36, 0.03)",
  },
  academic_light: {
    name: "academic_light",
    label: "高等学术雅白 (Academic Emerald)",
    isDark: false,
    bg: "#f4fbf7",
    card_bg: "#ffffff",
    primary: "#059669",
    secondary: "#0d9488",
    accent: "#d97706",
    text: "#064e3b",
    text_muted: "#4b5563",
    border: "rgba(167, 243, 208, 0.85)",
    glow: "rgba(5, 150, 105, 0.12)",
    card_shadow: "0 15px 40px rgba(6, 78, 59, 0.06), 0 2px 8px rgba(6, 78, 59, 0.03)",
  },
  corporate_light: {
    name: "corporate_light",
    label: "商务咨询雅白 (Corporate Clean)",
    isDark: false,
    bg: "#f1f5f9",
    card_bg: "#ffffff",
    primary: "#1d4ed8",
    secondary: "#0284c7",
    accent: "#0891b2",
    text: "#1e293b",
    text_muted: "#64748b",
    border: "rgba(203, 213, 225, 0.9)",
    glow: "rgba(29, 78, 216, 0.12)",
    card_shadow: "0 15px 40px rgba(30, 41, 59, 0.07), 0 2px 8px rgba(30, 41, 59, 0.03)",
  },
  warm_editorial: {
    name: "warm_editorial",
    label: "人文杂志暖调 (Warm Editorial)",
    isDark: false,
    bg: "#fdfbf7",
    card_bg: "#ffffff",
    primary: "#c2410c",
    secondary: "#b45309",
    accent: "#be123c",
    text: "#292524",
    text_muted: "#78716c",
    border: "rgba(231, 229, 228, 0.95)",
    glow: "rgba(194, 65, 12, 0.12)",
    card_shadow: "0 15px 40px rgba(41, 37, 36, 0.06), 0 2px 8px rgba(41, 37, 36, 0.03)",
  },
  fresh_mint: {
    name: "fresh_mint",
    label: "清新薄荷绿 (Fresh Mint)",
    isDark: false,
    bg: "#f0fdf4",
    card_bg: "#ffffff",
    primary: "#10b981",
    secondary: "#06b6d4",
    accent: "#f59e0b",
    text: "#0f172a",
    text_muted: "#64748b",
    border: "rgba(167, 243, 208, 0.85)",
    glow: "rgba(16, 185, 129, 0.12)",
    card_shadow: "0 15px 40px rgba(16, 185, 129, 0.07), 0 2px 8px rgba(16, 185, 129, 0.03)",
  },
  sunset_light: {
    name: "sunset_light",
    label: "活力暖阳 (Sunset Amber)",
    isDark: false,
    bg: "#fffaf5",
    card_bg: "#ffffff",
    primary: "#ea580c",
    secondary: "#f59e0b",
    accent: "#e11d48",
    text: "#1c1917",
    text_muted: "#78716c",
    border: "rgba(254, 215, 170, 0.85)",
    glow: "rgba(234, 88, 12, 0.12)",
    card_shadow: "0 15px 40px rgba(234, 88, 12, 0.07), 0 2px 8px rgba(234, 88, 12, 0.03)",
  },
  lavender_light: {
    name: "lavender_light",
    label: "梦幻香芋紫 (Lavender Dream)",
    isDark: false,
    bg: "#faf5ff",
    card_bg: "#ffffff",
    primary: "#7c3aed",
    secondary: "#c026d3",
    accent: "#ec4899",
    text: "#1e1b4b",
    text_muted: "#6b7280",
    border: "rgba(233, 213, 255, 0.9)",
    glow: "rgba(124, 58, 237, 0.12)",
    card_shadow: "0 15px 40px rgba(124, 58, 237, 0.07), 0 2px 8px rgba(124, 58, 237, 0.03)",
  },

  // ==================== 4 款艺术与品牌定制调性 (Aesthetic & Brand Themes) ====================
  morandi_mist: {
    name: "morandi_mist",
    label: "莫兰迪灰绿 (Morandi Mist)",
    isDark: false,
    bg: "#e9ede9",
    card_bg: "rgba(255, 255, 255, 0.92)",
    primary: "#527365",
    secondary: "#7e9f90",
    accent: "#a38f78",
    text: "#24332c",
    text_muted: "#66776f",
    border: "rgba(126, 159, 144, 0.45)",
    glow: "rgba(82, 115, 101, 0.15)",
    card_shadow: "0 15px 40px rgba(36, 51, 44, 0.06), 0 2px 8px rgba(36, 51, 44, 0.03)",
  },
  luxury_gold: {
    name: "luxury_gold",
    label: "黑金奢华 (Luxury Black Gold)",
    isDark: true,
    bg: "#0c0d10",
    card_bg: "rgba(24, 25, 30, 0.92)",
    primary: "#d4af37",
    secondary: "#f3e5ab",
    accent: "#e5c158",
    text: "#ffffff",
    text_muted: "#c5b8a5",
    border: "rgba(212, 175, 55, 0.35)",
    glow: "rgba(212, 175, 55, 0.35)",
    card_shadow: "0 20px 50px rgba(0, 0, 0, 0.7), 0 0 35px rgba(212, 175, 55, 0.2)",
  },
  tiffany_cyan: {
    name: "tiffany_cyan",
    label: "蒂芙尼水青 (Tiffany Cyan)",
    isDark: false,
    bg: "#eaf7f6",
    card_bg: "#ffffff",
    primary: "#0abab5",
    secondary: "#0284c7",
    accent: "#14b8a6",
    text: "#0c3b39",
    text_muted: "#487a78",
    border: "rgba(10, 186, 181, 0.35)",
    glow: "rgba(10, 186, 181, 0.15)",
    card_shadow: "0 15px 40px rgba(12, 59, 57, 0.06), 0 2px 8px rgba(12, 59, 57, 0.03)",
  },
  retro_film: {
    name: "retro_film",
    label: "复古胶片暖咖 (Retro Film)",
    isDark: false,
    bg: "#f4ede2",
    card_bg: "#ffffff",
    primary: "#8c431d",
    secondary: "#b45309",
    accent: "#c2410c",
    text: "#29180e",
    text_muted: "#785848",
    border: "rgba(180, 83, 9, 0.3)",
    glow: "rgba(140, 67, 29, 0.12)",
    card_shadow: "0 15px 40px rgba(41, 24, 14, 0.06), 0 2px 8px rgba(41, 24, 14, 0.03)",
  },
};

export const THEME_ALIASES: Record<string, string> = {
  // 浅色主题别名映射
  light: "clean_white",
  white: "clean_white",
  apple: "clean_white",
  pure_white: "clean_white",
  notion: "notion_light",
  paper: "notion_light",
  warm: "notion_light",
  warm_white: "notion_light",
  academic: "academic_light",
  university: "academic_light",
  scholar: "academic_light",
  education_light: "academic_light",
  corporate: "corporate_light",
  consulting: "corporate_light",
  business_light: "corporate_light",
  editorial: "warm_editorial",
  magazine: "warm_editorial",
  cream: "warm_editorial",
  mint: "fresh_mint",
  fresh: "fresh_mint",
  nature: "fresh_mint",
  sunset: "sunset_light",
  orange: "sunset_light",
  sunshine: "sunset_light",
  lavender: "lavender_light",
  purple_light: "lavender_light",
  dream: "lavender_light",

  // 艺术与品牌定制别名映射
  morandi: "morandi_mist",
  morandi_green: "morandi_mist",
  mist: "morandi_mist",
  gold: "luxury_gold",
  black_gold: "luxury_gold",
  luxury: "luxury_gold",
  tiffany: "tiffany_cyan",
  tiffany_blue: "tiffany_cyan",
  cyan: "tiffany_cyan",
  retro: "retro_film",
  film: "retro_film",
  vintage: "retro_film",
  coffee: "retro_film",

  // 深色主题别名映射
  dark: "tech",
  slate: "tech",
  neon: "cyberpunk",
  crypto: "finance",
  dark_minimal: "minimal",
  black: "minimal",
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

/**
 * 判断十六进制颜色是否属于深色
 */
function isColorDark(hex?: string): boolean {
  if (!hex || typeof hex !== "string") return true;
  const cleanHex = hex.replace("#", "").trim();
  if (cleanHex.length === 3) {
    const r = parseInt(cleanHex[0] + cleanHex[0], 16);
    const g = parseInt(cleanHex[1] + cleanHex[1], 16);
    const b = parseInt(cleanHex[2] + cleanHex[2], 16);
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140;
  }
  if (cleanHex.length >= 6) {
    const r = parseInt(cleanHex.substring(0, 2), 16);
    const g = parseInt(cleanHex.substring(2, 4), 16);
    const b = parseInt(cleanHex.substring(4, 6), 16);
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140;
  }
  return true;
}

/**
 * 获取或自适应解析主题配置
 * - 支持直接传主题名字符串（包括内置 16 大主题及常见别名）
 * - 支持传自定义 Theme 对象，按背景色深浅智能推导并补全预设参数
 */
export function getTheme(themeInput?: string | Partial<ThemeColors>): ThemeColors {
  if (!themeInput) {
    return THEMES.tech;
  }

  // 1. 若传入自定义对象
  if (typeof themeInput === "object" && themeInput !== null) {
    const isDark = themeInput.isDark !== undefined
      ? themeInput.isDark
      : isColorDark(themeInput.bg);
    const base = isDark ? THEMES.tech : THEMES.clean_white;

    return {
      name: themeInput.name || (isDark ? "custom_dark" : "custom_light"),
      label: themeInput.label || (isDark ? "自定义暗色" : "自定义明亮"),
      isDark,
      bg: themeInput.bg || base.bg,
      card_bg: themeInput.card_bg || themeInput.surface || base.card_bg,
      surface: themeInput.surface || themeInput.card_bg || base.surface,
      primary: themeInput.primary || base.primary,
      secondary: themeInput.secondary || base.secondary,
      accent: themeInput.accent || base.accent,
      text: themeInput.text || base.text,
      text_muted: themeInput.text_muted || themeInput.muted || base.text_muted,
      muted: themeInput.muted || themeInput.text_muted || base.muted,
      border: themeInput.border || base.border,
      glow: themeInput.glow || base.glow,
      card_shadow: themeInput.card_shadow || base.card_shadow,
    };
  }

  // 2. 若传入字符串主题名或别名
  if (typeof themeInput === "string") {
    const key = themeInput.toLowerCase().trim();
    if (THEMES[key]) {
      return THEMES[key];
    }
    const aliased = THEME_ALIASES[key];
    if (aliased && THEMES[aliased]) {
      return THEMES[aliased];
    }
  }

  return THEMES.tech;
}
