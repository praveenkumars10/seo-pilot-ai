import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  GitCommit,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  Folder,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { Website, GitStatus } from '../types';
import { api } from '../services/api';

export const GitHistoryView: React.FC = () => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string>('');
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);
  const [commits, setCommits] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    api.getWebsites().then((sites) => {
      setWebsites(sites);
      if (sites.length > 0) {
        setSelectedSiteId(sites[0].id);
      }
    });
  }, []);

  const loadGitData = async (siteId: string) => {
    const site = websites.find((w) => w.id === siteId);
    if (!site || !site.local_repo_path) {
      setGitStatus(null);
      setCommits([]);
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const [status, hist] = await Promise.all([
        api.getGitStatus(site.local_repo_path),
        api.getGitCommits(site.local_repo_path, 15)
      ]);
      setGitStatus(status);
      setCommits(hist);
    } catch (e: any) {
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedSiteId && websites.length > 0) {
      loadGitData(selectedSiteId);
    }
  }, [selectedSiteId, websites]);

  const handlePush = async () => {
    const site = websites.find((w) => w.id === selectedSiteId);
    if (!site?.local_repo_path) return;

    setPushing(true);
    setErrorMsg(null);
    setActionMsg(null);
    try {
      const res = await api.pushGit(site.local_repo_path);
      setActionMsg(res.message || 'Successfully pushed to remote!');
      await loadGitData(selectedSiteId);
    } catch (e: any) {
      setErrorMsg(e.message || 'Failed to push');
    } finally {
      setPushing(false);
    }
  };

  const selectedSite = websites.find((w) => w.id === selectedSiteId);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Git & GitHub Version Control</h1>
          <p className="text-sm text-slate-400 mt-1">
            Auditable commit log, automated branch tracking, and credential-safe synchronization.
          </p>
        </div>

        {websites.length > 0 && (
          <select
            value={selectedSiteId}
            onChange={(e) => setSelectedSiteId(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white"
          >
            {websites.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {actionMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Repo Status Card */}
      {gitStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Current Branch</span>
            <div className="flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-indigo-400" />
              <span className="text-xl font-bold text-white font-mono">{gitStatus.branch || 'N/A'}</span>
            </div>
            <span className="text-[11px] text-slate-500">Repository detected and active</span>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Uncommitted Changes</span>
            <div className="text-xl font-bold text-white">
              {gitStatus.has_uncommitted_changes ? (
                <span className="text-amber-400">Working Tree Modified</span>
              ) : (
                <span className="text-emerald-400">Working Tree Clean</span>
              )}
            </div>
            <span className="text-[11px] text-slate-500">
              {gitStatus.modified_files.length} modified, {gitStatus.untracked_files.length} untracked
            </span>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Remote Synchronize</span>
            <button
              onClick={handlePush}
              disabled={pushing || !gitStatus.remotes.length}
              className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              {pushing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <UploadCloud className="w-4 h-4" />
              )}
              <span>Push to Remote</span>
            </button>
          </div>
        </div>
      )}

      {/* Commits Log */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <h3 className="text-base font-bold text-white">Audit Commit Log</h3>

        {commits.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No commits found in this repository.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60 font-mono text-xs">
            {commits.map((c) => (
              <div key={c.hash} className="py-3.5 flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-bold text-[11px]">
                      {c.hash}
                    </span>
                    <span className="text-white font-sans font-medium">{c.message}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 font-sans">
                    {c.author} • {new Date(c.timestamp).toLocaleString()}
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 shrink-0">
                  {c.files_changed.length} file(s) changed
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

