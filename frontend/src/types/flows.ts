export interface TestFlow {
  id: string;
  name: string;
  description: string;
  claude_instruction: string;
}

export interface TestFlowDetails extends TestFlow {
  expected_changes: {
    action: string;
    seller_id?: string;
    sku?: string;
    expected_data?: any;
    search_criteria?: any;
    expected_count?: number;
    expected_count_min?: number;
    expected_seller_name?: string;
    expected_keywords?: string[];
    price_validation?: boolean;
    quantity_reduction?: number;
    expected_results?: any;
  };
}

export interface ValidationResult {
  success: boolean;
  flow_id: string;
  message: string;
  validation_results: any;
  summary?: {
    status: 'PASS' | 'FAIL';
    flow_name: string;
    session_id: string;
    timestamp?: string;
  };
}

export interface BulkValidationResult {
  summary: {
    total_flows: number;
    passed: number;
    failed: number;
    success_rate: string;
    session_id: string;
  };
  results: Record<string, ValidationResult>;
}