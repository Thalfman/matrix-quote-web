import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0B1F3A",
          600: "#15305B",
          700: "#0E2238",
          800: "#091729",
          900: "#0A1729",
        },
        steel: {
          100: "#E8ECF0",
          200: "#CDD4DC",
          300: "#A9B6C3",
          400: "#7D91A2",
          500: "#546D82",
          600: "#3A5166",
          700: "#263D50",
        },
        // Signature electric-blue — the single brand accent (replaces amber).
        brand: {
          DEFAULT: "#2563EB",
          hover:   "#1D4ED8",
          pressed: "#1E40AF",
          subtle:  "#DBEAFE",
          foreground: "#FFFFFF",
        },
        // Semantic tokens (light + dark aware via `dark:` variants).
        bg: {
          DEFAULT: "#F6F8FB",
          dark:    "#0A1220",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          dark:    "#0F1B30",
        },
        ink: {
          DEFAULT: "#0F172A",
          dark:    "#E2E8F0",
        },
        muted: {
          DEFAULT: "#475569",
          dark:    "#94A3B8",
        },
        border: {
          DEFAULT: "#E2E8F0",
          dark:    "#1E293B",
        },
        accent: {
          DEFAULT: "#2563EB",
          foreground: "#FFFFFF",
        },
        success: "#0F766E",
        warning: "#B45309",
        danger:  "#B91C1C",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        display: ["56px", { lineHeight: "60px", fontWeight: "600", letterSpacing: "-0.02em" }],
      },
      maxWidth: {
        content: "1200px",
      },
    },
  },
  plugins: [],
};

export default config;
