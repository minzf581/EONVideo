import { ExternalLink, RefreshCcw, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { MetricCard } from "../components/MetricCard";
import { api } from "../lib/api";
import type { VideoJob } from "../lib/types";

export function VideoJobsPage() {
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setJobs(await api.allVideoJobs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法读取视频任务。");
    } finally {
      setLoading(false);
    }
  }

  async function retry(job: VideoJob) {
    const updated = await api.retryVideoJob(job.payload.topic_id, job.id);
    setJobs((items) => items.map((item) => (item.id === updated.id ? updated : item)));
  }

  useEffect(() => {
    void load();
  }, []);

  const stats = useMemo(
    () => ({
      total: jobs.length,
      pending: jobs.filter((job) => job.status === "pending").length,
      processing: jobs.filter((job) => job.status === "processing").length,
      completed: jobs.filter((job) => job.status === "completed").length,
    }),
    [jobs],
  );

  return (
    <div>
      <header className="border-b border-gray-200 bg-white px-6 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">视频任务</h1>
            <p className="mt-1 text-sm text-gray-500">查看所有 Remotion 云端渲染任务、状态、失败原因和输出 MP4。</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white" onClick={load}>
            <RefreshCcw size={16} />
            刷新任务
          </button>
        </div>
      </header>

      <section className="grid grid-cols-4 gap-4 px-6 py-5">
        <MetricCard label="全部任务" value={stats.total} />
        <MetricCard label="待渲染" value={stats.pending} tone="amber" />
        <MetricCard label="渲染中" value={stats.processing} tone="blue" />
        <MetricCard label="已完成" value={stats.completed} tone="green" />
      </section>

      {error && <div className="mx-6 mb-5 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>}

      <main className="px-6 pb-8">
        {loading ? (
          <div className="rounded-md border bg-white p-5 text-sm text-gray-500">加载中...</div>
        ) : jobs.length === 0 ? (
          <div className="rounded-md border bg-white p-5 text-sm text-gray-500">还没有视频任务。请先在“选题审核”里通过选题并生成视频草稿。</div>
        ) : (
          <div className="space-y-3">
            {jobs.map((job) => (
              <article className="rounded-md border border-gray-200 bg-white p-4" key={job.id}>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <JobStatusBadge status={job.status} />
                      <span className="text-xs text-gray-500">重试 {job.retry_count} 次</span>
                    </div>
                    <h2 className="mt-3 text-base font-semibold text-gray-950">{job.payload.title}</h2>
                    <p className="mt-1 text-sm leading-6 text-gray-600">{job.payload.subtitle}</p>
                  </div>
                  <div className="flex gap-2">
                    {job.status === "failed" && (
                      <button className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm" onClick={() => retry(job)}>
                        <RotateCcw size={15} />
                        重试
                      </button>
                    )}
                    {job.video_url && (
                      <a className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm" href={job.video_url} rel="noreferrer" target="_blank">
                        <ExternalLink size={15} />
                        MP4
                      </a>
                    )}
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-6 gap-3 text-xs text-gray-600">
                  <span>平台：{platformLabel(job.payload.targetPlatform)}</span>
                  <span>模板：{job.payload.template}</span>
                  <span>脚本：{job.payload.scriptType}</span>
                  <span>时长：{job.payload.durationSeconds}s</span>
                  <span>FPS：{job.payload.fps}</span>
                  <span>更新：{formatDate(job.updated_at)}</span>
                </div>

                <div className="mt-3 grid grid-cols-4 gap-2">
                  {["pending", "processing", "completed", "failed"].map((status) => (
                    <div
                      className={`h-1.5 rounded-full ${status === job.status || (job.status === "completed" && status !== "failed") ? "bg-gray-900" : "bg-gray-200"}`}
                      key={status}
                    />
                  ))}
                </div>

                {job.error_message && <div className="mt-3 rounded-md bg-red-50 p-3 text-xs leading-5 text-red-800">{job.error_message}</div>}
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function JobStatusBadge({ status }: { status: VideoJob["status"] }) {
  const label = {
    pending: "待渲染",
    processing: "渲染中",
    completed: "已完成",
    failed: "失败",
  }[status];
  const tone = {
    pending: "bg-amber-50 text-amber-700 border-amber-200",
    processing: "bg-blue-50 text-blue-700 border-blue-200",
    completed: "bg-green-50 text-green-700 border-green-200",
    failed: "bg-red-50 text-red-700 border-red-200",
  }[status];
  return <span className={`rounded-md border px-2 py-1 text-xs font-medium ${tone}`}>{label}</span>;
}

function platformLabel(platform: string) {
  return {
    douyin: "抖音",
    wechat_channels: "微信视频号",
    xiaohongshu: "小红书",
  }[platform] ?? platform;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}
