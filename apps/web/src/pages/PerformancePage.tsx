import { useEffect, useState } from "react";

import { MetricCard } from "../components/MetricCard";
import { api } from "../lib/api";

export function PerformancePage() {
  const [dashboard, setDashboard] = useState<{ publication_count: number; snapshot_count: number; analysis_count: number } | null>(null);
  const [summary, setSummary] = useState<string[]>([]);

  useEffect(() => {
    void Promise.all([api.dashboard(), api.learningSummary()]).then(([dashboardData, summaryData]) => {
      setDashboard(dashboardData);
      setSummary(summaryData.summary);
    });
  }, []);

  return (
    <div>
      <header className="border-b border-gray-200 bg-white px-6 py-5">
        <h1 className="text-xl font-semibold">内容表现分析与选题学习</h1>
        <p className="mt-1 text-sm text-gray-500">把发布效果沉淀为次日 AI 选题的优化规则。</p>
      </header>

      <section className="grid grid-cols-4 gap-4 px-6 py-5">
        <MetricCard label="发布记录" value={dashboard?.publication_count ?? 0} />
        <MetricCard label="效果快照" value={dashboard?.snapshot_count ?? 0} tone="blue" />
        <MetricCard label="分析结论" value={dashboard?.analysis_count ?? 0} tone="green" />
        <MetricCard label="平台" value="视频号 / 抖音 / 小红书" tone="amber" />
      </section>

      <main className="grid grid-cols-[1fr_360px] gap-4 px-6 pb-8">
        <section className="rounded-md border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold">推荐优化方向</h2>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <RuleCard title="高观看低咨询" body="增强业务切入和 CTA，把咨询场景提前到脚本前半段。" />
            <RuleCard title="低观看高咨询" body="保留精准客户画像，优化封面标题和开头 3 秒。" />
            <RuleCard title="高转发" body="适合做系列化内容，例如上市路径比较、融资避坑清单。" />
            <RuleCard title="高收藏" body="适合做步骤、清单、检查表和决策框架。" />
          </div>
        </section>

        <aside className="rounded-md border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold">AI 学习摘要</h2>
          <div className="mt-4 space-y-3">
            {summary.map((item) => (
              <div className="rounded-md bg-gray-50 p-3 text-sm leading-6 text-gray-700" key={item}>
                {item}
              </div>
            ))}
          </div>
        </aside>
      </main>
    </div>
  );
}

function RuleCard({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-gray-200 p-4">
      <div className="text-sm font-semibold text-gray-950">{title}</div>
      <div className="mt-2 text-sm leading-6 text-gray-600">{body}</div>
    </div>
  );
}

