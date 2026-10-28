import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Search,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  MousePointerClick,
  Eye,
  Key,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';

export const GoogleIntegrationsView: React.FC = () => {
  const [status, setStatus] = useState<{ configured: boolean; has_token: boolean; client_id?: string }>({
    configured: false,
    has_token: false
  });
  const [sites, setSites] = useState<{ siteUrl: string; permissionLevel: string }[]>([]);
  const [selectedSite, setSelectedSite] = useState<string>('');
  const [analyticsData, setAnalyticsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [authUrl, setAuthUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const gStatus = await api.getGoogleStatus();
      setStatus(gStatus);

      if (gStatus.has_token) {
        const sitesRes = await api.getSearchConsoleSites();
        if (sitesRes.connected && sitesRes.sites.length > 0) {
          setSites(sitesRes.sites);
          setSelectedSite(sitesRes.sites[0].siteUrl);
          const perf = await api.getSearchAnalytics(sitesRes.sites[0].siteUrl, 28);
          if (perf.connected) {
            setAnalyticsData(perf.rows || []);
          }
        }
      } else {
        const authRes = await api.getGoogleAuthUrl();
        if (authRes.configured && authRes.auth_url) {
          setAuthUrl(authRes.auth_url);
        }
      }
    } catch (e: any) {
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSiteChange = async (siteUrl: string) => {
    setSelectedSite(siteUrl);
    setLoading(true);
    try {
      const perf = await api.getSearchAnalytics(siteUrl, 28);
      if (perf.connected) {
        setAnalyticsData(perf.rows || []);
      }
    } catch (e: any) {
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Google Search Console & Analytics Integration</h1>
        <p className="text-sm text-slate-400 mt-1">
          OAuth 2.0 connection to retrieve real search impressions, clicks, keyword rankings, and organic session data.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Connection Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
            status.has_token
              ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
              : 'bg-amber-500/10 border border-amber-500/30 text-amber-400'
          }`}>
            <BarChart3 className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">Google Services Status:</h3>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                status.has_token
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}>
                {status.has_token ? 'Authenticated (OAuth Active)' : 'Awaiting Google OAuth'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {status.has_token
                ? 'Search Console API and Google Analytics Data API are active and authorized.'
                : 'Connect your authorized Google account to inspect search queries and indexing.'}
            </p>
          </div>
        </div>

        <div>
          {status.has_token ? (
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh API Data</span>
            </button>
          ) : authUrl ? (
            <a
              href={authUrl}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
            >
              <span>Connect Google Account via OAuth</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : (
            <div className="text-xs text-slate-400 italic">
              Set GOOGLE_CLIENT_ID & SECRET in .env
            </div>
          )}
        </div>
      </div>

      {/* If Not Connected: Step-by-Step Setup Guide */}
      {!status.has_token && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">Google OAuth Setup Instructions</h3>
          </div>
          <ol className="text-xs text-slate-400 space-y-2 list-decimal list-inside leading-relaxed">
            <li>
              Visit the{' '}
              <a
                href="https://console.cloud.google.com/apis/credentials"
                target="_blank"
                rel="noreferrer"
                className="text-indigo-400 hover:underline"
              >
                Google Cloud Console Credentials Page
              </a>.
            </li>
            <li>Enable <strong>Google Search Console API</strong> and <strong>Google Analytics Data API</strong>.</li>
            <li>Create an <strong>OAuth 2.0 Client ID</strong> (Application type: Web application).</li>
            <li>
              Add Authorized Redirect URI:{' '}
              <code className="text-slate-200 font-mono bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                http://localhost:8000/api/google/oauth2callback
              </code>
            </li>
            <li>
              Copy your <code className="text-indigo-300">Client ID</code> and <code className="text-indigo-300">Client Secret</code> into your project's <code className="text-slate-200">.env</code> file.
            </li>
          </ol>
        </div>
      )}

      {/* If Connected: Search Console Queries & Analytics Table */}
      {status.has_token && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Search Analytics Performance (Last 28 Days)</h3>
            {sites.length > 0 && (
              <select
                value={selectedSite}
                onChange={(e) => handleSiteChange(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white"
              >
                {sites.map((s) => (
                  <option key={s.siteUrl} value={s.siteUrl}>
                    {s.siteUrl}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3.5">Search Query</th>
                  <th className="px-5 py-3.5">Target Page</th>
                  <th className="px-5 py-3.5 text-right">Clicks</th>
                  <th className="px-5 py-3.5 text-right">Impressions</th>
                  <th className="px-5 py-3.5 text-right">CTR</th>
                  <th className="px-5 py-3.5 text-right">Position</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {analyticsData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-5 py-8 text-center text-slate-500 font-sans">
                      No search traffic data recorded for this property in the requested range.
                    </td>
                  </tr>
                ) : (
                  analyticsData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-5 py-3 text-slate-200 font-sans font-medium">{row.query || '(direct)'}</td>
                      <td className="px-5 py-3 text-slate-400 text-[11px] truncate max-w-xs">{row.page}</td>
                      <td className="px-5 py-3 text-right text-emerald-400 font-bold">{row.clicks}</td>
                      <td className="px-5 py-3 text-right text-slate-300">{row.impressions}</td>
                      <td className="px-5 py-3 text-right text-cyan-400">{row.ctr}%</td>
                      <td className="px-5 py-3 text-right text-amber-400">#{row.position}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
