import { useState, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import { flowService } from '../services/flowService';
import { TestFlow, ValidationResult } from '../types/flows';

const Flows = () => {
  const { currentSession } = useSession();
  const [flows, setFlows] = useState<TestFlow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedFlow, setExpandedFlow] = useState<string | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [validatingFlows, setValidatingFlows] = useState<Set<string>>(new Set());
  const [validationResults, setValidationResults] = useState<Record<string, ValidationResult>>({});

  useEffect(() => {
    loadFlows();
  }, []);

  const loadFlows = async () => {
    try {
      setLoading(true);
      const flowsData = await flowService.getTestFlows();
      setFlows(flowsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load test flows');
    } finally {
      setLoading(false);
    }
  };

  const getFlowCategory = (flowId: string): string => {
    if (flowId.includes('create')) return 'create';
    if (flowId.includes('update')) return 'update';
    if (flowId.includes('delete') || flowId.includes('deactivate')) return 'delete';
    if (flowId.includes('search')) return 'search';
    if (flowId.includes('bulk')) return 'bulk';
    if (flowId.includes('analysis') || flowId.includes('expensive')) return 'analysis';
    return 'other';
  };

  const categories = [
    { id: 'all', name: 'All Flows', icon: '📋' },
    { id: 'create', name: 'Create', icon: '➕' },
    { id: 'update', name: 'Update', icon: '✏️' },
    { id: 'delete', name: 'Delete', icon: '🗑️' },
    { id: 'search', name: 'Search', icon: '🔍' },
    { id: 'bulk', name: 'Bulk Operations', icon: '📦' },
    { id: 'analysis', name: 'Analysis', icon: '📊' },
  ];

  const filteredFlows = flows.filter(flow => {
    const matchesCategory = selectedCategory === 'all' || getFlowCategory(flow.id) === selectedCategory;
    const matchesSearch = flow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      flow.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      flow.claude_instruction.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const copyToClipboard = async (text: string, identifier?: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(identifier || 'text');
      // Clear the copied indication after 2 seconds
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const validateFlow = async (flowId: string) => {
    if (!currentSession) {
      alert('Please create or select a session first');
      return;
    }

    try {
      setValidatingFlows(prev => new Set(prev).add(flowId));
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
      setValidatingFlows(prev => {
        const newSet = new Set(prev);
        newSet.delete(flowId);
        return newSet;
      });
    }
  };

  const getStatusColor = (success: boolean): string => {
    return success ? 'success' : 'error';
  };

  const getStatusIcon = (success: boolean): string => {
    return success ? '✅' : '❌';
  };

  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'create': return 'bg-success-100 text-success-800 dark:bg-green-600 dark:text-white';
      case 'update': return 'bg-primary-100 text-primary-800 dark:bg-blue-600 dark:text-white';
      case 'delete': return 'bg-error-100 text-error-800 dark:bg-red-600 dark:text-white';
      case 'search': return 'bg-warning-100 text-warning-800 dark:bg-yellow-600 dark:text-black';
      case 'bulk': return 'bg-purple-100 text-purple-800 dark:bg-purple-600 dark:text-white';
      case 'analysis': return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-600 dark:text-white';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-white';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading test flows...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-error-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Failed to Load Test Flows</h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">{error}</p>
          <button onClick={loadFlows} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Test Flows</h1>
        <div className="text-sm text-gray-600 dark:text-gray-300">
          {filteredFlows.length} of {flows.length} flows
        </div>
      </div>

      {!currentSession && (
        <div className="card bg-warning-50 border-warning-200 dark:bg-gray-700 dark:border-gray-500">
          <div className="flex items-center space-x-3">
            <div className="text-warning-500 text-xl">⚠️</div>
            <div>
              <p className="font-medium text-warning-800 dark:text-gray-200">No Active Session</p>
              <p className="text-sm text-warning-600 dark:text-gray-300">
                Create a session from the Dashboard to validate test flows
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search flows
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name, description, or instruction..."
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Filter by category
            </label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${selectedCategory === category.id
                    ? 'bg-primary-600 text-white dark:bg-gray-100 dark:text-gray-900'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                    }`}
                >
                  <span className="mr-1">{category.icon}</span>
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Flow Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredFlows.map((flow) => {
          const category = getFlowCategory(flow.id);
          const isExpanded = expandedFlow === flow.id;
          const isValidating = validatingFlows.has(flow.id);
          const validationResult = validationResults[flow.id];

          return (
            <div key={flow.id} className="card hover:shadow-md transition-shadow">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{flow.name}</h3>
                      <span className={`badge ${getCategoryColor(category)}`}>
                        {category}
                      </span>
                      {validationResult && (
                        <span className={`badge badge-${getStatusColor(validationResult.success)}`}>
                          {validationResult.success ? 'PASS' : 'FAIL'}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded dark:bg-gray-600 dark:text-gray-200">
                        {flow.id}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 text-sm">{flow.description}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="mb-2">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Claude Instruction
                      </label>
                    </div>
                    <div className={`bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-sm font-mono dark:text-gray-200 ${isExpanded ? '' : 'max-h-20 overflow-hidden relative'
                      }`}>
                      {flow.claude_instruction}
                      {!isExpanded && flow.claude_instruction.length > 100 && (
                        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-gray-50 to-transparent dark:from-gray-700"></div>
                      )}
                    </div>
                    {flow.claude_instruction.length > 100 && (
                      <button
                        onClick={() => setExpandedFlow(isExpanded ? null : flow.id)}
                        className="text-xs text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 mt-1"
                      >
                        {isExpanded ? 'Show less' : 'Show more'}
                      </button>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(flow.claude_instruction, `button-${flow.id}`)}
                      className="btn-secondary flex-1 text-sm"
                    >
                      {copiedText === `button-${flow.id}` ? '✅ Copied!' : '📋 Copy Instruction'}
                    </button>
                    {currentSession && (
                      <button
                        onClick={() => validateFlow(flow.id)}
                        disabled={isValidating}
                        className="btn-primary flex-1 text-sm"
                      >
                        {isValidating ? '🔄 Validating...' : '✅ Validate'}
                      </button>
                    )}
                  </div>

                  {/* Validation Results */}
                  {validationResult && (
                    <div className={`mt-4 p-3 rounded-lg border ${validationResult.success
                      ? 'border-success-200 bg-success-50 dark:border-green-400 dark:bg-green-900/20'
                      : 'border-error-200 bg-error-50 dark:border-red-400 dark:bg-red-900/20'
                      }`}>
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-lg">{getStatusIcon(validationResult.success)}</span>
                        <span className={`font-medium ${validationResult.success ? 'text-success-800 dark:text-green-300' : 'text-error-800 dark:text-red-300'
                          }`}>
                          {validationResult.success ? 'Validation Passed' : 'Validation Failed'}
                        </span>
                      </div>
                      <p className={`text-sm ${validationResult.success ? 'text-success-700 dark:text-green-300' : 'text-error-700 dark:text-red-300'
                        }`}>
                        {validationResult.message}
                      </p>
                      {validationResult.validation_results && (
                        <details className="mt-2">
                          <summary className="text-xs cursor-pointer text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200">
                            View Details
                          </summary>
                          <pre className="mt-2 text-xs bg-white dark:bg-gray-800 dark:text-gray-200 p-2 rounded border dark:border-gray-600 overflow-x-auto">
                            {JSON.stringify(validationResult.validation_results, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredFlows.length === 0 && (
        <div className="card text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No flows found</h3>
          <p className="text-gray-600 dark:text-gray-300">
            Try adjusting your search terms or category filter
          </p>
        </div>
      )}
    </div>
  );
};

export default Flows;