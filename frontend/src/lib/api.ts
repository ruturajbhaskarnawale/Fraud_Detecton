import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export type Verdict = 'ACCEPT' | 'REJECT' | 'REVIEW' | 'ABSTAIN';

export interface VerifyResponse {
  session_id: string;
  tracking_id: string; // Add tracking_id which seems to be used
  decision: Verdict;
  confidence_score: number;
  explanation: string;
  ocr?: {
    text: string;
    confidence: number;
    engine?: string;
  };
  document?: {
    document_type: string;
    fields: Record<string, any>;
    confidence: number;
  };
  biometrics?: {
    face_similarity: number;
    liveness_score: number;
    status: string;
    flags: string[];
  };
  forensics?: {
    tamper_score: number;
    is_altered: boolean;
    forgery_flags: string[];
  };
  metadata?: {
    ip_risk: number;
    device_risk: number;
    geo_anomaly: boolean;
    flags: string[];
  };
  fraud?: {
    fraud_score: number;
    is_fraudulent: boolean;
    rules_triggered: string[];
  };
  risk: {
    score: number;
    level: string;
    breakdown: Record<string, number>;
  };
  image_paths?: Record<string, string>;
  timestamp: string;
}

export const verifyIdentity = async (document: File, selfie: File | null): Promise<VerifyResponse> => {
  const formData = new FormData();
  formData.append('document', document);
  if (selfie) formData.append('selfie', selfie);

  // Add browser metadata
  const metadata = {
    ip_address: '127.0.0.1', // Real apps would get this from a service or server-side
    user_agent: navigator.userAgent,
    device_id: 'browser-client-' + Math.random().toString(36).substring(7),
    timestamp: Date.now() / 1000
  };
  formData.append('metadata', JSON.stringify(metadata));

  try {
    const response = await axios.post(`${API_BASE_URL}/verify`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Verification failed:', error);
    throw error;
  }
};

