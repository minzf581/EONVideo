import type { TopicStatus } from "../lib/types";

const labelMap: Record<string, string> = {
  draft: "草稿",
  pending_review: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
  revision_requested: "需修改",
  video_draft_generated: "视频草稿",
  final_rendered: "已渲染",
  published: "已发布",
  metrics_pending: "待反馈",
  metrics_collected: "已录入",
  performance_analyzed: "已分析",
};

export function StatusBadge({ status }: { status: TopicStatus | string }) {
  return (
    <span className="inline-flex items-center rounded-md border border-gray-200 bg-white px-2 py-1 text-xs font-medium text-gray-700">
      {labelMap[status] ?? status}
    </span>
  );
}

