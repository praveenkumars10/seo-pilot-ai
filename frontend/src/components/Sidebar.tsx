import React from 'react';
import {
  LayoutDashboard,
  Globe,
  Search,
  CheckCircle2,
  Cpu,
  BarChart3,
  GitBranch
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  pendingCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, pendingCount }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'websites', label: 'Websites & Targets', icon: Globe },
    { id: 'audits', label: 'SEO Audit Engine', icon: Search },
    {
      id: 'approvals',
      label: 'Consolidated Approval',
      icon: CheckCircle2,
      badge: pendingCount > 0 ? pendingCount : undefined
    },
    { id: 'google', label: 'Google Search & Analytics', icon: BarChart3 },
    { id: 'ai', label: 'Multi-AI Providers', icon: Cpu },
    { id: 'monitoring', label: 'Continuous Monitoring', icon: LayoutDashboard },
    { id: 'git', label: 'Git & Version Control', icon: GitBranch },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
          Platform Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                  isActive ? 'bg-white text-indigo-700' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-semibold text-slate-300">Approval Policy</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          One consolidated confirmation before batch file edits. Tests run automatically before any Git commit.
        </p>
      </div>
    </aside>
  );
};

