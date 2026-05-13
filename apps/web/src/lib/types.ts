export type TopicStatus =
  | "draft"
  | "pending_review"
  | "approved"
  | "rejected"
  | "revision_requested"
  | "video_draft_generated"
  | "final_rendered"
  | "published"
  | "metrics_pending"
  | "metrics_collected"
  | "performance_analyzed";

export type Platform = "wechat_channels" | "douyin" | "xiaohongshu";

export interface TopicScript {
  script_type: "30s" | "60s" | "douyin" | "wechat_channels" | "xiaohongshu";
  full_script: string;
  estimated_duration_seconds: number;
}

export interface VideoAsset {
  asset_type: "mp4" | "srt" | "cover" | "publish_copy" | "remotion_json";
  file_name: string;
  download_url: string;
  render_status: "pending" | "completed" | "failed";
}

export interface Topic {
  id: string;
  production_date: string;
  status: TopicStatus;
  category: string;
  score: number;
  risk_score: number;
  topic_emotion: string;
  china_boss_relevance_score: number;
  enterprise_globalization_score: number;
  overseas_capital_score: number;
  wechat_channels_potential_score: number;
  douyin_potential_score: number;
  comment_controversy_score: number;
  collection_value_score: number;
  international_news_score: number;
  topic_title: string;
  hot_source: string;
  why_short_video: string;
  recommended_script_angle: string;
  hot_summary: string;
  target_client: string;
  user_pain_point: string;
  business_entry_point: string;
  cover_title: string;
  risk_notice: string;
  publish_copy: string;
  tags: string[];
  scripts: TopicScript[];
  created_at: string;
  assets: VideoAsset[];
}

export type VideoJobStatus = "pending" | "processing" | "completed" | "failed";

export interface VideoJobPayload {
  topic_id: string;
  title: string;
  subtitle: string;
  script: string;
  bullets: string[];
  brandName: string;
  cta: string;
  durationSeconds: number;
  fps: number;
  template: string;
  style: string;
  targetPlatform: string;
  coverTitle: string;
  scriptType: string;
}

export interface VideoJob {
  id: string;
  status: VideoJobStatus;
  payload: VideoJobPayload;
  video_url?: string | null;
  error_message?: string | null;
  retry_count: number;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface PublicationChannel {
  id: string;
  name: string;
  platform: Platform;
  account_name: string;
  api_enabled: boolean;
}

export interface Publication {
  id: string;
  topic_id: string;
  channel_id: string;
  platform: Platform;
  platform_name: string;
  topic_title: string;
  published_url: string;
  published_at: string;
  status: string;
  notes?: string;
}

export interface PerformanceSnapshot {
  id: string;
  publication_id: string;
  captured_at: string;
  hours_since_publish: number;
  data_source: "manual" | "platform_api";
  view_count: number;
  like_count: number;
  comment_count: number;
  share_count: number;
  favorite_count: number;
  completion_rate?: number;
  avg_watch_seconds?: number;
  profile_visit_count: number;
  follower_gain: number;
  dm_count: number;
  lead_count: number;
}

export interface PerformanceAnalysis {
  id: string;
  publication_id: string;
  topic_id: string;
  snapshot_id: string;
  performance_score: number;
  engagement_rate: number;
  lead_rate: number;
  performance_label: string;
  winning_factors: string[];
  weak_points: string[];
  recommendation: string;
  prompt_learning_summary: string;
  created_at: string;
}
