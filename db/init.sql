create extension if not exists pgcrypto;

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email varchar(255) unique not null,
  name varchar(100),
  role varchar(50) not null default 'editor',
  password_hash text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists news_sources (
  id uuid primary key default gen_random_uuid(),
  name varchar(200) not null,
  source_type varchar(50) not null,
  url text,
  language varchar(20) default 'zh',
  region varchar(50),
  category varchar(100),
  is_active boolean not null default true,
  crawl_interval_minutes int not null default 60,
  crawl_config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists news_clusters (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  summary text,
  category varchar(100),
  tags text[] not null default '{}',
  entities jsonb not null default '{}'::jsonb,
  published_from timestamptz,
  published_to timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists content_topics (
  id uuid primary key default gen_random_uuid(),
  cluster_id uuid references news_clusters(id),
  production_date date not null,
  status varchar(50) not null default 'pending_review',
  topic_title text not null,
  hot_summary text not null,
  target_client text,
  user_pain_point text,
  business_entry_point text,
  cover_title text,
  risk_notice text,
  publish_copy text,
  tags text[] not null default '{}',
  priority int not null default 0,
  ai_model varchar(100),
  ai_raw_output jsonb not null default '{}'::jsonb,
  reviewed_at timestamptz,
  review_comment text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists topic_scripts (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references content_topics(id) on delete cascade,
  script_type varchar(50) not null,
  hook text,
  body text not null,
  call_to_action text,
  full_script text not null,
  estimated_duration_seconds int,
  version int not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (topic_id, script_type, version)
);

create table if not exists video_assets (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references content_topics(id) on delete cascade,
  asset_type varchar(50) not null,
  file_path text not null,
  public_url text,
  render_status varchar(50) not null default 'pending',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists publication_channels (
  id uuid primary key default gen_random_uuid(),
  name varchar(100) not null,
  platform varchar(100) not null,
  account_name varchar(200),
  account_url text,
  api_enabled boolean not null default false,
  api_config jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists video_publications (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references content_topics(id) on delete cascade,
  channel_id uuid references publication_channels(id),
  asset_id uuid references video_assets(id),
  platform varchar(100) not null,
  published_url text,
  published_at timestamptz not null,
  status varchar(50) not null default 'published',
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists video_performance_snapshots (
  id uuid primary key default gen_random_uuid(),
  publication_id uuid references video_publications(id) on delete cascade,
  captured_at timestamptz not null default now(),
  hours_since_publish int not null,
  data_source varchar(50) not null default 'manual',
  view_count int not null default 0,
  like_count int not null default 0,
  comment_count int not null default 0,
  share_count int not null default 0,
  favorite_count int not null default 0,
  completion_rate numeric(5,2),
  avg_watch_seconds numeric(8,2),
  profile_visit_count int not null default 0,
  follower_gain int not null default 0,
  dm_count int not null default 0,
  lead_count int not null default 0,
  raw_metrics jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists video_performance_analyses (
  id uuid primary key default gen_random_uuid(),
  publication_id uuid references video_publications(id) on delete cascade,
  topic_id uuid references content_topics(id) on delete cascade,
  snapshot_id uuid references video_performance_snapshots(id),
  performance_score numeric(6,2) not null default 0,
  engagement_rate numeric(8,6),
  lead_rate numeric(8,6),
  performance_label varchar(100),
  winning_factors text[] not null default '{}',
  weak_points text[] not null default '{}',
  recommendation text,
  prompt_learning_summary text,
  analysis_payload jsonb not null default '{}'::jsonb,
  model_name varchar(100),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into publication_channels (name, platform, account_name)
values
  ('微信视频号', 'wechat_channels', '默认账号'),
  ('抖音', 'douyin', '默认账号'),
  ('小红书', 'xiaohongshu', '默认账号')
on conflict do nothing;
