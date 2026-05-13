import type {
  PerformanceAnalysis,
  PerformanceSnapshot,
  Platform,
  Publication,
  PublicationChannel,
  Topic,
  VideoJob,
  VideoJobPayload,
} from "./types";

type ScriptType = "30s" | "60s" | "douyin" | "wechat_channels" | "xiaohongshu";

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
  generateDailyTopics: () =>
    request<Topic[]>("/topics/generate-daily", {
      method: "POST",
      body: JSON.stringify({
        production_date: new Date().toISOString().slice(0, 10),
        count: 20,
        use_performance_learning: true,
      }),
    }),
  approveTopic: (id: string) => request<Topic>(`/topics/${id}/approve`, { method: "POST", body: "{}" }),
  rejectTopic: (id: string) => request<Topic>(`/topics/${id}/reject`, { method: "POST", body: "{}" }),
  requestRevision: (id: string) => request<Topic>(`/topics/${id}/request-revision`, { method: "POST", body: "{}" }),
  updateScript: (id: string, payload: { script_type: ScriptType; full_script: string }) =>
    request<Topic>(`/topics/${id}/scripts`, { method: "PATCH", body: JSON.stringify(payload) }),
  generateDraft: (id: string, scriptType: ScriptType = "60s") =>
    request<{ topic: Topic; assets: Topic["assets"]; message: string }>(`/topics/${id}/video-draft`, {
      method: "POST",
      body: JSON.stringify({ script_type: scriptType, template: "finance_advisory_dark" }),
    }),
  renderFinal: (id: string) => request<{ message: string }>(`/topics/${id}/render-final`, { method: "POST" }),
  allVideoJobs: () => request<VideoJob[]>("/video-jobs"),
  videoJobs: (topicId: string) => request<VideoJob[]>(`/topics/${topicId}/video-jobs`),
  createVideoJob: (topicId: string, payload: VideoJobPayload) =>
    request<VideoJob>(`/topics/${topicId}/video-jobs`, { method: "POST", body: JSON.stringify({ payload }) }),
  updateVideoJob: (topicId: string, jobId: string, payload: VideoJobPayload) =>
    request<VideoJob>(`/topics/${topicId}/video-jobs/${jobId}`, { method: "PATCH", body: JSON.stringify({ payload }) }),
  retryVideoJob: (topicId: string, jobId: string) =>
    request<VideoJob>(`/topics/${topicId}/video-jobs/${jobId}/retry`, { method: "POST" }),
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
