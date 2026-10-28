import React, { useState, useEffect } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  Key,
  ShieldAlert,
  Server,
  Zap,
  Loader2
} from 'lucide-react';
import { AIProvider } from '../types';
import { api } from '../services/api';

export const AISettingsView: React.FC = () => {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [testingName, setTestingName] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<{ [key: string]: any }>({});
  const [editKeys, setEditKeys] = useState<{ [key: string]: string }>({});

  const loadStatus = async () => {
    try {
      const data = await api.getAIProvidersStatus();
      setProviders(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleTest = async (name: string) => {
    setTestingName(name);
    try {
      const res = await api.testAIProvider(name);
      setTestResults((prev) => ({ ...prev, [name]: res }));
      await loadStatus();
    } catch (err: any) {
      setTestResults((prev) => ({
        ...prev,
        [name]: { status: 'error', message: err.message, latency_ms: 0 }
      }));
    } finally {
      setTestingName(null);
    }
  };

  const handleSaveKey = async (name: string) => {
    const key = editKeys[name];
    if (key === undefined) return;
    try {
      await api.configureAIProvider(name, { api_key: key });
      await handleTest(name);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Multi-Provider AI Architecture</h1>
        <p className="text-sm text-slate-400 mt-1">
          Unified AI orchestration layer supporting Google Gemini, Anthropic Claude, OpenAI, and Meta/local models with automatic fallback.
        </p>
      </div>

      {/* Free Tier Notice */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs">
          <ShieldAlert className="w-4 h-4" />
          <span>Safety & Free Quota Policy</span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Google Gemini offers generous free-tier API quotas. Claude and OpenAI require developer API access with separate quotas.
          Meta models can run 100% free locally via Ollama or vLLM without external API costs.
          If no external keys are present, SEO Pilot AI automatically defaults to its built-in Deterministic Rule Engine so your project is never blocked.
        </p>
      </div>

      {/* Providers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {providers.map((p) => {
          const result = testResults[p.provider_name];
          const isMeta = p.provider_name === 'meta';
          return (
            <div
              key={p.provider_name}
              className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-5 shadow-xl hover:border-slate-700 transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold uppercase text-xs">
                    {p.provider_name.slice(0, 3)}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white capitalize">{p.provider_name}</h3>
                    <span className="text-xs text-slate-400 font-mono">{p.model_name}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                    p.has_api_key || isMeta
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-slate-800 text-slate-500'
                  }`}>
                    {p.has_api_key || isMeta ? 'Key Configured' : 'Missing Key'}
                  </span>
                </div>
              </div>

              {/* Dynamic Key Input */}
              <div className="space-y-1.5 text-xs">
                <label className="text-slate-400 font-medium">
                  {isMeta ? 'Ollama / Local Endpoint URL' : `${p.provider_name.toUpperCase()} API Key`}
                </label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    placeholder={p.has_api_key ? '••••••••••••••••••••••••' : 'Paste API Key or Token...'}
                    value={editKeys[p.provider_name] ?? ''}
                    onChange={(e) => setEditKeys({ ...editKeys, [p.provider_name]: e.target.value })}
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white text-xs font-mono focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    onClick={() => handleSaveKey(p.provider_name)}
                    className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all"
                  >
                    Save
                  </button>
                </div>
              </div>

              {/* Test Connection Output */}
              {result && (
                <div className={`p-3 rounded-xl border text-xs font-mono ${
                  result.status === 'healthy'
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                    : 'bg-amber-500/10 border-amber-500/20 text-amber-300'
                }`}>
                  <div className="flex items-center justify-between font-bold">
                    <span>Status: {result.status.toUpperCase()}</span>
                    <span>{result.latency_ms} ms</span>
                  </div>
                  <div className="text-[11px] mt-1">{result.message}</div>
                </div>
              )}

              {/* Action Button */}
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[11px] text-slate-500">
                  Priority: {p.provider_name === 'gemini' ? '1 (Primary)' : 'Secondary / Fallback'}
                </span>
                <button
                  onClick={() => handleTest(p.provider_name)}
                  disabled={testingName === p.provider_name}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600/10 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-600/20 text-xs font-bold transition-all disabled:opacity-50"
                >
                  {testingName === p.provider_name ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Zap className="w-3.5 h-3.5" />
                  )}
                  <span>Test Connection</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

