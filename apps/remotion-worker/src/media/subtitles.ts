export interface SubtitleToken {
  text: string;
  highlight: boolean;
}

export interface SubtitleCue {
  start: number;
  end: number;
  text: string;
  lines: string[];
  tokens: SubtitleToken[];
}

const punctuationPattern = /[。！？!?；;：:\n]+/g;

export const financeKeywords = [
  "新加坡",
  "香港",
  "IPO",
  "企业出海",
  "AI",
  "RWA",
  "家族办公室",
  "企业融资",
  "上市公司",
  "工厂",
  "港口",
  "CBD",
  "股票市场",
];

export function splitScriptIntoSentences(script: string, maxItems = 12): string[] {
  const normalized = script.replace(punctuationPattern, "。\n");
  const parts = normalized
    .split(/\n+/)
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => part.replace(/。$/, ""));

  return (parts.length ? parts : [script.trim()]).filter(Boolean).slice(0, maxItems);
}

export function wrapChineseLine(text: string, maxChars = 14): string[] {
  const clean = text.trim();
  if (clean.length <= maxChars) {
    return [clean];
  }

  const lines: string[] = [];
  let current = "";
  for (const char of clean) {
    current += char;
    if (current.length >= maxChars || /[，,、]/.test(char)) {
      lines.push(current.replace(/[，,、]$/, ""));
      current = "";
    }
  }
  if (current) {
    lines.push(current);
  }
  return lines.slice(0, 3);
}

export function tokenizeSubtitle(text: string, keywords = financeKeywords): SubtitleToken[] {
  const sortedKeywords = [...keywords].sort((left, right) => right.length - left.length);
  const tokens: SubtitleToken[] = [];
  let index = 0;

  while (index < text.length) {
    const matched = sortedKeywords.find((keyword) => text.slice(index).toLowerCase().startsWith(keyword.toLowerCase()));
    if (matched) {
      tokens.push({ text: text.slice(index, index + matched.length), highlight: true });
      index += matched.length;
      continue;
    }
    tokens.push({ text: text[index], highlight: false });
    index += 1;
  }

  return tokens;
}

export function buildSubtitleTimeline(script: string, durationSeconds: number, keywords = financeKeywords): SubtitleCue[] {
  const sentences = splitScriptIntoSentences(script);
  const secondsPerCue = Math.max(2.4, durationSeconds / Math.max(sentences.length, 1));

  return sentences.map((sentence, index) => {
    const start = index * secondsPerCue;
    const end = index === sentences.length - 1 ? durationSeconds : Math.min(durationSeconds, start + secondsPerCue);
    return {
      start,
      end,
      text: sentence,
      lines: wrapChineseLine(sentence),
      tokens: tokenizeSubtitle(sentence, keywords),
    };
  });
}
