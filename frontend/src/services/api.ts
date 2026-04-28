import { verifyService } from './api/verify';
import { historyService } from './api/history';

/**
 * Consolidated Veridex API Service
 * Migrating towards modular structure in @/services/api/
 */
export const verificationService = {
  ...verifyService,
  ...historyService,
};

export * from './api/types';
export { default as apiClient } from './api/client';
