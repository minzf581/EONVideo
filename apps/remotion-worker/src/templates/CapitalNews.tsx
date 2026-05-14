import React from "react";
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";

const brollSceneSchema = z.object({
  start: z.number(),
  end: z.number(),
  keyword: z.string(),
  query: z.string(),
  source: z.enum(["pexels", "pixabay", "mixkit", "generated"]),
  url: z.string().optional(),
  credit: z.string().optional(),
  effect: z.enum(["slow_zoom", "pan_left", "pan_right", "blur_overlay"]),
  palette: z.tuple([z.string(), z.string(), z.string()]),
});

const subtitleCueSchema = z.object({
  start: z.number(),
  end: z.number(),
  text: z.string(),
  lines: z.array(z.string()),
  tokens: z.array(z.object({ text: z.string(), highlight: z.boolean() })),
});

export const capitalNewsSchema = z.object({
  title: z.string(),
  subtitle: z.string().optional(),
  script: z.string(),
  bullets: z.array(z.string()).optional(),
  brandName: z.string().optional(),
  cta: z.string().optional(),
  voiceoverUrl: z.string().optional(),
  bgmUrl: z.string().optional(),
  brollScenes: z.array(brollSceneSchema).optional(),
  subtitleTimeline: z.array(subtitleCueSchema).optional(),
  keywords: z.array(z.string()).optional(),
  visualStyle: z.string().optional(),
});

export type CapitalNewsProps = z.infer<typeof capitalNewsSchema>;
type BrollScene = z.infer<typeof brollSceneSchema>;
type SubtitleCue = z.infer<typeof subtitleCueSchema>;

const defaultScenes: BrollScene[] = [
  {
    start: 0,
    end: 60,
    keyword: "企业融资",
    query: "business finance",
    source: "generated",
    effect: "slow_zoom",
    palette: ["#07111F", "#1D4ED8", "#5EEAD4"],
  },
];

function activeItem<T extends { start: number; end: number }>(items: T[], seconds: number): T | undefined {
  return items.find((item) => seconds >= item.start && seconds < item.end) ?? items[items.length - 1];
}

function sceneProgress(scene: BrollScene, frame: number, fps: number): number {
  const startFrame = scene.start * fps;
  const duration = Math.max(1, (scene.end - scene.start) * fps);
  return Math.min(1, Math.max(0, (frame - startFrame) / duration));
}

function cameraTransform(scene: BrollScene, progress: number): string {
  if (scene.effect === "pan_left") {
    return `scale(1.12) translateX(${interpolate(progress, [0, 1], [34, -34])}px)`;
  }
  if (scene.effect === "pan_right") {
    return `scale(1.12) translateX(${interpolate(progress, [0, 1], [-34, 34])}px)`;
  }
  if (scene.effect === "blur_overlay") {
    return `scale(${interpolate(progress, [0, 1], [1.08, 1.18])}) translateY(${interpolate(progress, [0, 1], [18, -18])}px)`;
  }
  return `scale(${interpolate(progress, [0, 1], [1.03, 1.18])})`;
}

function GeneratedBackground({ scene, progress }: { scene: BrollScene; progress: number }) {
  const [base, accent, glow] = scene.palette;
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(145deg, ${base}, ${accent} 58%, #020617)`,
        transform: cameraTransform(scene, progress),
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(0deg, rgba(255,255,255,0.06) 1px, transparent 1px)",
          backgroundSize: "92px 92px",
          opacity: 0.22,
        }}
      />
      {Array.from({ length: 10 }).map((_, index) => (
        <div
          key={index}
          style={{
            position: "absolute",
            left: `${(index * 97) % 960}px`,
            top: `${180 + ((index * 173) % 1240)}px`,
            width: 260 + (index % 3) * 90,
            height: 2,
            background: index % 2 === 0 ? glow : "rgba(255,255,255,0.72)",
            opacity: 0.18,
            transform: `rotate(-18deg) translateX(${progress * 80}px)`,
          }}
        />
      ))}
    </AbsoluteFill>
  );
}

function BrollLayer({ scenes }: { scenes: BrollScene[] }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill>
      {scenes.map((scene, index) => {
        const from = Math.round(scene.start * fps);
        const durationInFrames = Math.max(1, Math.round((scene.end - scene.start) * fps));
        const progress = sceneProgress(scene, frame, fps);
        return (
          <Sequence from={from} durationInFrames={durationInFrames} key={`${scene.keyword}-${index}`}>
            <AbsoluteFill style={{ overflow: "hidden", background: scene.palette[0] }}>
              {scene.url ? (
                <OffthreadVideo
                  muted
                  src={scene.url}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    filter: scene.effect === "blur_overlay" ? "blur(5px) saturate(1.16)" : "saturate(1.12) contrast(1.06)",
                    transform: cameraTransform(scene, progress),
                  }}
                />
              ) : (
                <GeneratedBackground scene={scene} progress={progress} />
              )}
            </AbsoluteFill>
          </Sequence>
        );
      })}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(2,6,23,0.38), rgba(2,6,23,0.12) 38%, rgba(2,6,23,0.72)), radial-gradient(circle at 72% 18%, rgba(94,234,212,0.26), transparent 32%)",
        }}
      />
    </AbsoluteFill>
  );
}

function LightLeak() {
  const frame = useCurrentFrame();
  const x = interpolate(frame % 210, [0, 210], [-360, 1280]);
  const opacity = interpolate(frame % 210, [0, 30, 130, 210], [0, 0.36, 0.18, 0]);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: -180,
        width: 220,
        height: 2280,
        opacity,
        background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.52), rgba(245,158,11,0.28), transparent)",
        filter: "blur(18px)",
        transform: "rotate(16deg)",
      }}
    />
  );
}

