import apiClient from './client';
import { VerifyResponse } from './types';

export const historyService = {
  /**
   * Retrieves past verification records.
   */
  getHistory: async (): Promise<VerifyResponse[]> => {
    const response = await apiClient.get('/sessions');
    return response.data.map((r: any) => ({
      ...r,
      tracking_id: r.session_id,
      top_factors: [
        ...(r.fraud?.rules_triggered || []),
        ...(r.forensics?.forgery_flags || []),
        ...(r.biometrics?.flags || [])
      ].slice(0, 3)
    }));
  },
  
  /**
   * Fetches a single forensic audit record by tracking ID.
   */
  getRecord: async (trackingId: string): Promise<VerifyResponse> => {
    const response = await apiClient.get(`/session/${trackingId}`);
    const r = response.data;
    return {
      ...r,
      tracking_id: r.session_id,
      top_factors: [
        ...(r.fraud?.rules_triggered || []),
        ...(r.forensics?.forgery_flags || []),
        ...(r.biometrics?.flags || [])
      ]
    };
  }


};
