import React, { useState, useEffect } from 'react';
import { Globe, Plus, Trash2, Folder, ExternalLink, Play, AlertCircle } from 'lucide-react';
import { Website } from '../types';
import { api } from '../services/api';

interface WebsitesViewProps {
  onStartAudit: (website: Website) => void;
}

export const WebsitesView: React.FC<WebsitesViewProps> = ({ onStartAudit }) => {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState('');
  const [canonicalUrl, setCanonicalUrl] = useState('');
  const [localRepoPath, setLocalRepoPath] = useState('');
  const [gscSiteUrl, setGscSiteUrl] = useState('');
  const [ga4PropertyId, setGa4PropertyId] = useState('');

  const loadWebsites = async () => {
    try {
      const data = await api.getWebsites();
      setWebsites(data);
    } catch (e: any) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadWebsites();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.createWebsite({
        name,
        canonical_url: canonicalUrl,
        local_repo_path: localRepoPath || undefined,
        gsc_site_url: gscSiteUrl || undefined,
        ga4_property_id: ga4PropertyId || undefined,
      });
      setName('');
      setCanonicalUrl('');
      setLocalRepoPath('');
      setGscSiteUrl('');
      setGa4PropertyId('');
      setShowAddModal(false);
      await loadWebsites();
    } catch (err: any) {
      setError(err.message || 'Failed to register website');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to remove this website from monitoring?')) {
      await api.deleteWebsite(id);
      await loadWebsites();
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Registered Websites & Repositories</h1>
          <p className="text-sm text-slate-400 mt-1">
            Connect live production URLs with local source-code repositories for bidirectional SEO analysis.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Register Website</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Website Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {websites.map((site) => (
          <div
            key={site.id}
            className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/80 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all shadow-xl"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Globe className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{site.name}</h3>
                    <a
                      href={site.canonical_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-indigo-400 hover:underline flex items-center gap-1 font-mono"
                    >
                      <span>{site.canonical_url}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(site.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-xs space-y-1.5">
                <div className="flex items-center gap-2 text-slate-400">
                  <Folder className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  <span className="font-semibold text-slate-300">Local Repo:</span>
                  <span className="font-mono truncate text-slate-400">{site.local_repo_path || 'Not specified (live crawl only)'}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="w-3.5 text-center font-bold text-slate-500">G</span>
                  <span className="font-semibold text-slate-300">Search Console:</span>
                  <span className="font-mono text-slate-400">{site.gsc_site_url || 'Unlinked'}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="w-3.5 text-center font-bold text-slate-500">A</span>
                  <span className="font-semibold text-slate-300">Analytics GA4:</span>
                  <span className="font-mono text-slate-400">{site.ga4_property_id || 'Unlinked'}</span>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">
                Added {new Date(site.created_at).toLocaleDateString()}
              </span>
              <button
                onClick={() => onStartAudit(site)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-600/20 text-xs font-bold transition-all"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Launch Comprehensive Audit</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Website Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl">
            <h2 className="text-base font-bold text-white">Register Website for SEO Pilot AI</h2>
            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Friendly Website Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. My Next.js Web App"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Canonical Production URL *</label>
                <input
                  type="url"
                  required
                  value={canonicalUrl}
                  onChange={(e) => setCanonicalUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Local Source Code Repository Path</label>
                <input
                  type="text"
                  value={localRepoPath}
                  onChange={(e) => setLocalRepoPath(e.target.value)}
                  placeholder="C:\Users\prave\...\my-project or .\"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Required for automated source-code modifications and Git version control.
                </p>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Search Console Property (Optional)</label>
                <input
                  type="text"
                  value={gscSiteUrl}
                  onChange={(e) => setGscSiteUrl(e.target.value)}
                  placeholder="sc-domain:example.com or https://example.com/"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Google Analytics 4 Property ID (Optional)</label>
                <input
                  type="text"
                  value={ga4PropertyId}
                  onChange={(e) => setGa4PropertyId(e.target.value)}
                  placeholder="e.g. 123456789"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold disabled:opacity-50"
                >
                  {loading ? 'Registering...' : 'Save Website'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
