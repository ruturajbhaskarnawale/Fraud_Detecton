import apiClient from './client';
import { VerifyResponse, VerificationMetadata } from './types';

export const verifyService = {
  /**
   * Submits ID and Selfie for the full AI verification pipeline.
   * Injects forensic metadata for fraud detection.
   */
  verify: async (
    idFile: File, 
    selfieFile?: File, 
    metadata?: VerificationMetadata
  ): Promise<VerifyResponse> => {
    const formData = new FormData();
    formData.append('document', idFile);
    if (selfieFile) {
      formData.append('selfie', selfieFile);
    }
    
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    const response = await apiClient.post<VerifyResponse>('/verify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    // Contract Validation & Fallbacks
    const data = response.data;
    return {
      ...data,
      tracking_id: data.session_id || data.tracking_id || `ERR-${Math.random().toString(36).substr(2, 9)}`,
    };

  },

  /**
   * Polls for the result of a verification job (future-ready architecture).
   */
  pollResult: async (jobId: string, interval = 2000, timeout = 60000): Promise<VerifyResponse> => {
    const start = Date.now();
    
    return new Promise((resolve, reject) => {
      const timer = setInterval(async () => {
        if (Date.now() - start > timeout) {
          clearInterval(timer);
          reject(new Error("Verification timeout. The neural pipeline is taking longer than expected."));
          return;
        }

        try {
          // Note: Backend doesn't support /jobs/{id} yet, but this prepares the frontend
          const response = await apiClient.get<VerifyResponse>(`/verify/jobs/${jobId}`);
          if (response.data && response.data.decision) {
            clearInterval(timer);
            resolve(response.data);
          }
        } catch (err: any) {
          // If 404, we continue polling. If other error, we might stop.
          if (err.response?.status !== 404) {
            clearInterval(timer);
            reject(err);
          }
        }
      }, interval);
    });
  },

  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  }

};
