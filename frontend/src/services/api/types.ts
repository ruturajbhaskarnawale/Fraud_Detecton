/**
 * Standardized Veridex Decision States
 */
export type Verdict = 'ACCEPT' | 'REJECT' | 'REVIEW' | 'ABSTAIN';

/**
 * Calibrated AI Signal Schema (Normalized [0, 1])
 */
/**
 * Calibrated AI Signal Schema (Normalized [0, 1])
 */
export interface KYCSignals {
  ocr_confidence: number;
  doc_confidence: number;
  doc_completeness: number;
  face_similarity: number;
  liveness_score: number;
  forensic_tamper_score: number;
  fraud_graph_score: number;
  fraud_tabular_score: number;
}

export interface VerifyResponse {
  session_id: string;
  tracking_id: string; // Alias for UI compatibility
  decision: Verdict;
  confidence_score: number;
  explanation: string;
  ocr: {
    text: string;
    confidence: number;
  };
  document: {
    document_type: string;
    fields: Record<string, any>;
    confidence: number;
  };
  biometrics: {
    face_similarity: number;
    liveness_score: number;
    status: string;
    flags: string[];
  };
  forensics: {
    tamper_score: number;
    is_altered: boolean;
    forgery_flags: string[];
  };
  metadata: {
    ip_risk: number;
    device_risk: number;
    geo_anomaly: boolean;
    flags: string[];
  };
  fraud: {
    fraud_score: number;
    is_fraudulent: boolean;
    rules_triggered: string[];
  };
  risk: {
    score: number;
    level: string;
    breakdown: Record<string, number>;
  };
  timestamp: string;
  image_paths: {
    id_card: string;
    selfie?: string;
  };
  latency_ms?: number;
}


export interface VerificationMetadata {
  device_id: string;
  session_id: string;
  user_agent: string;
  timezone: string;
  resolution: string;
  language: string;
}
