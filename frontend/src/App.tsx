import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ConsolidatedApprovalModal } from './components/ConsolidatedApprovalModal';
import { Dashboard } from './pages/Dashboard';
import { WebsitesView } from './pages/WebsitesView';
import { AuditsView } from './pages/AuditsView';
import { ApprovalsView } from './pages/ApprovalsView';
import { GoogleIntegrationsView } from './pages/GoogleIntegrationsView';
import { AISettingsView } from './pages/AISettingsView';
import { GitHistoryView } from './pages/GitHistoryView';
import { MonitoringView } from './pages/MonitoringView';
import { ChangePlan, Website } from './types';
import { api } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [pendingPlans, setPendingPlans] = useState<ChangePlan[]>([]);
  const [activeApprovalPlan, setActiveApprovalPlan] = useState<ChangePlan | null>(null);
  const [selectedAuditSite, setSelectedAuditSite] = useState<Website | null>(null);

  const refreshPendingApprovals = async () => {
    try {
      const data = await api.getPendingApprovals();
      setPendingPlans(data);
    } catch (e) {
      // Ignore initial connection errors
    }
  };

  useEffect(() => {
    refreshPendingApprovals();
    const timer = setInterval(refreshPendingApprovals, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleStartAuditFromWebsites = (site: Website) => {
    setSelectedAuditSite(site);
    setCurrentTab('audits');
  };

  const handlePlanGenerated = (plan: ChangePlan) => {
    refreshPendingApprovals();
    setActiveApprovalPlan(plan);
  };

  const handlePlanExecuted = (updatedPlan: ChangePlan) => {
    setActiveApprovalPlan(null);
    refreshPendingApprovals();
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
      <Header
        pendingApprovalsCount={pendingPlans.length}
        onOpenApprovals={() => {
          if (pendingPlans.length > 0) {
            setActiveApprovalPlan(pendingPlans[0]);
          } else {
            setCurrentTab('approvals');
          }
        }}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          pendingCount={pendingPlans.length}
        />

        <main className="flex-1 overflow-y-auto">
          {currentTab === 'dashboard' && (
            <Dashboard
              onNavigate={setCurrentTab}
              onOpenApproval={(p) => setActiveApprovalPlan(p)}
            />
          )}

          {currentTab === 'websites' && (
            <WebsitesView onStartAudit={handleStartAuditFromWebsites} />
          )}

          {currentTab === 'audits' && (
            <AuditsView
              initialWebsite={selectedAuditSite}
              onPlanGenerated={handlePlanGenerated}
            />
          )}

          {currentTab === 'approvals' && (
            <ApprovalsView
              onOpenApproval={(p) => setActiveApprovalPlan(p)}
            />
          )}

          {currentTab === 'google' && <GoogleIntegrationsView />}

          {currentTab === 'ai' && <AISettingsView />}

          {currentTab === 'monitoring' && <MonitoringView />}

          {currentTab === 'git' && <GitHistoryView />}
        </main>
      </div>

      {/* Consolidated Approval Modal */}
      {activeApprovalPlan && (
        <ConsolidatedApprovalModal
          plan={activeApprovalPlan}
          onClose={() => setActiveApprovalPlan(null)}
          onExecuted={handlePlanExecuted}
        />
      )}
    </div>
  );
}

export default App;
