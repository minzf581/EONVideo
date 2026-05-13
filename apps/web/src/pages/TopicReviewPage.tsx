import { Check, Clapperboard, Download, RefreshCcw, Save, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";
import type { Topic } from "../lib/types";
import { MetricCard } from "../components/MetricCard";
import { StatusBadge } from "../components/StatusBadge";

type ScriptType = "30s" | "60s" | "douyin" | "wechat_channels" | "xiaohongshu";

export function TopicReviewPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selected, setSelected] = useState<Topic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scriptType, setScriptType] = useState<ScriptType>("60s");
  const [scriptDraft, setScriptDraft] = useState("");
  const [draftMessage, setDraftMessage] = useState<string | null>(null);

  function selectTopic(topic: Topic | null) {
    setSelected(topic);
    setScriptDraft(topic?.scripts.find((script) => script.script_type === scriptType)?.full_script ?? "");
    setDraftMessage(null);
  }

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.topics();
      setTopics(data);
      selectTopic(data[0] ?? null);
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
      selectTopic(data[0] ?? null);
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
    selectTopic(updated);
  }

  async function generateDraft() {
    if (!selected) return;
    if (selected.status !== "approved" && selected.status !== "video_draft_generated") {
      setError("请先通过选题，再生成视频草稿。");
      return;
    }
    await saveScript();
    const result = await api.generateDraft(selected.id, scriptType);
    const updated = result.topic;
    setTopics((items) => items.map((item) => (item.id === selected.id ? updated : item)));
    selectTopic(updated);
    setDraftMessage(result.message);
  }

  async function saveScript() {
    if (!selected) return;
    const updated = await api.updateScript(selected.id, {
      script_type: scriptType,
      full_script: scriptDraft,
    });
    setTopics((items) => items.map((item) => (item.id === updated.id ? updated : item)));
    setSelected(updated);
    setDraftMessage("脚本已保存。");
  }

  function changeScriptType(nextType: ScriptType) {
    setScriptType(nextType);
    setScriptDraft(selected?.scripts.find((script) => script.script_type === nextType)?.full_script ?? "");
  }

  return (
    <div>
      <header className="border-b border-gray-200 bg-white px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">中国老板热点短视频审核</h1>
            <p className="mt-1 text-sm text-gray-500">从国内平台热点中提炼资本逻辑，再人工确认生成最终视频。</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white" onClick={generateDailyTopics}>
            <RefreshCcw size={16} />
            生成今日 20 个选题
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
                onClick={() => selectTopic(topic)}
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
                  <span>老板相关 {topic.china_boss_relevance_score || topic.score}</span>
                  <span>风险分 {topic.risk_score}</span>
                  <span>情绪 {topic.topic_emotion}</span>
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
                <div>老板相关度</div>
                <div className="text-3xl font-semibold text-gray-950">{selected.china_boss_relevance_score || selected.score}</div>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-2 gap-4">
              <InfoBlock label="目标客户" value={selected.target_client} />
              <InfoBlock label="热点来源" value={selected.hot_source || selected.hot_summary} />
              <InfoBlock label="适合短视频" value={selected.why_short_video || "从老板痛点切入，转译为资本逻辑和业务决策。"} />
              <InfoBlock label="用户痛点" value={selected.user_pain_point} />
              <InfoBlock label="推荐脚本角度" value={selected.recommended_script_angle || selected.business_entry_point} />
              <InfoBlock label="业务切入点" value={selected.business_entry_point} />
              <InfoBlock label="封面标题" value={selected.cover_title} />
              <InfoBlock label="话题情绪" value={selected.topic_emotion} />
              <InfoBlock label="评分结构" value={`全球化 ${selected.enterprise_globalization_score} / 海外资本 ${selected.overseas_capital_score} / 视频号 ${selected.wechat_channels_potential_score} / 抖音 ${selected.douyin_potential_score}`} />
            </div>

            <div className="mt-5 rounded-md border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold">生成视频前编辑脚本</div>
                  <div className="mt-1 text-xs text-gray-500">保存脚本后再生成视频草稿，字幕和 Remotion JSON 会使用这里的内容。</div>
                </div>
                <div className="inline-flex rounded-md border border-gray-200 bg-gray-50 p-1">
                  {(["30s", "60s", "douyin", "wechat_channels", "xiaohongshu"] as const).map((type) => (
                    <button
                      className={`rounded px-3 py-1 text-xs font-medium ${scriptType === type ? "bg-white text-gray-950 shadow-sm" : "text-gray-500"}`}
                      key={type}
                      onClick={() => changeScriptType(type)}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>
              <textarea
                className="mt-4 min-h-44 w-full rounded-md border border-gray-300 p-3 text-sm leading-6 outline-none focus:border-gray-900"
                value={scriptDraft}
                onChange={(event) => setScriptDraft(event.target.value)}
              />
              <div className="mt-3 flex items-center justify-between">
                <div className="text-xs text-gray-500">约 {scriptDraft.length} 字</div>
                <button className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm" onClick={saveScript}>
                  <Save size={16} />
                  保存脚本
                </button>
              </div>
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
              <button
                className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50"
                disabled={selected.status !== "approved" && selected.status !== "video_draft_generated"}
                onClick={generateDraft}
              >
                <Clapperboard size={16} />
                生成视频草稿
              </button>
              <button className="inline-flex items-center gap-2 rounded-md border border-red-200 px-3 py-2 text-sm text-red-700" onClick={() => mutate(api.rejectTopic)}>
                <X size={16} />
                拒绝
              </button>
            </div>

            {draftMessage && (
              <div className="mt-5 rounded-md border border-teal-200 bg-teal-50 p-4 text-sm leading-6 text-teal-900">
                {draftMessage}
              </div>
            )}

            {selected.assets.length > 0 && (
              <div className="mt-5 rounded-md border border-gray-200 p-4">
                <div className="text-sm font-semibold">视频草稿资产</div>
                <div className="mt-3 grid grid-cols-2 gap-3">
                  {selected.assets.map((asset) => (
                    <a
                      className={`flex items-center justify-between rounded-md border px-3 py-2 text-sm ${
                        asset.render_status === "pending" ? "border-amber-200 bg-amber-50 text-amber-900" : "border-gray-200 text-gray-700 hover:border-gray-400"
                      }`}
                      download={asset.file_name}
                      href={asset.download_url}
                      key={`${asset.asset_type}-${asset.file_name}`}
                      onClick={(event) => {
                        if (asset.render_status === "pending") event.preventDefault();
                      }}
                    >
                      <span>{asset.file_name}</span>
                      <Download size={15} />
                    </a>
                  ))}
                </div>
                <div className="mt-3 text-xs leading-5 text-gray-500">
                  MP4 当前为待渲染状态；SRT、发布文案和 Remotion JSON 可先下载审核。接入 Remotion Worker 后会替换为真实 MP4。
                </div>
              </div>
            )}
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
