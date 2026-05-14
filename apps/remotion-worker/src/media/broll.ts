import { financeKeywords, splitScriptIntoSentences } from "./subtitles.js";

export type BrollSource = "pexels" | "pixabay" | "mixkit" | "generated";

export interface BrollScene {
  start: number;
  end: number;
  keyword: string;
  query: string;
  source: BrollSource;
  url?: string;
  credit?: string;
  effect: "slow_zoom" | "pan_left" | "pan_right" | "blur_overlay";
  palette: [string, string, string];
}

interface VideoCandidate {
  url: string;
  source: BrollSource;
  credit?: string;
}

const keywordQueries: Record<string, string> = {
  新加坡: "Singapore skyline finance CBD",
  香港: "Hong Kong skyline stock exchange",
  IPO: "stock market trading board IPO finance",
  企业出海: "global business shipping port asia",
  AI: "artificial intelligence data center business",
  RWA: "digital asset blockchain finance city",
  家族办公室: "luxury office private wealth finance",
  企业融资: "business meeting investors finance",
  上市公司: "stock exchange listed company trading",
  工厂: "modern factory production line",
  港口: "container port shipping logistics",
  CBD: "business district skyscrapers city",
  股票市场: "stock market trading screen finance",
};

const keywordPalettes: Record<string, [string, string, string]> = {
  新加坡: ["#07111F", "#0F766E", "#F59E0B"],
  香港: ["#111827", "#B91C1C", "#F8FAFC"],
  IPO: ["#080F1E", "#2563EB", "#22C55E"],
  企业出海: ["#0B1220", "#0284C7", "#F97316"],
  AI: ["#050816", "#7C3AED", "#06B6D4"],
  RWA: ["#0C1222", "#0F766E", "#FACC15"],
  家族办公室: ["#111827", "#334155", "#D6B36A"],
  企业融资: ["#08111F", "#1D4ED8", "#A7F3D0"],
  上市公司: ["#0A0F1F", "#4F46E5", "#F8FAFC"],
  工厂: ["#111827", "#475569", "#F97316"],
  港口: ["#08111F", "#0369A1", "#F59E0B"],
  CBD: ["#080F1E", "#0EA5E9", "#E2E8F0"],
  股票市场: ["#06111F", "#16A34A", "#F8FAFC"],
};

const effects: BrollScene["effect"][] = ["slow_zoom", "pan_left", "pan_right", "blur_overlay"];

export function detectKeywords(text: string): string[] {
  const normalized = text.toLowerCase();
  const found = financeKeywords.filter((keyword) => normalized.includes(keyword.toLowerCase()));
  return found.length ? found : ["企业融资", "CBD", "股票市场"];
}

export async function buildBrollTimeline(script: string, durationSeconds: number): Promise<BrollScene[]> {
  const sentences = splitScriptIntoSentences(script, 10);
  const sceneCount = Math.max(4, Math.min(8, sentences.length || 6));
  const secondsPerScene = durationSeconds / sceneCount;
  const scriptKeywords = detectKeywords(script);

  const scenes: BrollScene[] = [];
  for (let index = 0; index < sceneCount; index += 1) {
    const sentence = sentences[index] ?? script;
    const keyword = detectKeywords(sentence)[0] ?? scriptKeywords[index % scriptKeywords.length] ?? "企业融资";
    const query = keywordQueries[keyword] ?? keyword;
    const candidate = await findVideoCandidate(query);
    scenes.push({
      start: index * secondsPerScene,
      end: index === sceneCount - 1 ? durationSeconds : (index + 1) * secondsPerScene,
      keyword,
      query,
      source: candidate?.source ?? "generated",
      url: candidate?.url,
      credit: candidate?.credit,
      effect: effects[index % effects.length],
      palette: keywordPalettes[keyword] ?? ["#08111F", "#1D4ED8", "#5EEAD4"],
    });
  }

  return scenes;
}

async function findVideoCandidate(query: string): Promise<VideoCandidate | null> {
  const explicit = findExplicitAsset(query);
  if (explicit) {
    return explicit;
  }

  const pexels = await searchPexels(query);
  if (pexels) {
    return pexels;
  }

  const pixabay = await searchPixabay(query);
  if (pixabay) {
    return pixabay;
  }

  return null;
}

function findExplicitAsset(query: string): VideoCandidate | null {
  const raw = process.env.BROLL_LIBRARY_JSON;
  if (!raw) {
    return null;
  }

  try {
    const library = JSON.parse(raw) as Record<string, string>;
    const url = library[query] ?? Object.entries(library).find(([key]) => query.toLowerCase().includes(key.toLowerCase()))?.[1];
    return url ? { url, source: "mixkit", credit: "Configured B-roll library" } : null;
  } catch (error) {
    console.warn("[broll] invalid BROLL_LIBRARY_JSON", error);
    return null;
  }
}

async function searchPexels(query: string): Promise<VideoCandidate | null> {
  const apiKey = process.env.PEXELS_API_KEY;
  if (!apiKey) {
    return null;
  }

  const url = new URL("https://api.pexels.com/videos/search");
  url.searchParams.set("query", query);
  url.searchParams.set("orientation", "portrait");
  url.searchParams.set("per_page", "1");

  try {
    const response = await fetch(url, { headers: { Authorization: apiKey } });
    if (!response.ok) {
      throw new Error(`Pexels ${response.status}`);
    }
    const data = (await response.json()) as {
      videos?: Array<{ user?: { name?: string }; video_files?: Array<{ width: number; height: number; link: string }> }>;
    };
    const video = data.videos?.[0];
    const file = video?.video_files
      ?.filter((item) => item.height >= item.width)
      .sort((left, right) => right.height - left.height)[0] ?? video?.video_files?.[0];
    return file ? { url: file.link, source: "pexels", credit: video?.user?.name } : null;
  } catch (error) {
    console.warn("[broll] Pexels search failed", error);
    return null;
  }
}

async function searchPixabay(query: string): Promise<VideoCandidate | null> {
  const apiKey = process.env.PIXABAY_API_KEY;
  if (!apiKey) {
    return null;
  }

  const url = new URL("https://pixabay.com/api/videos/");
  url.searchParams.set("key", apiKey);
  url.searchParams.set("q", query);
  url.searchParams.set("orientation", "vertical");
  url.searchParams.set("per_page", "3");

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Pixabay ${response.status}`);
    }
    const data = (await response.json()) as { hits?: Array<{ user?: string; videos?: { medium?: { url?: string }; large?: { url?: string } } }> };
    const hit = data.hits?.[0];
    const videoUrl = hit?.videos?.large?.url ?? hit?.videos?.medium?.url;
    return videoUrl ? { url: videoUrl, source: "pixabay", credit: hit?.user } : null;
  } catch (error) {
    console.warn("[broll] Pixabay search failed", error);
    return null;
  }
}
