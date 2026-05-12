import { BarChart3, Plus, RadioTower } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { MetricCard } from "../components/MetricCard";
import { StatusBadge } from "../components/StatusBadge";
import { api } from "../lib/api";
import type { PerformanceAnalysis, Platform, Publication, PublicationChannel, Topic } from "../lib/types";

export function PublicationsPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [channels, setChannels] = useState<PublicationChannel[]>([]);
  const [publications, setPublications] = useState<Publication[]>([]);
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [selectedChannelId, setSelectedChannelId] = useState("");
  const [selectedPublicationId, setSelectedPublicationId] = useState("");
  const [analysis, setAnalysis] = useState<PerformanceAnalysis | null>(null);

  async function load() {
    const [topicData, channelData, publicationData] = await Promise.all([
      api.topics(),
      api.channels(),
      api.publications(),
    ]);
    setTopics(topicData);
    setChannels(channelData);
    setPublications(publicationData);
    setSelectedTopicId(topicData[0]?.id ?? "");
    setSelectedChannelId(channelData[0]?.id ?? "");
    setSelectedPublicationId(publicationData[0]?.id ?? "");
  }

  useEffect(() => {
    void load();
  }, []);

  const selectedChannel = useMemo(
    () => channels.find((channel) => channel.id === selectedChannelId),
    [channels, selectedChannelId],
  );

  async function createPublication() {
    if (!selectedTopicId || !selectedChannel) return;
    const created = await api.createPublication(selectedTopicId, {
      channel_id: selectedChannel.id,
      platform: selectedChannel.platform,
      published_url: `https://example.com/${selectedChannel.platform}/${Date.now()}`,
      published_at: new Date().toISOString(),
      notes: "人工发布后登记，等待 24 小时效果反馈。",
    });
    setPublications((items) => [created, ...items]);
    setSelectedPublicationId(created.id);
  }

  async function submitSnapshot() {
    if (!selectedPublicationId) return;
    await api.createSnapshot(selectedPublicationId, {
      hours_since_publish: 24,
      data_source: "manual",
      view_count: 12800,
      like_count: 430,
      comment_count: 58,
      share_count: 96,
      favorite_count: 210,
      completion_rate: 37.5,
      avg_watch_seconds: 18.2,
      profile_visit_count: 168,
      follower_gain: 42,
      dm_count: 13,
      lead_count: 4,
    });
    const result = await api.analyze(selectedPublicationId);
    setAnalysis(result);
    await load();
  }

  const pending = publications.filter((item) => item.status === "metrics_pending").length;

  return (
    <div>
      <header className="border-b border-gray-200 bg-white px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">发布效果反馈</h1>
            <p className="mt-1 text-sm text-gray-500">发布后 24 小时内回填微信视频号、抖音、小红书数据。</p>
          </div>
          <div className="flex gap-2">
            <select className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm" value={selectedTopicId} onChange={(event) => setSelectedTopicId(event.target.value)}>
              {topics.map((topic) => (
                <option key={topic.id} value={topic.id}>
                  {topic.topic_title}
                </option>
              ))}
            </select>
            <select className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm" value={selectedChannelId} onChange={(event) => setSelectedChannelId(event.target.value)}>
              {channels.map((channel) => (
                <option key={channel.id} value={channel.id}>
                  {channel.name}
                </option>
              ))}
            </select>
            <button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm text-white" onClick={createPublication}>
              <Plus size={16} />
              登记发布
            </button>
          </div>
        </div>
      </header>

      <section className="grid grid-cols-4 gap-4 px-6 py-5">
        <MetricCard label="已登记发布" value={publications.length} />
        <MetricCard label="待录入 24 小时反馈" value={pending} tone="amber" />
        <MetricCard label="支持平台" value="3" tone="blue" />
        <MetricCard label="已生成分析" value={analysis ? 1 : 0} tone="green" />
      </section>

      <main className="grid grid-cols-[1fr_380px] gap-4 px-6 pb-8">
        <section className="rounded-md border border-gray-200 bg-white">
          <div className="border-b border-gray-200 px-4 py-3 text-sm font-semibold">发布记录</div>
          <div className="divide-y divide-gray-100">
            {publications.length === 0 ? (
              <div className="p-6 text-sm text-gray-500">还没有发布记录。先选择一个选题和平台进行登记。</div>
            ) : (
              publications.map((publication) => (
                <button
                  className={`grid w-full grid-cols-[150px_1fr_120px_100px] items-center gap-4 px-4 py-4 text-left text-sm hover:bg-gray-50 ${
                    selectedPublicationId === publication.id ? "bg-gray-50" : ""
                  }`}
                  key={publication.id}
                  onClick={() => setSelectedPublicationId(publication.id)}
                >
                  <div className="inline-flex items-center gap-2 font-medium">
                    <RadioTower size={16} />
                    {publication.platform_name}
                  </div>
                  <div>
                    <div className="font-medium text-gray-950">{publication.topic_title}</div>
                    <div className="mt-1 text-xs text-gray-500">{publication.published_url}</div>
                  </div>
                  <StatusBadge status={publication.status} />
                  <div className="text-xs text-gray-500">{new Date(publication.published_at).toLocaleString()}</div>
                </button>
              ))
            )}
          </div>
        </section>

        <aside className="space-y-4">
          <div className="rounded-md border border-gray-200 bg-white p-4">
            <div className="text-sm font-semibold">24 小时效果录入</div>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              MVP 先用固定样例数据模拟后台回填。后续可接微信视频号、抖音、小红书平台 API 或保留人工录入。
            </p>
            <button className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm text-white" onClick={submitSnapshot} disabled={!selectedPublicationId}>
              <BarChart3 size={16} />
              录入样例数据并分析
            </button>
          </div>

          {analysis && (
            <div className="rounded-md border border-gray-200 bg-white p-4">
              <div className="text-sm font-semibold">系统分析</div>
              <div className="mt-3 text-3xl font-semibold">{analysis.performance_score}</div>
              <div className="mt-1 text-xs text-gray-500">表现分 · {analysis.performance_label}</div>
              <div className="mt-4 space-y-3 text-sm leading-6 text-gray-700">
                <p>{analysis.recommendation}</p>
                <p className="rounded-md bg-teal-50 p-3 text-teal-900">{analysis.prompt_learning_summary}</p>
              </div>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}

