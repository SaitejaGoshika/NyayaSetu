export type RiskLevel = "high" | "medium" | "low";

export interface RiskFinding {
  id: string;
  title: string;
  riskLevel: RiskLevel;
  legalBasis: string;
  explanation: string;
  matchText: string;
  start: number;
  end: number;
  clauseIndex?: number | null;
  status?: string | null;
  reviewedBy?: string | null;
  whatToAsk?: string | null;
  needsCitationCheck?: boolean;
}

export interface AnalysisResponse {
  documentId: string;
  filename: string;
  extractedText: string;
  findings: RiskFinding[];
  rulesVersion: string;
}

export interface DocumentUploadResponse {
  documentId: string;
  filename: string;
  createdAt: string;
}

export interface DocumentRecord {
  documentId: string;
  filename: string;
  createdAt: string;
  status: string;
}

export interface SessionUser {
  uid: string;
  email: string;
  displayName: string;
}

export interface ComparisonFinding {
  id: string;
  title: string;
  riskLevel: RiskLevel;
  legalBasis: string;
  explanation: string;
  matchText: string;
  clauseIndex?: number | null;
  changeType: string;
}

export interface ComparisonClause {
  clauseIndex: number;
  primaryClause: string;
  secondaryClause: string;
  changeType: string;
}

export interface CompareDocumentsResponse {
  primaryDocumentId: string;
  secondaryDocumentId: string;
  newFindings: ComparisonFinding[];
  removedFindings: ComparisonFinding[];
  unchangedFindings: ComparisonFinding[];
  severityChanged: ComparisonFinding[];
  changedClauses: ComparisonClause[];
}
