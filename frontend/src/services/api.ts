import {
  Website,
  Audit,
  ChangePlan,
  AIProvider,
  SearchConsoleSite,
  SearchAnalyticsRow,
  GitStatus
} from '../types';

const API_BASE = '/api';

export const api = {
  // Websites
  getWebsites: async (): Promise<Website[]> => {
    const res = await fetch(`${API_BASE}/websites`);
    if (!res.ok) throw new Error('Failed to fetch websites');
    return res.json();
  },

  createWebsite: async (data: Partial<Website>): Promise<Website> => {
    const res = await fetch(`${API_BASE}/websites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create website');
    }
    return res.json();
  },

  deleteWebsite: async (id: string): Promise<void> => {
    const res = await fetch(`${API_BASE}/websites/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete website');
  },

  // Audits & Crawler
  triggerAudit: async (websiteId: string, maxPages: number = 20, includeCodeAnalysis: boolean = true): Promise<Audit> => {
    const res = await fetch(`${API_BASE}/audits/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        website_id: websiteId,
        max_pages: maxPages,
        include_code_analysis: includeCodeAnalysis
      }),
    });
    if (!res.ok) throw new Error('Failed to trigger audit');
    return res.json();
  },

  getAuditsForWebsite: async (websiteId: string): Promise<Audit[]> => {
    const res = await fetch(`${API_BASE}/audits/website/${websiteId}`);
    if (!res.ok) throw new Error('Failed to fetch audits');
    return res.json();
  },

  getAuditDetails: async (auditId: string): Promise<Audit> => {
    const res = await fetch(`${API_BASE}/audits/${auditId}`);
    if (!res.ok) throw new Error('Failed to fetch audit details');
    return res.json();
  },

  // Consolidated Approval Center
  generateChangePlan: async (websiteId: string, auditId?: string): Promise<ChangePlan> => {
    const res = await fetch(`${API_BASE}/approvals/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ website_id: websiteId, audit_id: auditId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate change plan');
    }
    return res.json();
  },

  getPendingApprovals: async (): Promise<ChangePlan[]> => {
    const res = await fetch(`${API_BASE}/approvals/pending`);
    if (!res.ok) throw new Error('Failed to fetch pending approvals');
    return res.json();
  },

  getPlanDetails: async (planId: string): Promise<ChangePlan> => {
    const res = await fetch(`${API_BASE}/approvals/${planId}`);
    if (!res.ok) throw new Error('Failed to fetch plan');
    return res.json();
  },

  submitApprovalDecision: async (
    planId: string,
    decision: 'approve' | 'reject',
    autoGitPush: boolean = false,
    customCommitMessage?: string
  ): Promise<ChangePlan> => {
    const res = await fetch(`${API_BASE}/approvals/${planId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        decision,
        auto_git_push: autoGitPush,
        custom_commit_message: customCommitMessage,
        run_tests: true
      }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Approval submission failed');
    }
    return res.json();
  },

  // AI Providers
  getAIProvidersStatus: async (): Promise<AIProvider[]> => {
    const res = await fetch(`${API_BASE}/ai/status`);
    if (!res.ok) throw new Error('Failed to fetch AI provider status');
    return res.json();
  },

  testAIProvider: async (name: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/ai/test/${name}`, { method: 'POST' });
    if (!res.ok) throw new Error('Provider test failed');
    return res.json();
  },

  configureAIProvider: async (name: string, payload: { api_key?: string; model_name?: string }): Promise<any> => {
    const res = await fetch(`${API_BASE}/ai/configure/${name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to configure provider');
    return res.json();
  },

  // Google Integrations
  getGoogleStatus: async (): Promise<{ configured: boolean; has_token: boolean; client_id?: string }> => {
    const res = await fetch(`${API_BASE}/google/status`);
    if (!res.ok) throw new Error('Failed to fetch Google status');
    return res.json();
  },

  getGoogleAuthUrl: async (): Promise<{ configured: boolean; auth_url?: string; instructions?: string }> => {
    const res = await fetch(`${API_BASE}/google/auth-url`);
    if (!res.ok) throw new Error('Failed to get Google auth URL');
    return res.json();
  },

  getSearchConsoleSites: async (): Promise<{ connected: boolean; sites: SearchConsoleSite[]; error?: string }> => {
    const res = await fetch(`${API_BASE}/google/search-console/sites`);
    if (!res.ok) throw new Error('Failed to query Search Console sites');
    return res.json();
  },

  getSearchAnalytics: async (siteUrl: string, days: number = 28): Promise<any> => {
    const res = await fetch(`${API_BASE}/google/search-console/performance?site_url=${encodeURIComponent(siteUrl)}&days=${days}`);
    if (!res.ok) throw new Error('Failed to fetch Search Analytics');
    return res.json();
  },

  getAnalyticsTraffic: async (propertyId: string, days: number = 30): Promise<any> => {
    const res = await fetch(`${API_BASE}/google/analytics/traffic?property_id=${encodeURIComponent(propertyId)}&days=${days}`);
    if (!res.ok) throw new Error('Failed to fetch GA4 metrics');
    return res.json();
  },

  // Git & Version Control
  getGitStatus: async (repoPath: string): Promise<GitStatus> => {
    const res = await fetch(`${API_BASE}/git/status?repo_path=${encodeURIComponent(repoPath)}`);
    if (!res.ok) throw new Error('Failed to get Git status');
    return res.json();
  },

  getGitCommits: async (repoPath: string, limit: number = 15): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/git/commits?repo_path=${encodeURIComponent(repoPath)}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to get Git commits');
    return res.json();
  },

  pushGit: async (repoPath: string, remote: string = 'origin'): Promise<any> => {
    const res = await fetch(`${API_BASE}/git/push`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath, remote_name: remote }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Git push failed');
    }
    return res.json();
  }
};
