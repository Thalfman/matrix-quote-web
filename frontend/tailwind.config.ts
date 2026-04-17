import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // ===== Design tokens (canonical) =====
        ink:       { DEFAULT: "#0D1B2A", dark: "#EDEBE4" },
        ink2:      "#1E2B3A",
        paper:     "#F6F4EF",
        surface:   { DEFAULT: "#FFFFFF", dark: "#15212F" },
        line:      "#E5E1D8",
        line2:     "#D8D3C6",
        muted:     { DEFAULT: "#5A6573", dark: "#92A0B3" },
        muted2:    "#8A94A1",
        amber:     "#F2B61F",
        amberSoft: "#FAEBB5",
        teal:      "#1F8FA6",
        tealDark:  "#177082",
        tealSoft:  "#D7ECF1",
        success:   "#2F8F6F",
        warning:   "#F2B61F",
        danger:    "#B5412B",

        // ===== Aliases (for incremental migration — removed in Plan 7) =====
        // bg = paper. Kept because index.html references `bg-bg-dark` in some pages.
        bg:        { DEFAULT: "#F6F4EF", dark: "#0A1420" },
        border:    { DEFAULT: "#E5E1D8", dark: "#25334A" },
        // brand = teal. Existing code uses bg-brand / text-brand — aliased to the new teal.
        brand: {
          DEFAULT: "#1F8FA6",
          hover:   "#177082",
          pressed: "#125562",
          subtle:  "#D7ECF1",
          foreground: "#FFFFFF",
        },
        // accent = teal, matches brand semantics for focus rings.
        accent: {
          DEFAULT: "#1F8FA6",
          foreground: "#FFFFFF",
        },
        // navy = ink. Preserves navy-900/800 numeric usages.
        navy: {
          DEFAULT: "#0D1B2A",
          600: "#1E2B3A",
          700: "#15212F",
          800: "#0D1B2A",
          900: "#0A1420",
        },
        // steel = line + muted family. Approximations — good enough for migration.
        steel: {
          100: "#F6F4EF",
          200: "#E5E1D8",
          300: "#D8D3C6",
          400: "#8A94A1",
          500: "#5A6573",
          600: "#25334A",
          700: "#15212F",
        },
      },
      fontFamily: {
        sans:    ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        display: ['"Barlow Condensed"', "Inter", "sans-serif"],
        mono:    ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        display: ["56px", { lineHeight: "60px", fontWeight: "600", letterSpacing: "-0.02em" }],
      },
      maxWidth: {
        content: "1400px",
      },
      borderRadius: {
        card: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
