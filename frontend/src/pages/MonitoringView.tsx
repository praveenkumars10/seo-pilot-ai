import React, { useState, useEffect } from 'react';
import {
  Clock,
  Play,
  Pause,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  History,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { Website } from '../types';
import { api } from '../services/api';

export const MonitoringView: React.FC = () => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>('');
  const [comparison, setComparison] = useState<any | null>(null);
  const [intervalHours, setIntervalHours] = useState<number>(24);
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sites, scheds] = await Promise.all([
        api.getWebsites().catch(() => []),
        api.getSchedules().catch(() => []),
      ]);
      setWebsites(sites);
      setSchedules(scheds);
      if (sites.length > 0 && !selectedSiteId) {
        setSelectedSiteId(sites[0].id);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadComparison = async (siteId: string) => {
    if (!siteId) return;
    try {
      const comp = await api.getAuditComparison(siteId);
      setComparison(comp);
    } catch (e) {
      setComparison(null);
    }
  };

  useEffect(() => {
    if (selectedSiteId) {
      loadComparison(selectedSiteId);
    }
  }, [selectedSiteId]);

  const handleSetSchedule = async () => {
    if (!selectedSiteId) return;
    try {
      await api.scheduleWebsite(selectedSiteId, intervalHours);
      setActionMsg(`Scheduled recurring audit every ${intervalHours} hours!`);
      await loadData();
    } catch (e: any) {
      setActionMsg(`Error: ${e.message}`);
    }
  };

  const handlePause = async (siteId: string) => {
    await api.pauseSchedule(siteId);
    await loadData();
  };

  const handleResume = async (siteId: string) => {
    await api.resumeSchedule(siteId);
    await loadData();
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Continuous Monitoring & Scheduled Audits</h1>
        <p className="text-sm text-slate-400 mt-1">
          Automated background crawlers, trend detection, regression monitoring, and historical fix verification.
        </p>
      </div>

      {actionMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionMsg}</span>
        </div>
      )}

      {/* Top Controls: Schedule Recurring Audit */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Configure Automated Background Audit</h3>
            <p className="text-xs text-slate-400">
              The scheduler continuously runs in the background, crawls target URLs, scans source code, and prepares recommendations.
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center gap-4 pt-2">
          <select
            value={selectedSiteId}
            onChange={(e) => setSelectedSiteId(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white"
          >
            {websites.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} ({w.canonical_url})
              </option>
            ))}
          </select>

          <select
            value={intervalHours}
            onChange={(e) => setIntervalHours(Number(e.target.value))}
            className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white"
          >
            <option value={1}>Every 1 Hour (Intensive)</option>
            <option value={6}>Every 6 Hours</option>
            <option value={12}>Every 12 Hours</option>
            <option value={24}>Daily (Every 24 Hours - Recommended)</option>
            <option value={168}>Weekly (Every 7 Days)</option>
          </select>

          <button
            onClick={handleSetSchedule}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all shrink-0"
          >
            Save Recurring Schedule
          </button>
        </div>
      </div>

      {/* Historical Audit Comparison */}
      {comparison && comparison.has_history && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-5 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-400" />
              <h3 className="text-base font-bold text-white">Historical Comparison & Trend Detection</h3>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
              comparison.status_trend === 'improved'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : comparison.status_trend === 'regressed'
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                : 'bg-slate-800 text-slate-300'
            }`}>
              Trend: {comparison.status_trend}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-xs text-slate-400">Current Health Score</span>
              <div className="text-2xl font-bold text-white">{comparison.latest_score} / 100</div>
              <span className="text-[11px] text-slate-500">
                Delta from prior audit: {comparison.score_delta > 0 ? `+${comparison.score_delta}` : comparison.score_delta} pts
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-xs text-emerald-400 font-semibold">Resolved SEO Issues</span>
              <div className="text-2xl font-bold text-emerald-400">{comparison.resolved_issues.length}</div>
              <span className="text-[11px] text-slate-500">Verified fixed in latest crawl</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-xs text-amber-400 font-semibold">Newly Introduced Issues</span>
              <div className="text-2xl font-bold text-amber-400">{comparison.newly_introduced_issues.length}</div>
              <span className="text-[11px] text-slate-500">Regressions detected</span>
            </div>
          </div>
        </div>
      )}

      {/* Active Schedules Table */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <h3 className="text-base font-bold text-white">Active Background Schedules</h3>

        {schedules.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No recurring audit schedules active. Configure one above to enable 24/7 background monitoring.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60 font-mono text-xs">
            {schedules.map((s, idx) => (
              <div key={idx} className="py-3 flex items-center justify-between">
                <div>
                  <div className="text-slate-200 font-semibold">Website: {s.website_id}</div>
                  <div className="text-[11px] text-slate-400 font-sans">
                    Runs every {s.interval_hours}h • Next run: {s.next_run_at ? new Date(s.next_run_at).toLocaleString() : 'N/A'}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    s.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {s.is_active ? 'Active' : 'Paused'}
                  </span>

                  {s.is_active ? (
                    <button
                      onClick={() => handlePause(s.website_id)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1 font-sans font-medium"
                    >
                      <Pause className="w-3 h-3" />
                      <span>Pause</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => handleResume(s.website_id)}
                      className="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs flex items-center gap-1 font-sans font-medium"
                    >
                      <Play className="w-3 h-3" />
                      <span>Resume</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
