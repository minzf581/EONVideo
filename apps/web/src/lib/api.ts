import type {
  PerformanceAnalysis,
  PerformanceSnapshot,
  Platform,
  Publication,
  PublicationChannel,
  Topic,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export const api = {
  topics: () => request<Topic[]>("/topics"),
  approveTopic: (id: string) => request<Topic>(`/topics/${id}/approve`, { method: "POST", body: "{}" }),
  rejectTopic: (id: string) => request<Topic>(`/topics/${id}/reject`, { method: "POST", body: "{}" }),
  requestRevision: (id: string) => request<Topic>(`/topics/${id}/request-revision`, { method: "POST", body: "{}" }),
  generateDraft: (id: string) => request<{ message: string }>(`/topics/${id}/video-draft`, { method: "POST" }),
  renderFinal: (id: string) => request<{ message: string }>(`/topics/${id}/render-final`, { method: "POST" }),
  channels: () => request<PublicationChannel[]>("/publication-channels"),
  publications: () => request<Publication[]>("/publications"),
  createPublication: (topicId: string, payload: { channel_id: string; platform: Platform; published_url: string; published_at: string; notes?: string }) =>
    request<Publication>(`/topics/${topicId}/publications`, { method: "POST", body: JSON.stringify(payload) }),
  createSnapshot: (publicationId: string, payload: Omit<PerformanceSnapshot, "id" | "publication_id" | "captured_at">) =>
    request<PerformanceSnapshot>(`/publications/${publicationId}/performance-snapshots`, { method: "POST", body: JSON.stringify(payload) }),
  analyze: (publicationId: string) =>
    request<PerformanceAnalysis>(`/publications/${publicationId}/analyze-performance`, { method: "POST" }),
  dashboard: () => request<{ publication_count: number; snapshot_count: number; analysis_count: number; top_topics: PerformanceAnalysis[] }>("/performance/dashboard"),
  learningSummary: () => request<{ active_rules: number; summary: string[] }>("/performance/learning-summary"),
};

