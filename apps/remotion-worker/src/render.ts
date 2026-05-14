import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

import type { RenderPayload } from "./db.js";
import { buildBrollTimeline } from "./media/broll.js";
import { buildSubtitleTimeline, financeKeywords } from "./media/subtitles.js";
import { prepareVoiceover, resolveBgmUrl } from "./media/tts.js";

const dirname = path.dirname(fileURLToPath(import.meta.url));
const entryPoint = path.join(dirname, "Root.js");

let bundled: string | null = null;

export async function renderJobVideo(jobId: string, payload: RenderPayload): Promise<string> {
  const outputPath = `/tmp/${jobId}.mp4`;
  const fps = payload.fps ?? 30;
  const durationSeconds = payload.durationSeconds ?? 60;
  const voiceover = await prepareVoiceover(jobId, payload.script, payload.voiceoverUrl);
  const brollScenes = await buildBrollTimeline(payload.script, durationSeconds);
  const subtitleTimeline = buildSubtitleTimeline(payload.script, durationSeconds, financeKeywords);
  const inputProps = {
    title: payload.title,
    subtitle: payload.subtitle ?? "国际资本市场观察",
    script: payload.script,
    bullets: payload.bullets ?? [],
    brandName: payload.brandName ?? "EONVideo Capital Brief",
    cta: payload.cta ?? "关注账号，了解更多海外融资与新加坡资本市场观察。",
    voiceoverUrl: voiceover?.url,
    bgmUrl: resolveBgmUrl(payload.bgmUrl),
    brollScenes,
    subtitleTimeline,
    keywords: financeKeywords,
    visualStyle: payload.style ?? "douyin_finance_ip",
  };

  if (!bundled) {
    console.log("[render] bundling Remotion project");
    bundled = await bundle({
      entryPoint,
      webpackOverride: (config) => config,
    });
  }

  const composition = await selectComposition({
    serveUrl: bundled,
    id: "CapitalNews",
    inputProps,
  });

  console.log(`[render] rendering job=${jobId} to ${outputPath}`);
  await renderMedia({
    composition: {
      ...composition,
      durationInFrames: Math.max(1, Math.round(durationSeconds * fps)),
      fps,
      width: 1080,
      height: 1920,
    },
    serveUrl: bundled,
    codec: "h264",
    outputLocation: outputPath,
    inputProps,
  });

  return outputPath;
}
