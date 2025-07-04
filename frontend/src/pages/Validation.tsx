import { useState, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import { flowService } from '../services/flowService';
import { TestFlow, ValidationResult, BulkValidationResult } from '../types/flows';

const Validation = () => {
  const { currentSession } = useSession();
  const [flows, setFlows] = useState<TestFlow[]>([]);
  const [loading, setLoading] = useState(false);
  const [validationResults, setValidationResults] = useState<Record<string, ValidationResult>>({});
  const [bulkValidationResult, setBulkValidationResult] = useState<BulkValidationResult | null>(null);
  const [selectedFlow, setSelectedFlow] = useState<string>('');
  const [validatingFlow, setValidatingFlow] = useState<string | null>(null);
  const [bulkValidating, setBulkValidating] = useState(false);

  useEffect(() => {
    loadFlows();
  }, []);

  const loadFlows = async () => {
    try {
      const flowsData = await flowService.getTestFlows();
      setFlows(flowsData);
    } catch (err) {
      console.error('Failed to load flows:', err);
    }
  };

  const validateSingleFlow = async (flowId: string) => {
    if (!currentSession) {
      alert('Please create or select a session first');
      return;
    }

    try {
      setValidatingFlow(flowId);
      const result = await flowService.validateFlow(flowId);
      setValidationResults(prev => ({
        ...prev,
        [flowId]: result
      }));
    } catch (err: any) {
      console.error('Validation failed:', err);
      setValidationResults(prev => ({
        ...prev,
        [flowId]: {
          success: false,
          flow_id: flowId,
          message: err.message || 'Validation failed',
          validation_results: null
        }
      }));
    } finally {
      setValidatingFlow(null);
    }
  };

  const validateAllFlows = async () => {
    if (!currentSession) {
      alert('Please create or select a session first');
      return;
    }

    try {
      setBulkValidating(true);
      const result = await flowService.validateAllFlows();
      setBulkValidationResult(result);
      setValidationResults(result?.results || {});
    } catch (err: any) {
      console.error('Bulk validation failed:', err);
      alert('Bulk validation failed: ' + (err.message || 'Unknown error'));
      // Reset validation results on error
      setValidationResults({});
      setBulkValidationResult(null);
    } finally {
      setBulkValidating(false);
    }
  };

  const getStatusColor = (success: boolean): string => {
    return success ? 'success' : 'error';
  };

  const getStatusIcon = (success: boolean): string => {
    return success ? '✅' : '❌';
  };

  const formatValidationDetails = (result: ValidationResult) => {
    if (!result.validation_results) return null;

    return (
      <div className="mt-4 space-y-2">
        <h4 className="font-medium text-gray-900">Validation Details:</h4>
        <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
          {JSON.stringify(result.validation_results, null, 2)}
        </pre>
      </div>
    );
  };

  if (!currentSession) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Validation</h1>
        <div className="card bg-warning-50 border-warning-200">
          <div className="text-center py-8">
            <div className="text-warning-500 text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-warning-800 mb-2">No Active Session</h3>
            <p className="text-warning-600 mb-4">
              You need an active session to validate test flows. Please create or select a session from the Dashboard.
            </p>
            <a href="/" className="btn-primary">
              Go to Dashboard
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Validation</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Session:</span>
          <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm font-mono">
            {currentSession}
          </span>
        </div>
      </div>

      {/* Bulk Validation */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Bulk Validation</h2>
          <button
            onClick={validateAllFlows}
            disabled={bulkValidating}
            className="btn-primary"
          >
            {bulkValidating ? 'Validating...' : 'Validate All Flows'}
          </button>
        </div>

        {bulkValidationResult && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-primary-50 rounded-lg">
                <div className="text-2xl font-bold text-primary-900">
                  {bulkValidationResult.summary.total_flows}
                </div>
                <div className="text-sm text-primary-600">Total Flows</div>
              </div>
              <div className="text-center p-3 bg-success-50 rounded-lg">
                <div className="text-2xl font-bold text-success-900">
                  {bulkValidationResult.summary.passed}
                </div>
                <div className="text-sm text-success-600">Passed</div>
              </div>
              <div className="text-center p-3 bg-error-50 rounded-lg">
                <div className="text-2xl font-bold text-error-900">
                  {bulkValidationResult.summary.failed}
                </div>
                <div className="text-sm text-error-600">Failed</div>
              </div>
              <div className="text-center p-3 bg-warning-50 rounded-lg">
                <div className="text-2xl font-bold text-warning-900">
                  {bulkValidationResult.summary.success_rate}
                </div>
                <div className="text-sm text-warning-600">Success Rate</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Individual Flow Validation */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Individual Flow Validation</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select a flow to validate
            </label>
            <select
              value={selectedFlow}
              onChange={(e) => setSelectedFlow(e.target.value)}
              className="input"
            >
              <option value="">Choose a test flow...</option>
              {flows.map((flow) => (
                <option key={flow.id} value={flow.id}>
                  {flow.id} - {flow.name}
                </option>
              ))}
            </select>
          </div>

          {selectedFlow && (
            <div className="flex space-x-2">
              <button
                onClick={() => validateSingleFlow(selectedFlow)}
                disabled={validatingFlow === selectedFlow}
                className="btn-primary"
              >
                {validatingFlow === selectedFlow ? 'Validating...' : 'Validate Flow'}
              </button>
              <a
                href={`/flows`}
                className="btn-secondary"
              >
                View Flow Details
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Validation Results */}
      {validationResults && Object.keys(validationResults).length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Validation Results</h2>

          <div className="space-y-4">
            {Object.entries(validationResults).map(([flowId, result]) => {
              const flow = flows.find(f => f.id === flowId);
              const statusColor = getStatusColor(result.success);

              return (
                <div
                  key={flowId}
                  className={`border rounded-lg p-4 ${result.success
                    ? 'border-success-200 bg-success-50'
                    : 'border-error-200 bg-error-50'
                    }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-lg">{getStatusIcon(result.success)}</span>
                        <h3 className="font-semibold text-gray-900">
                          {flow?.name || flowId}
                        </h3>
                        <span className={`badge badge-${statusColor}`}>
                          {result.success ? 'PASS' : 'FAIL'}
                        </span>
                      </div>

                      <p className={`text-sm mb-2 ${result.success ? 'text-success-700' : 'text-error-700'
                        }`}>
                        {result.message}
                      </p>

                      {result.summary && (
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>Flow ID: {result.summary.flow_name}</div>
                          <div>Session: {result.summary.session_id}</div>
                        </div>
                      )}

                      {formatValidationDetails(result)}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="card bg-blue-50 border-blue-200">
        <h2 className="text-lg font-semibold text-blue-900 mb-3">How to Use Validation</h2>
        <div className="text-sm text-blue-800 space-y-2">
          <p><strong>1.</strong> Choose a test flow from the dropdown or run bulk validation</p>
          <p><strong>2.</strong> Ask Claude to perform the action described in the flow's instruction</p>
          <p><strong>3.</strong> Click "Validate Flow" to check if Claude performed the action correctly</p>
          <p><strong>4.</strong> Review the validation results to see if the test passed or failed</p>
          <p><strong>5.</strong> Use the Tools page to reset the database between tests</p>
        </div>
      </div>
    </div>
  );
};

export default Validation;