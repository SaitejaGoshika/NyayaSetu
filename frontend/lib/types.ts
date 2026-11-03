export type RiskLevel = "high" | "medium" | "low";

export interface RiskFinding {
  id: string;
  title: string;
  riskLevel: RiskLevel;
  legalBasis: string;
  explanation: string;
  matchText: string;
}

export interface AnalysisResponse {
  documentId: string;
  filename: string;
  extractedText: string;
  findings: RiskFinding[];
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

export interface CasePredictResponse {
  classes: string[];
  probabilities: number[];
}

export interface CasePredictStatus {
  available: boolean;
  message: string;
}

export interface SessionUser {
  uid: string;
  email: string;
  displayName: string;
}
