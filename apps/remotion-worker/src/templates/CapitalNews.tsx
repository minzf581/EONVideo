import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";

export const capitalNewsSchema = z.object({
  title: z.string(),
  subtitle: z.string().optional(),
  script: z.string(),
  bullets: z.array(z.string()).optional(),
  brandName: z.string().optional(),
  cta: z.string().optional(),
});

export type CapitalNewsProps = z.infer<typeof capitalNewsSchema>;

function splitScript(script: string): string[] {
  return script
    .replace(/[！？!?]/g, "。")
    .split("。")
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 8);
}

export function CapitalNews({
  title,
  subtitle = "国际资本市场观察",
  script,
  bullets = [],
  brandName = "EONVideo Capital Brief",
  cta = "关注账号，获取更多海外融资与新加坡资本市场观察。",
}: CapitalNewsProps) {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const titleProgress = spring({ frame, fps, config: { damping: 18, stiffness: 90 } });
  const scriptParts = splitScript(script);
  const activeSubtitle = scriptParts[Math.min(Math.floor(frame / Math.max(90, durationInFrames / Math.max(scriptParts.length, 1))), Math.max(scriptParts.length - 1, 0))] ?? script;
  const lineWidth = interpolate(frame, [20, 80], [0, 680], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#09111F", color: "#F9FAFB", fontFamily: "Noto Sans CJK SC, Noto Sans SC, Arial, sans-serif" }}>
      <AbsoluteFill
        style={{
          background: "linear-gradient(160deg, rgba(15,118,110,0.38), rgba(29,78,216,0.18) 48%, rgba(9,17,31,0.96))",
        }}
      />
      <div style={{ position: "absolute", inset: 0, opacity: 0.12 }}>
        {Array.from({ length: 14 }).map((_, index) => (
          <div
            key={index}
            style={{
              position: "absolute",
              left: 80 + (index % 4) * 230,
              top: 220 + Math.floor(index / 4) * 280,
              width: 1,
              height: 180,
              background: "#E5E7EB",
            }}
          />
        ))}
      </div>

      <div style={{ position: "absolute", left: 72, right: 72, top: 92 }}>
        <div style={{ color: "#5EEAD4", fontSize: 34, fontWeight: 800 }}>{brandName}</div>
        <div style={{ marginTop: 18, height: 6, width: lineWidth, background: "#5EEAD4" }} />
      </div>

      <div style={{ position: "absolute", left: 72, right: 72, top: 250 }}>
        <h1
          style={{
            margin: 0,
            fontSize: 86,
            lineHeight: 1.08,
            fontWeight: 900,
            letterSpacing: 0,
            transform: `translateY(${(1 - titleProgress) * 40}px)`,
            opacity: titleProgress,
          }}
        >
          {title}
        </h1>
        <p style={{ marginTop: 44, fontSize: 40, lineHeight: 1.45, color: "#CBD5E1" }}>{subtitle}</p>
      </div>

      <div style={{ position: "absolute", left: 72, right: 72, top: 850, display: "grid", gap: 24 }}>
        {bullets.slice(0, 4).map((bullet, index) => {
          const opacity = interpolate(frame, [120 + index * 24, 160 + index * 24], [0, 1], { extrapolateRight: "clamp" });
          return (
            <div
              key={bullet}
              style={{
                opacity,
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: 8,
                padding: "24px 28px",
                background: "rgba(255,255,255,0.08)",
                color: "#F8FAFC",
                fontSize: 36,
                fontWeight: 760,
              }}
            >
              {bullet}
            </div>
          );
        })}
      </div>

      <div
        style={{
          position: "absolute",
          left: 72,
          right: 72,
          bottom: 220,
          minHeight: 156,
          borderLeft: "8px solid #5EEAD4",
          paddingLeft: 28,
          color: "#E5E7EB",
          fontSize: 35,
          lineHeight: 1.45,
          fontWeight: 650,
        }}
      >
        {activeSubtitle}
      </div>

      <div
        style={{
          position: "absolute",
          left: 72,
          right: 72,
          bottom: 82,
          color: "#A7F3D0",
          fontSize: 30,
          lineHeight: 1.4,
          fontWeight: 700,
        }}
      >
        {cta}
      </div>
    </AbsoluteFill>
  );
}

