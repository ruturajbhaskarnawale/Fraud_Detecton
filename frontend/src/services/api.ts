import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export interface VerificationResult {
  id_validation: {
    type: string;
    extracted_fields: {
      id_number?: string;
      name?: string;
      dob?: string;
    };
  };
  face_validation: {
    similarity: number;
    decision: string;
  };
  fraud_validation: {
    confidence: number;
    status: string;
    signals: string[];
  };
  final_decision: {
    risk_score: number;
    decision: string;
    reasons: string[];
  };
}

export interface VerifyResponse {
  status: string;
  tracking_id: string;
  latency_ms: number;
  image_paths: {
    id_card: string;
    selfie?: string;
  };
  results: VerificationResult;
}

export const verificationService = {
  verify: async (idFile: File, selfieFile?: File): Promise<VerifyResponse> => {
    const formData = new FormData();
    formData.append('id_card', idFile);
    if (selfieFile) {
      formData.append('selfie', selfieFile);
    }
    
    const response = await api.post<VerifyResponse>('/verify', formData);
    return response.data;
  },
  
  getHistory: async (): Promise<any[]> => {
    const response = await api.get('/records');
    return response.data;
  },
  
  getRecord: async (trackingId: string): Promise<any> => {
    const response = await api.get(`/records/${trackingId}`);
    return response.data;
  }
};

export default api;
