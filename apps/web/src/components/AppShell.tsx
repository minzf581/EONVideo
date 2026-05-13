import { BarChart3, ClipboardCheck, RadioTower } from "lucide-react";
import type { ReactNode } from "react";

const nav = [
  { href: "/review/topics", label: "选题审核", icon: ClipboardCheck },
  { href: "/publications", label: "发布反馈", icon: RadioTower },
  { href: "/performance", label: "效果学习", icon: BarChart3 },
];

export function AppShell({ children }: { children: ReactNode }) {
  const path = window.location.pathname;
  return (
    <div className="min-h-screen bg-finance-surface">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-5 py-5">
          <div className="text-lg font-semibold text-gray-950">EONVideo</div>
          <div className="mt-1 text-xs text-gray-500">中国老板全球化资本视频系统</div>
        </div>
        <nav className="space-y-1 p-3">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = path.startsWith(item.href.split("/").slice(0, 2).join("/"));
            return (
              <a
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm ${
                  active ? "bg-gray-900 text-white" : "text-gray-700 hover:bg-gray-100"
                }`}
                href={item.href}
                key={item.href}
              >
                <Icon size={17} />
                {item.label}
              </a>
            );
          })}
        </nav>
        <div className="absolute bottom-0 border-t border-gray-200 p-4 text-xs leading-5 text-gray-500">
          平台：视频号、抖音、小红书。核心：老板痛点、全球化、海外资本。
        </div>
      </aside>
      <main className="pl-64">{children}</main>
    </div>
  );
}
