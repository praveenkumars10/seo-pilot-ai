import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  FileCode,
  AlertTriangle,
  RotateCcw,
  GitCommit,
  Clock,
  Terminal,
  ExternalLink
} from 'lucide-react';
import { ChangePlan } from '../types';
import { api } from '../services/api';

interface ApprovalsViewProps {
  onOpenApproval: (plan: ChangePlan) => void;
}

export const ApprovalsView: React.FC<ApprovalsViewProps> = ({ onOpenApproval }) => {
  const [pendingPlans, setPendingPlans] = useState<ChangePlan[]>([]);
  const [selectedPlanDetails, setSelectedPlanDetails] = useState<ChangePlan | null>(null);
  const [loading, setLoading] = useState(true);

  const loadPlans = async () => {
    setLoading(true);
    try {
      const data = await api.getPendingApprovals();
      setPendingPlans(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, []);

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Consolidated Approval Gatekeeper</h1>
        <p className="text-sm text-slate-400 mt-1">
          Review, approve, or reject atomic batches of code modifications. Zero unverified file edits.
        </p>
      </div>

      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Consolidated Workflow Policy</h3>
            <p className="text-xs text-slate-400">
              A single consolidated confirmation applies all prepared file changes, triggers builds/tests, and commits to Git.
            </p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
          Enforced Locally
        </span>
      </div>

      {pendingPlans.length === 0 ? (
        <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-white">No Batches Awaiting Approval</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            When you run an SEO audit and generate an action plan, the consolidated change plan will appear here for your explicit review and authorization.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Pending Approval ({pendingPlans.length})
          </div>

          <div className="grid grid-cols-1 gap-4">
            {pendingPlans.map((plan) => (
              <div
                key={plan.id}
                className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-slate-700 transition-all shadow-xl"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 border border-amber-500/30 text-amber-400">
                      Pending Consolidated Review
                    </span>
                    <h3 className="text-base font-bold text-white">{plan.title}</h3>
                  </div>
                  <p className="text-xs text-slate-400">{plan.description}</p>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1.5">
                      <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{plan.changes.length} file(s) affected</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{plan.tests_to_run.length} automated test(s)</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span>Created {new Date(plan.created_at).toLocaleTimeString()}</span>
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onOpenApproval(plan)}
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all shrink-0"
                >
                  Review Batch & Diff
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

