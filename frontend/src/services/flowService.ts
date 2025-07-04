import { apiService } from './api';
import { TestFlow, TestFlowDetails, ValidationResult, BulkValidationResult } from '../types/flows';

export class FlowService {
  // Get all test flows
  async getTestFlows(): Promise<TestFlow[]> {
    return apiService.get<TestFlow[]>('/test/flows');
  }

  // Get specific test flow details
  async getTestFlowDetails(flowId: string): Promise<TestFlowDetails> {
    return apiService.get<TestFlowDetails>(`/test/flows/${flowId}`);
  }

  // Validate a specific test flow
  async validateFlow(flowId: string): Promise<ValidationResult> {
    return apiService.get<ValidationResult>(`/test/validate/${flowId}`);
  }

  // Validate all test flows
  async validateAllFlows(): Promise<BulkValidationResult> {
    return apiService.get<BulkValidationResult>('/test/validate/all');
  }

  // Get testing help information
  async getTestingHelp(): Promise<any> {
    return apiService.get('/test/help');
  }
}

export const flowService = new FlowService();