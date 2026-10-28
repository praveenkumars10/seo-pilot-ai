import React, { useState, useEffect } from 'react';
import {
  Search,
  Play,
  AlertCircle,
  FileCode,
  Sparkles,
  Filter,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  Loader2
} from 'lucide-react';
import { Website, Audit, SEOIssue, ChangePlan } from '../types';
import { api } from '../services/api';

interface AuditsViewProps {
  initialWebsite?: Website | null;
  onPlanGenerated: (plan: ChangePlan) => void;
}

export const AuditsView: React.FC<AuditsViewProps> = ({ initialWebsite, onPlanGenerated }) => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>(initialWebsite?.id || '');
  const [audits, setAudits] = useState<Audit[]>([]);
  const [selectedAudit, setSelectedAudit] = useState<Audit | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCrawling, setIsCrawling] = useState(false);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    api.getWebsites().then((sites) => {
      setWebsites(sites);
      if (!selectedSiteId && sites.length > 0) {
        setSelectedSiteId(sites[0].id);
      }
    });
  }, []);

  const loadAudits = async (siteId: string) => {
    try {
      const data = await api.getAuditsForWebsite(siteId);
      setAudits(data);
      if (data.length > 0) {
        const fullAudit = await api.getAuditDetails(data[0].id);
        setSelectedAudit(fullAudit);
      } else {
        setSelectedAudit(null);
      }
    } catch (e: any) {
      setErrorMsg(e.message);
    }
  };

  useEffect(() => {
    if (selectedSiteId) {
      loadAudits(selectedSiteId);
    }
  }, [selectedSiteId]);

  const handleLaunchAudit = async () => {
    if (!selectedSiteId) return;
    setIsCrawling(true);
    setErrorMsg(null);
    try {
      await api.triggerAudit(selectedSiteId, 25, true);
      // Poll audit status for a few seconds
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        const updatedAudits = await api.getAuditsForWebsite(selectedSiteId);
        setAudits(updatedAudits);
        if (updatedAudits.length > 0 && updatedAudits[0].status === 'completed') {
          clearInterval(interval);
          setIsCrawling(false);
          const full = await api.getAuditDetails(updatedAudits[0].id);
          setSelectedAudit(full);
        } else if (attempts > 20) {
          clearInterval(interval);
          setIsCrawling(false);
        }
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message);
      setIsCrawling(false);
    }
  };

  const handlePrepareApprovalPlan = async () => {
    if (!selectedSiteId) return;
    setIsGeneratingPlan(true);
    setErrorMsg(null);
    try {
      const plan = await api.generateChangePlan(selectedSiteId, selectedAudit?.id);
      onPlanGenerated(plan);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to synthesize plan');
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  const filteredIssues = (selectedAudit?.issues || []).filter((iss) => {
    if (filterSeverity !== 'all' && iss.severity !== filterSeverity) return false;
    if (searchTerm && !iss.title.toLowerCase().includes(searchTerm.toLowerCase()) && !iss.url_or_file.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header & Site Picker */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Technical SEO Crawler & Code Analysis</h1>
          <p className="text-sm text-slate-400 mt-1">
            Deep crawl verification: headers, canonicals, robots meta, alt tags, schema JSON-LD, and AST code analysis.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedSiteId}
            onChange={(e) => setSelectedSiteId(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-semibold"
          >
            {websites.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} ({w.canonical_url})
              </option>
            ))}
          </select>

          <button
            onClick={handleLaunchAudit}
            disabled={isCrawling || !selectedSiteId}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
          >
            {isCrawling ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Crawling & Inspecting...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Full Audit</span>
              </>
            )}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {selectedAudit ? (
        <div className="space-y-6">
          {/* Health Score & Stats Header */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
            <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/60 to-slate-900 border border-indigo-500/30 space-y-2">
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">SEO Health Score</span>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-black text-white">{selectedAudit.health_score}</span>
                <span className="text-xs text-slate-400">/ 100</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${selectedAudit.health_score}%` }}
                />
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs font-semibold text-slate-400">Pages Crawled</span>
              <div className="text-2xl font-bold text-white">{selectedAudit.pages_crawled}</div>
              <span className="text-[11px] text-slate-500">Live HTTP responses checked</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs font-semibold text-rose-400">Critical Issues</span>
              <div className="text-2xl font-bold text-rose-400">{selectedAudit.critical_issues}</div>
              <span className="text-[11px] text-slate-500">Direct SERP blockers</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <span className="text-xs font-semibold text-amber-400">High / Medium</span>
              <div className="text-2xl font-bold text-amber-400">
                {selectedAudit.high_issues + selectedAudit.medium_issues}
              </div>
              <span className="text-[11px] text-slate-500">Affects CTR & indexability</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
              <span className="text-xs font-semibold text-slate-400">Action Plan</span>
              <button
                onClick={handlePrepareApprovalPlan}
                disabled={isGeneratingPlan || selectedAudit.total_issues === 0}
                className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
              >
                {isGeneratingPlan ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5" />
                )}
                <span>Generate Fix Batch</span>
              </button>
            </div>
          </div>

          {/* Issues Browser */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-5 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filter by issue title or file..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 w-64"
                />
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-slate-400" />
                <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800 text-xs">
                  {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
                    <button
                      key={sev}
                      onClick={() => setFilterSeverity(sev)}
                      className={`px-3 py-1 rounded-lg font-semibold uppercase text-[11px] transition-all ${
                        filterSeverity === sev
                          ? 'bg-indigo-600 text-white'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Issues List */}
            <div className="space-y-3">
              {filteredIssues.length === 0 ? (
                <div className="p-12 text-center text-xs text-slate-500">
                  No issues matching the selected filters.
                </div>
              ) : (
                filteredIssues.map((issue) => (
                  <div
                    key={issue.id}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                          issue.severity === 'critical'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : issue.severity === 'high'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        }`}>
                          {issue.severity}
                        </span>
                        <h4 className="text-sm font-bold text-white">{issue.title}</h4>
                      </div>
                      <span className="text-[11px] font-mono text-slate-500 truncate max-w-xs">
                        {issue.url_or_file}
                      </span>
                    </div>

                    {issue.evidence && (
                      <div className="text-xs text-slate-400 font-mono bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                        {issue.evidence}
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                      <div>
                        <span className="text-slate-500 font-semibold">Root Cause: </span>
                        <span className="text-slate-300">{issue.root_cause_hypothesis || 'Under analysis'}</span>
                      </div>
                      <div>
                        <span className="text-indigo-400 font-semibold">Recommended Fix: </span>
                        <span className="text-slate-300">{issue.recommended_fix}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
          <Search className="w-8 h-8 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Audits Run Yet for this Website</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click "Run Full Audit" above to launch the crawler and scan your local source repository.
          </p>
        </div>
      )}
    </div>
  );
};
