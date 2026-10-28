export interface Website {
  id: string;
  name: string;
  canonical_url: string;
  local_repo_path?: string;
  git_remote_url?: string;
  gsc_site_url?: string;
  ga4_property_id?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface SEOIssue {
  id: string;
  website_id: string;
  audit_id: string;
  category: 'technical' | 'meta' | 'content' | 'links' | 'performance' | 'indexing' | 'security';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  url_or_file: string;
  evidence?: string;
  root_cause_hypothesis?: string;
  recommended_fix?: string;
  confidence: number;
  status: 'open' | 'in_plan' | 'resolved' | 'ignored';
  created_at: string;
}

export interface Audit {
  id: string;
  website_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  health_score: number;
  pages_crawled: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  medium_issues: number;
  low_issues: number;
  summary?: string;
  created_at: string;
  completed_at?: string;
  issues?: SEOIssue[];
}

export interface FileModification {
  file_path: string;
  action: 'modify' | 'create' | 'delete';
  original_snippet?: string;
  new_snippet?: string;
  diff: string;
  reason: string;
  target_issues: string[];
}

export interface ChangePlan {
  id: string;
  website_id: string;
  audit_id?: string;
  title: string;
  description?: string;
  status: 'pending_approval' | 'approved' | 'applied' | 'rejected' | 'failed' | 'rolled_back';
  changes: FileModification[];
  risk_assessment?: 'low' | 'medium' | 'high';
  tests_to_run: string[];
  execution_log?: string;
  git_commit_hash?: string;
  git_commit_message?: string;
  created_at: string;
  approved_at?: string;
  applied_at?: string;
}

export interface AIProvider {
  provider_name: string;
  model_name: string;
  status: 'healthy' | 'degraded' | 'quota_exceeded' | 'error' | 'unreachable' | 'unknown';
  message: string;
  latency_ms: number;
  has_api_key: boolean;
}

export interface SearchConsoleSite {
  siteUrl: string;
  permissionLevel: string;
}

export interface SearchAnalyticsRow {
  query: string;
  page: string;
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

export interface GitStatus {
  is_repo: boolean;
  branch?: string;
  remotes: { name: string; url: string }[];
  has_uncommitted_changes: boolean;
  untracked_files: string[];
  modified_files: string[];
}

