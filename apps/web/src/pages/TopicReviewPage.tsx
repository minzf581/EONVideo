import { Check, Clapperboard, RefreshCcw, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";
import type { Topic } from "../lib/types";
import { MetricCard } from "../components/MetricCard";
import { StatusBadge } from "../components/StatusBadge";

export function TopicReviewPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<Topic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.topics();
      setTopics(data);
      setSelected(data[0] ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法连接后端 API，请检查 VITE_API_BASE 或 CORS 配置。");
    } finally {
      setLoading(false);
    }
  }

  async function generateDailyTopics() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.generateDailyTopics();
      setTopics(data);
      setSelected(data[0] ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成选题失败，请稍后重试。");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const stats = useMemo(
    () => ({
      total: topics.length,
      pending: topics.filter((topic) => topic.status === "pending_review").length,
      approved: topics.filter((topic) => topic.status === "approved").length,
      risk: topics.filter((topic) => topic.risk_score >= 35).length,
    }),
    [topics],
  );

  async function mutate(action: (id: string) => Promise<Topic>) {
    if (!selected) return;
    const updated = await action(selected.id);
    setTopics((items) => items.map((item) => (item.id === updated.id ? updated : item)));
    setSelected(updated);
  }

  async function generateDraft() {
    if (!selected) return;
    await api.generateDraft(selected.id);
    const updated = { ...selected, status: "video_draft_generated" as const };
    setTopics((items) => items.map((item) => (item.id === selected.id ? updated : item)));
    setSelected(updated);
  }

  return (
    <div>
      <header className="border-b border-gray-200 bg-white px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">每日 AI 热点短视频审核</h1>
            <p className="mt-1 text-sm text-gray-500">先审核选题，再人工确认生成最终视频。</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white" onClick={generateDailyTopics}>
            <RefreshCcw size={16} />
            生成今日 10 个选题
          </button>
        </div>
      </header>

      <section className="grid grid-cols-4 gap-4 px-6 py-5">
        <MetricCard label="今日选题" value={stats.total} />
        <MetricCard label="待审核" value={stats.pending} tone="blue" />
        <MetricCard label="已通过" value={stats.approved} tone="green" />
        <MetricCard label="高风险关注" value={stats.risk} tone="amber" />
      </section>

      {error && (
        <div className="mx-6 mb-5 rounded-md border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800">
          {error}
        </div>
      )}

      <main className="grid grid-cols-[minmax(420px,0.95fr)_1.05fr] gap-4 px-6 pb-8">
        <section className="space-y-3">
          {loading ? (
            <div className="rounded-md border bg-white p-5 text-sm text-gray-500">加载中...</div>
          ) : (
            topics.map((topic) => (
              <button
                className={`w-full rounded-md border bg-white p-4 text-left shadow-sm transition hover:border-gray-400 ${
                  selected?.id === topic.id ? "border-gray-900" : "border-gray-200"
                }`}
                key={topic.id}
                onClick={() => setSelected(topic)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-gray-950">{topic.topic_title}</div>
                    <div className="mt-2 line-clamp-2 text-sm leading-6 text-gray-600">{topic.hot_summary}</div>
                  </div>
                  <StatusBadge status={topic.status} />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {topic.tags.map((tag) => (
                    <span className="rounded-md bg-gray-100 px-2 py-1 text-xs text-gray-600" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="mt-3 flex gap-4 text-xs text-gray-500">
                  <span>综合分 {topic.score}</span>
                  <span>风险分 {topic.risk_score}</span>
                  <span>{topic.category}</span>
                </div>
              </button>
            ))
          )}
        </section>

        {selected && (
          <section className="rounded-md border border-gray-200 bg-white p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <StatusBadge status={selected.status} />
                <h2 className="mt-3 text-xl font-semibold">{selected.topic_title}</h2>
                <p className="mt-2 text-sm leading-6 text-gray-600">{selected.hot_summary}</p>
              </div>
              <div className="text-right text-sm text-gray-500">
                <div>综合分</div>
                <div className="text-3xl font-semibold text-gray-950">{selected.score}</div>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-2 gap-4">
              <InfoBlock label="目标客户" value={selected.target_client} />
              <InfoBlock label="用户痛点" value={selected.user_pain_point} />
              <InfoBlock label="业务切入点" value={selected.business_entry_point} />
              <InfoBlock label="封面标题" value={selected.cover_title} />
            </div>

            <div className="mt-5 space-y-4">
              {selected.scripts.map((script) => (
                <div className="rounded-md border border-gray-200 p-4" key={script.script_type}>
                  <div className="mb-2 text-sm font-semibold">{script.script_type} 口播脚本</div>
                  <p className="text-sm leading-6 text-gray-700">{script.full_script}</p>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
              {selected.risk_notice}
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              <button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-3 py-2 text-sm text-white" onClick={() => mutate(api.approveTopic)}>
                <Check size={16} />
                通过选题
              </button>
              <button className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm" onClick={() => mutate(api.requestRevision)}>
                <RefreshCcw size={16} />
                要求修改
              </button>
              <button className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm" onClick={generateDraft}>
                <Clapperboard size={16} />
                生成视频草稿
              </button>
              <button className="inline-flex items-center gap-2 rounded-md border border-red-200 px-3 py-2 text-sm text-red-700" onClick={() => mutate(api.rejectTopic)}>
                <X size={16} />
                拒绝
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-gray-200 p-4">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="mt-2 text-sm leading-6 text-gray-800">{value}</div>
    </div>
  );
}
