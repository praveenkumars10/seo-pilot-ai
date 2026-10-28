import React from 'react';
import { ShieldCheck, Sparkles, Activity, AlertCircle } from 'lucide-react';

interface HeaderProps {
  pendingApprovalsCount: number;
  onOpenApprovals: () => void;
}

export const Header: React.FC<HeaderProps> = ({ pendingApprovalsCount, onOpenApprovals }) => {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            SEO Pilot AI
          </h1>
          <p className="text-xs text-slate-400 font-medium">Autonomous SEO Engineering & Optimization Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {pendingApprovalsCount > 0 ? (
          <button
            onClick={onOpenApprovals}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold hover:bg-amber-500/20 transition-all animate-pulse"
          >
            <AlertCircle className="w-4 h-4" />
            <span>{pendingApprovalsCount} Batch Awaiting Approval</span>
          </button>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="w-4 h-4" />
            <span>Gatekeeper Active (No Pending Approvals)</span>
          </div>
        )}

        <div className="h-4 w-px bg-slate-800" />

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
          <Activity className="w-3.5 h-3.5 text-indigo-400 animate-spin" style={{ animationDuration: '4s' }} />
          <span>Local Engine Active</span>
        </div>
      </div>
    </header>
  );
};
