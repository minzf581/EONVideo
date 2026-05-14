import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

export interface VoiceoverAsset {
  url: string;
  provider: "openai" | "external";
  voice: string;
}

export async function prepareVoiceover(jobId: string, script: string, explicitUrl?: string): Promise<VoiceoverAsset | null> {
  if (explicitUrl) {
    return { url: explicitUrl, provider: "external", voice: "provided" };
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.warn("[tts] OPENAI_API_KEY is not set; rendering without AI voiceover");
    return null;
  }

  const model = process.env.TTS_MODEL ?? "gpt-4o-mini-tts";
  const voice = process.env.TTS_VOICE ?? "alloy";
  const outputPath = path.join("/tmp", "eonvideo-tts", `${jobId}.mp3`);

  await mkdir(path.dirname(outputPath), { recursive: true });

  const response = await fetch("https://api.openai.com/v1/audio/speech", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      voice,
      input: script,
      response_format: "mp3",
      instructions: "中文财经短视频口播，语速稳健、有企业家IP感，重点词略加强但不要夸张。",
    }),
  });

  if (!response.ok) {
    const message = await response.text().catch(() => response.statusText);
    throw new Error(`TTS generation failed: ${response.status} ${message}`);
  }

  const audio = Buffer.from(await response.arrayBuffer());
  await writeFile(outputPath, audio);
  return { url: `file://${outputPath}`, provider: "openai", voice };
}

export function resolveBgmUrl(explicitUrl?: string): string | undefined {
  return explicitUrl ?? process.env.BGM_URL ?? process.env.FINANCE_BGM_URL;
}
