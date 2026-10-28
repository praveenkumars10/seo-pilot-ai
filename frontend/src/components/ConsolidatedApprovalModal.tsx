import React, { useState } from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  FileCode,
  Check,
  Terminal,
  RotateCcw,
  GitCommit,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { ChangePlan } from '../types';
import { api } from '../services/api';

interface ConsolidatedApprovalModalProps {
  plan: ChangePlan;
  onClose: () => void;
  onExecuted: (updatedPlan: ChangePlan) => void;
}

export const ConsolidatedApprovalModal: React.FC<ConsolidatedApprovalModalProps> = ({
  plan,
  onClose,
  onExecuted,
}) => {
  const [selectedFileIdx, setSelectedFileIdx] = useState(0);
  const [autoGitPush, setAutoGitPush] = useState(false);
  const [customCommitMessage, setCustomCommitMessage] = useState(
    plan.git_commit_message || `fix(seo): resolve ${plan.changes.length} SEO issue(s)`
  );
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const selectedFile = plan.changes[selectedFileIdx] || plan.changes[0];

  const handleDecision = async (decision: 'approve' | 'reject') => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const updated = await api.submitApprovalDecision(
        plan.id,
        decision,
        autoGitPush,
        customCommitMessage
      );
      onExecuted(updated);
    } catch (err: any) {
      setErrorMsg(err.message || 'Execution error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-5xl h-[88vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Consolidated Approval Gatekeeper</h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 border border-amber-500/30 text-amber-400">
                  Batch Review
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Single consolidated confirmation to apply {plan.changes.length} file change(s) with automated testing.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMsg && (
          <div className="px-6 py-3 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Content Body: Two Columns */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Files & Review Summary */}
          <div className="w-80 border-r border-slate-800 flex flex-col bg-slate-950/20">
            <div className="p-4 border-b border-slate-800 space-y-3">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Batch Files ({plan.changes.length})
              </div>
              <div className="space-y-1">
                {plan.changes.map((change, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedFileIdx(idx)}
                    className={`w-full text-left px-3 py-2.5 rounded-xl text-xs font-medium flex items-center justify-between transition-all ${
                      selectedFileIdx === idx
                        ? 'bg-indigo-600/20 border border-indigo-500/40 text-indigo-200'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileCode className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span className="truncate">{change.file_path}</span>
                    </div>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                      change.action === 'create'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-cyan-500/20 text-cyan-400'
                    }`}>
                      {change.action}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Risk & Verification Checklist */}
            <div className="p-4 space-y-3 flex-1 overflow-y-auto">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Safety & Verification
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Risk Assessment:</span>
                  <span className="font-semibold text-emerald-400 uppercase">{plan.risk_assessment || 'LOW'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Pre-apply Backup:</span>
                  <span className="font-semibold text-cyan-400">Automatic Snapshot</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Auto-Rollback:</span>
                  <span className="font-semibold text-indigo-400">On Test Failure</span>
                </div>
              </div>

              {plan.tests_to_run && plan.tests_to_run.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-[11px] font-semibold text-slate-400">Automated Tests to Run:</div>
                  {plan.tests_to_run.map((cmd, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-300 font-mono bg-slate-950 p-2 rounded-lg border border-slate-800">
                      <Terminal className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span className="truncate">{cmd}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: Diff & Impact View */}
          <div className="flex-1 flex flex-col overflow-hidden bg-slate-950/40">
            {selectedFile ? (
              <div className="flex-1 flex flex-col p-6 overflow-hidden space-y-4">
                <div className="flex items-center justify-between bg-slate-900 p-3.5 rounded-xl border border-slate-800">
                  <div className="flex items-center gap-2">
                    <FileCode className="w-4 h-4 text-indigo-400" />
                    <span className="text-sm font-semibold text-white">{selectedFile.file_path}</span>
                  </div>
                  <span className="text-xs text-slate-400 font-medium">
                    Reason: {selectedFile.reason}
                  </span>
                </div>

                <div className="flex-1 flex flex-col bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
                  <div className="px-4 py-2 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400 font-mono">
                    <span>Unified Diff Preview</span>
                    <span>Standard Git Diff</span>
                  </div>
                  <div className="flex-1 p-4 overflow-auto font-mono text-xs leading-relaxed">
                    <pre className="text-slate-300">
                      {selectedFile.diff.split('\n').map((line, idx) => {
                        let colorClass = 'text-slate-400';
                        if (line.startsWith('+') && !line.startsWith('+++')) {
                          colorClass = 'text-emerald-400 bg-emerald-950/30 font-semibold';
                        } else if (line.startsWith('-') && !line.startsWith('---')) {
                          colorClass = 'text-rose-400 bg-rose-950/30';
                        } else if (line.startsWith('@@')) {
                          colorClass = 'text-cyan-400 bg-cyan-950/20';
                        }
                        return (
                          <div key={idx} className={`${colorClass} px-2 py-0.5 rounded`}>
                            {line || ' '}
                          </div>
                        );
                      })}
                    </pre>
                  </div>
                </div>

                {/* Target Issues Resolved */}
                <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-xs space-y-1">
                  <div className="font-semibold text-slate-300">Target SEO Issues Addressed:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedFile.target_issues.map((iss, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[11px]">
                        {iss}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500">
                No file selected
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
              <input
                type="checkbox"
                checked={autoGitPush}
                onChange={(e) => setAutoGitPush(e.target.checked)}
                className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-900 w-4 h-4"
              />
              <span className="font-medium">Push committed changes to remote repository</span>
            </label>

            <div className="flex items-center gap-2 text-xs">
              <GitCommit className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                value={customCommitMessage}
                onChange={(e) => setCustomCommitMessage(e.target.value)}
                placeholder="Commit message..."
                className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 text-xs w-72 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleDecision('reject')}
              disabled={loading}
              className="px-4 py-2 rounded-xl border border-slate-700 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all disabled:opacity-50"
            >
              Reject Plan
            </button>
            <button
              onClick={() => handleDecision('approve')}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Applying & Testing...</span>
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>Consolidate & Apply Approved Batch</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
