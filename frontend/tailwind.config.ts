import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#F8F8F6",
          dark: "#0F1013",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          dark: "#17181C",
        },
        ink: {
          DEFAULT: "#0F1013",
          dark: "#F2F2F3",
        },
        muted: {
          DEFAULT: "#5A5D66",
          dark: "#A0A0A8",
        },
        border: {
          DEFAULT: "#E5E5E2",
          dark: "#26272D",
        },
        accent: {
          DEFAULT: "#F5A524",
          foreground: "#0F1013",
        },
        accent2: {
          DEFAULT: "#60A5FA",
        },
        success: "#22C55E",
        warning: "#EAB308",
        danger: "#EF4444",
      },
      fontFamily: {
        sans: [
          "IBM Plex Sans",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        display: ["40px", { lineHeight: "44px", fontWeight: "500" }],
      },
      maxWidth: {
        content: "1200px",
      },
    },
  },
  plugins: [],
};

export default config;
