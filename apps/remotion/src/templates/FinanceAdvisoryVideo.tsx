import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";

export const financeVideoSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  bullets: z.array(z.string()),
  riskNotice: z.string(),
});

export type FinanceVideoProps = z.infer<typeof financeVideoSchema>;

export function FinanceAdvisoryVideo({ title, subtitle, bullets, riskNotice }: FinanceVideoProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleScale = spring({ frame, fps, config: { damping: 18 } });
  const lineProgress = interpolate(frame, [20, 80], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#0B1220", color: "white", fontFamily: "Inter, sans-serif" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(150deg, rgba(15,118,110,0.35), rgba(29,78,216,0.16) 42%, rgba(17,24,39,0.95))",
        }}
      />
      <div style={{ position: "absolute", top: 128, left: 80, right: 80 }}>
        <div style={{ color: "#5EEAD4", fontSize: 34, fontWeight: 700, letterSpacing: 0 }}>EONVideo Capital Brief</div>
        <h1
          style={{
            marginTop: 80,
            fontSize: 96,
            lineHeight: 1.05,
            fontWeight: 800,
            transform: `scale(${titleScale})`,
            transformOrigin: "left center",
          }}
        >
          {title}
        </h1>
        <div style={{ marginTop: 36, width: `${lineProgress * 640}px`, height: 8, background: "#5EEAD4" }} />
        <p style={{ marginTop: 52, fontSize: 44, lineHeight: 1.35, color: "#D1D5DB" }}>{subtitle}</p>
      </div>

      <div style={{ position: "absolute", left: 80, right: 80, top: 980, display: "grid", gap: 28 }}>
        {bullets.map((bullet, index) => {
          const opacity = interpolate(frame, [160 + index * 24, 200 + index * 24], [0, 1], { extrapolateRight: "clamp" });
          return (
            <div
              key={bullet}
              style={{
                opacity,
                border: "1px solid rgba(255,255,255,0.16)",
                borderRadius: 8,
                padding: "28px 32px",
                background: "rgba(255,255,255,0.08)",
                fontSize: 40,
                fontWeight: 700,
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
          left: 80,
          right: 80,
          bottom: 90,
          color: "#A7F3D0",
          fontSize: 28,
          lineHeight: 1.5,
        }}
      >
        {riskNotice}
      </div>
    </AbsoluteFill>
  );
}

