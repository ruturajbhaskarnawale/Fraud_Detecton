import { verifyService } from './verify';
import { historyService } from './history';

export * from './types';

export const verificationService = {
  ...verifyService,
  ...historyService,
};