function SubtitleBlock({ cue }: { cue?: SubtitleCue }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!cue) {
    return null;
  }

  const localFrame = frame - cue.start * fps;
  const pop = spring({ frame: Math.max(0, localFrame), fps, config: { damping: 13, stiffness: 180 } });
  const beat = interpolate(localFrame % 18, [0, 5, 18], [1, 1.035, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        left: 58,
        right: 58,
        bottom: 254,
        textAlign: "center",
        transform: `scale(${pop * beat})`,
        opacity: interpolate(localFrame, [0, 8], [0, 1], { extrapolateRight: "clamp" }),
      }}
    >
      <div
        style={{
          display: "inline",
          padding: "10px 18px",
          color: "#FFFFFF",
          fontSize: 64,
          lineHeight: 1.18,
          fontWeight: 950,
          textShadow: "0 5px 0 rgba(0,0,0,0.48), 0 14px 34px rgba(0,0,0,0.55)",
          WebkitTextStroke: "2px rgba(15,23,42,0.82)",
        }}
      >
        {cue.tokens.map((token, index) => (
          <span
            key={`${token.text}-${index}`}
            style={{
              color: token.highlight ? "#FACC15" : "#FFFFFF",
              background: token.highlight ? "rgba(15,23,42,0.62)" : "transparent",
              borderRadius: token.highlight ? 8 : 0,
              padding: token.highlight ? "0 8px" : 0,
              margin: token.highlight ? "0 2px" : 0,
            }}
          >
            {token.text}
          </span>
        ))}
      </div>
    </div>
  );
}

function HeroTitle({ title, subtitle }: { title: string; subtitle: string }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 17, stiffness: 86 } });
  return (
    <div style={{ position: "absolute", left: 56, right: 56, top: 132, transform: `translateY(${(1 - enter) * 38}px)`, opacity: enter }}>
      <div
        style={{
          display: "inline-block",
          border: "1px solid rgba(255,255,255,0.28)",
          borderRadius: 8,
          padding: "11px 16px",
          background: "rgba(15,23,42,0.42)",
          backdropFilter: "blur(18px)",
          color: "#A7F3D0",
          fontSize: 28,
          fontWeight: 850,
        }}
      >
        财经IP深度观察
      </div>
      <h1 style={{ margin: "30px 0 0", color: "#FFFFFF", fontSize: 74, lineHeight: 1.06, fontWeight: 950, textShadow: "0 18px 44px rgba(0,0,0,0.46)" }}>
        {title}
      </h1>
      <p style={{ margin: "26px 0 0", color: "#DDE7F3", fontSize: 35, lineHeight: 1.36, fontWeight: 720 }}>{subtitle}</p>
    </div>
  );
}

function BottomPanel({ brandName, bullets, cta, scene }: { brandName: string; bullets: string[]; cta: string; scene?: BrollScene }) {
  const frame = useCurrentFrame();
  const sceneLabel = scene?.keyword ?? "资本市场";
  return (
    <div
      style={{
        position: "absolute",
        left: 50,
        right: 50,
        bottom: 56,
        border: "1px solid rgba(255,255,255,0.22)",
        borderRadius: 8,
        padding: "22px 24px",
        background: "rgba(8,13,25,0.58)",
        backdropFilter: "blur(22px)",
        boxShadow: "0 24px 70px rgba(0,0,0,0.34)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 20 }}>
        <div style={{ color: "#F8FAFC", fontSize: 31, fontWeight: 900 }}>{brandName}</div>
        <div style={{ color: "#FACC15", fontSize: 27, fontWeight: 900 }}>#{sceneLabel}</div>
      </div>
      <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
        {bullets.slice(0, 3).map((bullet, index) => (
          <div
            key={bullet}
            style={{
              flex: 1,
              minHeight: 72,
              borderRadius: 8,
              padding: "14px 12px",
              background: index === frame % 3 ? "rgba(250,204,21,0.22)" : "rgba(255,255,255,0.10)",
              color: "#F8FAFC",
              fontSize: 24,
              lineHeight: 1.18,
              fontWeight: 800,
              textAlign: "center",
            }}
          >
            {bullet}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 18, color: "#BFDBFE", fontSize: 25, lineHeight: 1.3, fontWeight: 760 }}>{cta}</div>
    </div>
  );
}

export function CapitalNews({
  title,
  subtitle = "国际资本市场观察",
  bullets = [],
  brandName = "EONVideo Capital Brief",
  cta = "关注账号，获取更多海外融资与新加坡资本市场观察。",
  voiceoverUrl,
  bgmUrl,
  brollScenes = defaultScenes,
  subtitleTimeline = [],
}: CapitalNewsProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const seconds = frame / fps;
  const scene = activeItem(brollScenes, seconds);
  const cue = activeItem(subtitleTimeline, seconds);

  return (
    <AbsoluteFill style={{ background: "#020617", color: "#F9FAFB", fontFamily: "Noto Sans CJK SC, Noto Sans SC, Arial, sans-serif", overflow: "hidden" }}>
      <BrollLayer scenes={brollScenes.length ? brollScenes : defaultScenes} />
      <LightLeak />
      <AbsoluteFill style={{ boxShadow: "inset 0 0 160px rgba(0,0,0,0.56)" }} />
      <HeroTitle title={title} subtitle={subtitle} />
      <SubtitleBlock cue={cue} />
      <BottomPanel brandName={brandName} bullets={bullets} cta={cta} scene={scene} />
      {voiceoverUrl && <Audio src={voiceoverUrl} volume={1} />}
      {bgmUrl && <Audio loop src={bgmUrl} volume={0.14} />}
    </AbsoluteFill>
  );
}
