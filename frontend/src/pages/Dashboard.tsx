import React, { useState, useEffect } from 'react';
import {
  Globe,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  BarChart2,
  TrendingUp,
  ArrowUpRight,
  Play,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { Website, Audit, AIProvider, ChangePlan } from '../types';
import { api } from '../services/api';

interface DashboardProps {
  onNavigate: (tab: string) => void;
  onOpenApproval: (plan: ChangePlan) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate, onOpenApproval }) => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [aiProviders, setAIProviders] = useState<AIProvider[]>([]);
  const [pendingPlans, setPendingPlans] = useState<ChangePlan[]>([]);
  const [googleStatus, setGoogleStatus] = useState<{ configured: boolean; has_token: boolean }>({ configured: false, has_token: false });
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [webData, aiData, planData, gData] = await Promise.all([
        api.getWebsites().catch(() => []),
        api.getAIProvidersStatus().catch(() => []),
        api.getPendingApprovals().catch(() => []),
        api.getGoogleStatus().catch(() => ({ configured: false, has_token: false })),
      ]);
      setWebsites(webData);
      setAIProviders(aiData);
      setPendingPlans(planData);
      setGoogleStatus(gData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Autonomous SEO Control Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time technical crawler, code inspection, Google Search Console, and multi-model AI synthesis.
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Registered Sites</span>
            <Globe className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-black text-white">{websites.length}</div>
          <div className="text-xs text-slate-400 flex items-center gap-1">
            <span>Target Web Applications</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Approval Queue</span>
            <ShieldCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-amber-400">{pendingPlans.length}</div>
          <div className="text-xs text-slate-400 flex items-center gap-1">
            <span>Batches awaiting confirmation</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">AI Providers</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-black text-cyan-400">
            {aiProviders.filter(p => p.has_api_key || p.provider_name === 'meta').length} / {aiProviders.length || 4}
          </div>
          <div className="text-xs text-slate-400">Gemini, Claude, OpenAI, Meta</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Google OAuth Status</span>
            <BarChart2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${googleStatus.has_token ? 'bg-emerald-400' : 'bg-slate-600'}`} />
            <span className="text-lg font-bold text-white">
              {googleStatus.has_token ? 'Connected' : 'OAuth Ready'}
            </span>
          </div>
          <div className="text-xs text-slate-400">Search Console & GA4 Data</div>
        </div>
      </div>

      {/* Main Grid: Pending Approvals & Registered Sites */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 spans): Pending Approvals & Fast Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Pending Approval Callout */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/20 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Pending Consolidated Approvals</h3>
                  <p className="text-xs text-slate-400">Review proposed code patches, diffs, and verification commands before applying.</p>
                </div>
              </div>
              <button
                onClick={() => onNavigate('approvals')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <span>View All</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {pendingPlans.length === 0 ? (
              <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center text-xs text-slate-400 space-y-2">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto" />
                <p className="font-medium text-slate-300">All systems optimized and up-to-date.</p>
                <p>Run a fresh SEO audit from the Websites tab to detect opportunities and generate fixes.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingPlans.map((plan) => (
                  <div
                    key={plan.id}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition-all"
                  >
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-white">{plan.title}</div>
                      <div className="text-[11px] text-slate-400">
                        {plan.changes.length} file(s) modified • Risk: <span className="text-emerald-400 uppercase font-semibold">{plan.risk_assessment || 'LOW'}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => onOpenApproval(plan)}
                      className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/20"
                    >
                      Review & Approve
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Target Sites */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Target Websites</h3>
              <button
                onClick={() => onNavigate('websites')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
              >
                + Register Site
              </button>
            </div>

            {websites.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                No websites configured yet. Click "+ Register Site" to connect your first URL.
              </div>
            ) : (
              <div className="space-y-3">
                {websites.slice(0, 4).map((site) => (
                  <div
                    key={site.id}
                    className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between hover:border-slate-700 transition-all"
                  >
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-white">{site.name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{site.canonical_url}</div>
                      {site.local_repo_path && (
                        <div className="text-[10px] text-indigo-400 font-mono">Repo: {site.local_repo_path}</div>
                      )}
                    </div>
                    <button
                      onClick={() => onNavigate('audits')}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-all"
                    >
                      <Play className="w-3 h-3 text-emerald-400" />
                      <span>Audit Engine</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: AI Health & Architecture Highlights */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Multi-Model AI Health</h3>
              <button
                onClick={() => onNavigate('ai')}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
              >
                Manage
              </button>
            </div>

            <div className="space-y-2.5">
              {aiProviders.map((prov) => (
                <div
                  key={prov.provider_name}
                  className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs"
                >
                  <div className="space-y-0.5">
                    <div className="font-semibold text-slate-200 capitalize">{prov.provider_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{prov.model_name}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {prov.has_api_key || prov.provider_name === 'meta' ? (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        Configured
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-500">
                        Optional
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/30 to-slate-900 border border-indigo-500/20 space-y-3">
            <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Safety Architecture</h4>
            <ul className="text-xs text-slate-400 space-y-2 leading-relaxed">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Zero unsolicited code modifications.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Automated regression testing before git commit.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Instant rollback if tests fail.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Secrets (.env, tokens) permanently barred from commits.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

